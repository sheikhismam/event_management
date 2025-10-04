from django.urls import path
from events.views import *

urlpatterns = [
    path('', view_events, name="view-events"),
    path('event-details/<int:id>/', details, name="event-details"),
    path('create-event/', create_event, name="create-event"),
    path('update-event/<int:id>/', update_event, name="update-event"),
    path('delete-event/<int:id>/', delete_event, name="delete-event"),
    path('update-participant/<int:id>/', update_participant, name="update-participant"),
    path('update-category/<int:id>/', update_category, name="update-category"),
    path('organizer-dashboard/', organizer_dashboard, name="organizer-dashboard"),
    path('search-events/', search_events, name="search-events")
]
