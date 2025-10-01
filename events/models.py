from django.db import models
from datetime import time

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=100)
    description  = models.TextField(max_length=250)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=False, blank=False, default=time(9,0))
    location =  models.CharField(max_length=255)
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="events"
    )

    def __str__(self):
        return self.name
    
class Participant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    event = models.ManyToManyField(
        Event,
        related_name="participants"
    )
    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    description  = models.TextField(max_length=250)

    def __str__(self):
        return self.name