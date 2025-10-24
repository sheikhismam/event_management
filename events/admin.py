from django.contrib import admin
from events.models import Event, Participant, Category
# Register your models here.
admin.site.register(Event)
admin.site.register(Participant)
admin.site.register(Category)