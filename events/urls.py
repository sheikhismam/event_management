from django.urls import path
from events.views import *
from core.views import no_permission

urlpatterns = [
    path('', home, name="home"),
    path('event-details/<int:id>/', details, name="event-details"),
    path('create-event/', create_event, name="create-event"),
    path('update-event/<int:id>/', update_event, name="update-event"),
    path('delete-event/<int:id>/', delete_event, name="delete-event"),
    # path('update-participant/<int:id>/', update_participant, name="update-participant"),
    path('update-category/<int:event_id>/', update_category, name="update-category"),
    path('organizer-dashboard/', organizer_dashboard, name="organizer-dashboard"),
    path('search-events/', search_events, name="search-events"),
    path('register/', register, name="register"),
    path('user-activate/<int:user_id>/<str:token>/', activate_user, name='activate-user'),
    path('log-in/', log_in, name='log-in'),
    path('log-out/', log_out, name="log-out"),
    path('no-permission/', no_permission, name="no-permission"),
    path('admin-dashboard/', admin_dashboard, name="admin-dashboard"),
    path('<int:user_id>/assign-role/', Assign_role, name='assign-role'),
    path('create-group/', create_group, name="create-group"),
    path('create-category/', create_category, name="create-category"),
    path('view-category/', view_category, name="view-category"),
    path('delete-category/<int:category_id>', delete_category, name="delete-category"),
    path('view-groups/', view_groups, name="view-groups"),
    path('admin-dashboard/delete-group/<int:group_id>/', delete_group, name="delete-group"),
    path('admin-dashboard/view-participants', view_participants, name="view-participants"),
    path('admin-dashboard/delete-participant/<int:participant_id>/', delete_participant, name="delete-participant"),
    path('participant-dashboard/', participant_dashboard, name="participant-dashboard"),
    path('rsvp-event/<int:event_id>/', rsvp_event, name="rsvp-event"),
    path('activate-rsvp/<int:event_id>/<str:token>/', activate_rsvp, name="activate-rsvp"),
    path('view-dashboard/', view_dashboard, name="view-dashboard")
]
