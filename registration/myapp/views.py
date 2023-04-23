from django.shortcuts import render,HttpResponse,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.urls import reverse
from .models import CallAnalytics
from .models import Schedule
from .models import Contacts
from .models import Data
import pandas as pd
import requests
import datetime
import hashlib
import random
import time
import re

@login_required(login_url='login')
def BasePage(request):
    return render (request,'home.html')

def SignupPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = User.objects.create_user(username=username, email=email, password=password_hash)
        data = Data(username=username, email=email, phone=phone, password=password_hash)
        data.save()

        user = authenticate(username=username, password=password_hash)
        login(request, user)

        verification_link = request.build_absolute_uri(reverse('verify_email', args=[user.pk]))
        subject = 'Verify your email address'
        html_message = render_to_string('verification_email.html', {'username': username, 'verification_link': verification_link})
        plain_message = strip_tags(html_message)
        send_mail(subject, plain_message, 'autodialer23@gmail.com', [email], html_message=html_message, fail_silently=False)

    return render(request, 'signup.html')


User = get_user_model()

def verify_email(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.save()
    return render(request, 'home.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        password_hashed = hashlib.sha256(password.encode()).hexdigest()

        user=authenticate(request,username=username,password=password_hashed)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            error_message = 'Username or password is incorrect!'
            context = {
                'error_message': error_message,
                'username': username,
            }
            return render(request, 'login.html', context=context)
    return render(request, 'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')

def BasePage(request):
    return render(request, 'base.html')

def HomePage(request):
    return render(request, 'home.html')

def ContactsPage(request):
    return render(request, 'contacts.html')

def SchedulePage(request):
    return render(request, 'schedule.html')

def ScenarioPage(request):
    return render(request, 'scenario.html')

def ConnectionPage(request):
    total_calls = 0
    answered_calls = 0
    didnt_answer_calls = 0
    closed_calls = 0
    
    return render(request, 'connection.html', {
        'total_calls': total_calls,
        'answered_calls': answered_calls,
        'didnt_answer_calls': didnt_answer_calls,
        'closed_calls': closed_calls
    })

def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            df = pd.read_excel(file)

            data = Data.objects.get(username=request.user.username)
            
            for index, row in df.iterrows():
                contacts, created = Contacts.objects.get_or_create(
                    data=data,
                    name=row['Name'],
                    phones=row['Phones'],
                    date=row['Date'],
                    time=row['Time'],
                    data_id=data.id
                )
                contacts.save()

                status_options = ["Answered", "Didn't Answer"]
                weights = [3, 1]
                existing_call_analytics = CallAnalytics.objects.filter(
                    data=data,
                    name=row['Name'],
                    phones=row['Phones'],
                    date=row['Date'],
                    time=row['Time']
                ).first()

                if existing_call_analytics:
                    existing_call_analytics.status = random.choices(status_options, weights=weights)[0]
                    existing_call_analytics.save()
                else:
                    call_analytics = CallAnalytics.objects.create(
                        data=data,
                        name=row['Name'],
                        phones=row['Phones'],
                        date=row['Date'],
                        time=row['Time'],
                        status=random.choices(status_options, weights=weights)[0],
                        data_id=data.id
                    )

            contacts = Contacts.objects.filter(data__username=request.user.username)
            call_analytics = CallAnalytics.objects.filter(data__username=request.user.username)

            return render(request, 'contacts.html', {"contacts": contacts, "call_analytics": call_analytics})
    return render(request, 'contacts.html')

def save_schedule(request):
    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        max_number = request.POST.get('max_number')
        max_retry = request.POST.get('max_retry')
        time_between = request.POST.get('time_between')
        data = Data.objects.get(username=request.user.username)
        data_id=data.id

        schedule = Schedule(start_time=start_time, end_time=end_time, number_calls=max_number,
                            retry_count=max_retry, repeated_time=time_between, data_id=data_id)
        schedule.save()
        return render(request, 'schedule.html')

def create_call(request):
    url = request.POST.get('pbxinput')
    #caller = '711007'
    password = '103103103'
    ext_id = 'Chrome_extension 11'
    user = 103
    app = 'Chrome extension'

    data = Data.objects.get(username=request.user.username)
    caller = data.phone

    phone_numbers = Contacts.objects.filter(data__username=request.user.username).values_list('phones', flat=True)
    call_ids = [random.randint(1000000000000000000, 9999999999999999999) for _ in range(len(phone_numbers))]
    responses = []

    schedule = Schedule.objects.filter(data__username=request.user.username).order_by('-id').first()
    start_time = datetime.datetime.combine(datetime.date.today(), schedule.start_time)
    end_time = datetime.datetime.combine(datetime.date.today(), schedule.end_time)
    now = datetime.datetime.now()

    if start_time > now:
        time.sleep((start_time - now).total_seconds())

    if end_time < datetime.datetime.now():
        total_calls = 0
        answered_calls = 0
        didnt_answer_calls = 0
        closed_calls = 0
    
        return render(request, 'connection.html', {
        'total_calls': total_calls,
        'answered_calls': answered_calls,
        'didnt_answer_calls': didnt_answer_calls,
        'closed_calls': closed_calls
        })

    for i in range(schedule.number_calls):
        if end_time < datetime.datetime.now():
            responses.append("It's End Time. Stopping further calls.")
            break
        
        data = {
            'callid': call_ids[i],
            'caller': caller,
            'pass': password,
            'cmd': 0,
            'id': ext_id,
            'dest': phone_numbers[i],
            'user': user,
            'app': app
        }
        response = requests.post(url, data=data, verify=False)
        response_text = response.text.strip()
        state_pattern = re.compile(r'State=(\d+)')
        state_match = state_pattern.search(response_text)
        if state_match:
            state_code = int(state_match.group(1))
            if state_code == 5:
                responses.append("Extension Authorization Failed.")
            elif state_code == 18:
                responses.append("iQall Toggling License Failure.")
            elif state_code == 4:
                responses.append("Invalid Parameter.")
            elif state_code == 8:
                responses.append("Empty Destination Error!")
            elif state_code == 7:
                responses.append("Empty Caller Error!")
            elif state_code == 10:
                responses.append("Extension Access Temporarily Blocked!")
            elif state_code == 20:
                responses.append("Success! Response Code - " + str(state_code))
        else:
            responses.append("Error! Bad Response. Response Code - " + response_text)
        
        if i != len(phone_numbers)-1:
            time.sleep(3)

    if schedule.retry_count > 0:
        for i in range(schedule.retry_count):
            time.sleep(schedule.repeated_time * 60)
            retry_phones = CallAnalytics.objects.filter(status="Didn't Answer", data__username=request.user.username).values_list('phones', flat=True)
            phone_numbers = list(retry_phones)
            call_ids = [random.randint(1000000000000000000, 9999999999999999999) for _ in range(len(phone_numbers))]
            retry_responses = []

            for j in range(len(phone_numbers)):
                if end_time < datetime.datetime.now():
                    retry_responses.append("It's End Time. Stopping further calls.")
                    break

                data = {
                    'callid': call_ids[j],
                    'caller': caller,
                    'pass': password,
                    'cmd': 0,
                    'id': ext_id,
                    'dest': phone_numbers[j],
                    'user': user,
                    'app': app
                }
                response = requests.post(url, data=data, verify=False)
                response_text = response.text.strip()
                state_pattern = re.compile(r'State=(\d+)')
                state_match = state_pattern.search(response_text)
                if state_match:
                    state_code = int(state_match.group(1))
                    if state_code == 5:
                        retry_responses.append("Extension Authorization Failed.")
                    elif state_code == 18:
                        retry_responses.append("iQall Toggling License Failure.")
                    elif state_code == 4:
                        retry_responses.append("Invalid Parameter.")
                    elif state_code == 8:
                        retry_responses.append("Empty Destination Error!")
                    elif state_code == 7:
                        retry_responses.append("Empty Caller Error!")
                    elif state_code == 10:
                        retry_responses.append("Extension Access Temporarily Blocked!")
                    elif state_code == 20:
                        retry_responses.append("Success! Response Code - " + str(state_code))
                else:
                    retry_responses.append("Error! Bad Response. Response Code - " + response_text)
        
                if j != len(phone_numbers)-1:
                    time.sleep(3)

            responses += retry_responses

    total_calls = schedule.number_calls
    call_analytics = CallAnalytics.objects.filter(data__username=request.user.username)
    answered_calls = call_analytics.filter(status="Answered").count()
    didnt_answer_calls = call_analytics.filter(status="Didn't Answer").count()
    closed_calls = total_calls
    
    return render(request, 'connection.html', {
        'total_calls': total_calls,
        'answered_calls': answered_calls,
        'didnt_answer_calls': didnt_answer_calls,
        'closed_calls': closed_calls,
        'call_analytics': call_analytics,
        'responses': '<br>'.join(responses)
    })