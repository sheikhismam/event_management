from django.db import models
from datetime import time
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=100)
    description  = models.TextField(max_length=250)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=False, blank=False, default=time(9,0))
    location =  models.CharField(max_length=255)
    asset = models.ImageField(upload_to='events_asset', blank=True, null=True, default='events_asset/download.jpeg')
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='rsvp_events'
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="events"
    )

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    description  = models.TextField(max_length=250)

    def __str__(self):
        return self.name

class RSVP(models.Model):
    RESPONSE_CHOICES = [
        ('yes', 'Attending'),
        ('no', 'Not Attending'),
        ('maybe', 'Maybe')
    ]
    event = models.ForeignKey(Event, related_name='events', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='users', on_delete=models.CASCADE)
    response = models.CharField(max_length=15, choices=RESPONSE_CHOICES, default="yes")
    is_active = models.BooleanField(default=False)
    unique_together = ('user', 'event')

    def __str__(self):
        return f'{self.user.username} - {self.event.name} - {self.response}'
    
"""
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE, primary_key=True)
    bio = models.CharField(blank=True)
    profile_image = models.ImageField(upload_to='profile_asset',default='events_asset/health.jpeg', blank=True)


    def __str__(self):
        return f'{self.user.username}'
"""

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_asset', default='events_asset/health.jpeg', blank=True)
    phone_number = models.TextField(blank=True)

    def __str__(self):
        return self.username