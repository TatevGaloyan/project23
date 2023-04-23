"""registration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.LoginPage,name='login'),
    path('signup/',views.SignupPage,name='signup'),
    path('verify_email/<int:pk>/', views.verify_email, name='verify_email'),
    path('base/',views.BasePage,name='base'),
    path('home/',views.HomePage,name='home'),
    path('logout/',views.LogoutPage,name='logout'),
    path('contacts/', views.ContactsPage, name='contacts'),
    path('schedule/', views.SchedulePage, name='schedule'),
    path('scenario/', views.ScenarioPage, name='scenario'),
    path('connection/', views.ConnectionPage, name='connection'),
    path('create_call/', views.create_call, name='create_call'),
    path('upload/', views.upload_file, name='upload_file'),
    path('save_schedule/', views.save_schedule, name='save_schedule'),
]