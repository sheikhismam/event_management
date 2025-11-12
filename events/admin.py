from django.contrib import admin
from events.models import Event, Category, RSVP, CustomUser
# Register your models here.
admin.site.register(Event)
admin.site.register(Category)
admin.site.register(RSVP)
admin.site.register(CustomUser)