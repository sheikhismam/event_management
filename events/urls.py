from django.urls import path
from events.views import details, create_event, delete_event, update_event, update_participant, update_category, organizer_dashboard, search_events, register, activate_user, log_in, log_out, home
from core.views import no_permission

urlpatterns = [
    path('home/', home, name="home"),
    path('event-details/<int:id>/', details, name="event-details"),
    path('create-event/', create_event, name="create-event"),
    path('update-event/<int:id>/', update_event, name="update-event"),
    path('delete-event/<int:id>/', delete_event, name="delete-event"),
    path('update-participant/<int:id>/', update_participant, name="update-participant"),
    path('update-category/<int:id>/', update_category, name="update-category"),
    path('organizer-dashboard/', organizer_dashboard, name="organizer-dashboard"),
    path('search-events/', search_events, name="search-events"),
    path('register/', register, name="register"),
    path('user-activate/<int:user_id>/<str:token>/', activate_user, name='activate-user'),
    path('log-in/', log_in, name='log-in'),
    path('log-out/', log_out, name="log-out"),
    path('no-permission/', no_permission, name="no-permission")
]
