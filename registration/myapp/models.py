from django.db import models

class Data(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

class Contacts(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255)
    phones = models.CharField(max_length=20)
    date = models.DateTimeField()
    time = models.TimeField(auto_now=False, auto_now_add=False)

class Schedule(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE, related_name='schedule')
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    end_time = models.TimeField(auto_now=False, auto_now_add=False)
    number_calls = models.IntegerField()
    retry_count = models.IntegerField()
    repeated_time = models.IntegerField()

class CallAnalytics(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE, related_name='call_analytics')
    name = models.CharField(max_length=255)
    phones = models.CharField(max_length=20)
    date = models.DateTimeField()
    time = models.TimeField(auto_now=False, auto_now_add=False)
    status = models.CharField(max_length=255)