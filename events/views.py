from events.forms import EventModelForm, RSVPForm, CategoryModelForm
from events.models import Event, Category, RSVP
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Q, Prefetch
from datetime import date, datetime
from django.shortcuts import get_object_or_404
from events.forms import RegisterForm, LoginForm, AssignRoleForm, CreateGroupForm, EditProfileForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView

User = get_user_model()


class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["username"] =  user.username
        context['email'] = user.email
        context['first_name'] = user.first_name
        context['last_name'] = user.last_name
        context['phone_number'] = user.phone_number
        context['profile_image'] = user.profile_image
        context['date_joined'] = user.date_joined
        context['last_login'] = user.last_login
        return context
    

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

@login_required
def details(request, id):
    event = Event.objects.select_related("category").prefetch_related("participants").get(id=id)
    return render(request, 'event_details.html', {'event': event})

# @login_required
# @user_passes_test(is_organizer, login_url='no-permission')
# def organizer_dashboard(request):
#     type = request.GET.get('type', '')

#     events = Event.objects.select_related("category").all()
#     participants = User.objects.all()

#     if type == "upcoming":
#         events = events.filter(start_date__gte=date.today())
#     elif type == "past":
#         events = events.filter(end_date__lt=date.today())
#     elif type == "all":
#         events = events
    

#     participant_count = participants.count()
#     event_counts = Event.objects.aggregate(
#         total=Count('id'),
#         upcoming=Count('id', filter=Q(start_date__gte=date.today())),
#         past=Count('id', filter=Q(end_date__lt=date.today()))
#     )
#     view_type = "today"
#     todays_events = Event.objects.filter(start_date=date.today())

#     context = {
#         'events': events,
#         'participants': participants,
#         'participant_count': participant_count,
#         'event_counts': event_counts,
#         'type': type,
#         'view_type': view_type,
#         'todays_events': todays_events
#     }
#     return render(request, 'organizer/organizer_dashboard.html', context)


class OrganizerDashboardView(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = 'log-in'
    template_name = 'organizer/organizer_dashboard.html'
    permission_required = 'events.add_event'

    def get(self, request, *args, **kwargs):
        type = request.GET.get('type', '')

        events = Event.objects.select_related("category").all()
        participants = User.objects.all()

        if type == "upcoming":
            events = events.filter(start_date__gte=date.today())
        elif type == "past":
            events = events.filter(end_date__lt=date.today())
        elif type == "all":
            events = events

        participant_count = participants.count()
        event_counts = Event.objects.aggregate(
            total=Count('id'),
            upcoming=Count('id', filter=Q(start_date__gte=date.today())),
            past=Count('id', filter=Q(end_date__lte=date.today()))
        )
        view_type = "today"
        todays_events = Event.objects.filter(start_date=date.today())

        context = {
            'events': events,
            'participants': participants,
            'participant_count': participant_count,
            'event_counts': event_counts,
            'type': type,
            'view_type': view_type,
            'todays_events': todays_events
        }
        return render(request, self.template_name, context)


# @login_required
# @permission_required('events.add_event', login_url='no-permission')
# def create_event(request):
#     event_form = EventModelForm()
#     # participant_form = ParticipantModelForm()
#     if request.method == "POST":
#         event_form = EventModelForm(request.POST, request.FILES)
#         # participant_form = ParticipantModelForm(request.POST)
#         if event_form.is_valid():
#             event = event_form.save()
#             # if participant_form.is_valid():
#             #     participant = participant_form.save()
#             #     participant.event.add(event)
#             messages.success(request, 'Event created successfully')
#             return redirect('organizer-dashboard')
#     categories = Category.objects.all()
#     context = {
#         'event_form': event_form,
#         # 'participant_form': participant_form,
#         'categories': categories
#     }
#     return render(request, 'event_form.html', context)

class CreateEvent(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    login_url = 'log-in'
    permission_required = 'events.add_event'
    form_class = EventModelForm
    model = Event
    template_name = 'event_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_form'] = self.form_class()
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        form.save()    
        return redirect('organizer-dashboard')
    

# @login_required
# @permission_required('events.change_event', login_url='no-permission')
# def update_event(request, id):
#     event = get_object_or_404(Event, id=id)  
#     event_form = EventModelForm(instance=event)

#     if request.method == "POST":
#         event_form = EventModelForm(request.POST, instance=event)
#         if event_form.is_valid():
#             event = event_form.save()
#             messages.success(request, 'Event updated successfully')
#             return redirect('organizer-dashboard') 

#     context = {
#         'event_form': event_form,
#         'categories': Category.objects.all()
#     }
#     return render(request, 'event_form.html', context)

class UpdateEvent(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    login_url = 'log-in'
    permission_required = 'events.change_event'
    model = Event
    pk_url_kwarg = 'event_id'
    template_name = 'event_form.html'
    form_class = EventModelForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        context['event_form'] = self.form_class(instance=event)
        context['categories'] = Category.objects.all()
        return context
    def post(self, request, *args, **kwargs):
        event_form = self.form_class(request.POST, instance=self.get_object())
        if event_form.is_valid():
            event_form.save()
            messages.success(request, 'Event updated successfully')
            return redirect('organizer-dashboard')

# def update_participant(request, id):
#     try:
#         event = Event.objects.get(id=id)
#     except Event.DoesNotExist:
#         return render(request, "404.html", status=404)

#     if request.method == "POST":
#         participant_form = ParticipantModelForm(request.POST)
#         if participant_form.is_valid():
#             participant = participant_form.save()
#             event.participants.add(participant)
#             messages.success(request, "Participant updated successfully.")
#             return redirect("event-details", id=event.id)
#     else:
#         participant_form = ParticipantModelForm()

#     return render(request, "update_participant.html", {"form": participant_form, "event": event})

@login_required
@permission_required('events.change_category', login_url='no-permission')
def update_category(request, event_id):
    event = Event.objects.get(id=event_id)
    categories = Category.objects.all()
    if request.method == "POST":
        selected_category_id = request.POST.get('category')
        if selected_category_id:
            selected_category = Category.objects.get(id=selected_category_id)
            event.category = selected_category
            event.save()
            messages.success(request, "Category updated successfully.")
            return redirect("organizer-dashboard") 
    return render(request, "update_category.html", {"categories": categories})


def search_events(request):
    searchText = request.GET.get('searchText', '')
    if searchText:
        events = Event.objects.filter(Q(name__icontains=searchText) | Q(location__icontains=searchText))
    else:
        events = Event.objects.all()
    if not events.exists():
        messages.info(request, "No events found matching your search criteria.")
    return render(request, 'event_home.html', {'events': events})

@login_required
@permission_required('events.delete_event', login_url='no-permission')
def delete_event(request, id):
    event = Event.objects.get(id=id)

    if request.method == "POST":
        event.delete()
        return redirect('organizer-dashboard')

    return render(request, "delete_event.html", {"event": event})


def home(request):
    events = Event.objects.select_related("category").prefetch_related("participants").all()
    q = request.GET.get('q')
    if q:
        events = events.filter(Q(name__icontains=q) | Q(location__icontains=q))

    category = request.GET.get('type')
    if category:
        events = events.filter(category__name__icontains=category)

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        events = events.filter(start_date__gte=start_date, start_date__lte=end_date)
    categories = Category.objects.all()
    context = {'events':events, 'categories':categories}
    return render(request, 'event_home.html', context)


# def register(request):
#     # event = Event.objects.get(id=31)
#     form = RegisterForm()
#     if request.method == "POST":
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data.get('password1'))
#             user.is_active = False
#             user.save()
#             # event.participants.add(user)
#             messages.success(request, 'You have registered successfully. An activation email has been sent. Please check your email')
#             return redirect('register')
#     return render(request, 'registration/register.html', {'form':form})

class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            messages.success(request, 'You have registered successfully. An activation email has been sent. Please check your email')
            return redirect('register')
        return render(request, self.template_name, {'form':form})


def log_in(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    return render(request, 'registration/log_in.html', {'form':form})

@login_required
def log_out(request):
    logout(request)
    return redirect('log-in')


def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('log-in')
        else:
            return HttpResponse('Invalid id or token')
    except User.DoesNotExist:
        return HttpResponse('User not found')


@login_required
@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()
    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No role assigned'
    if request.user.groups.filter(name="Admin").exists():
        return render(request, 'admin/dashboard.html', {'users':users})

# @login_required
# @user_passes_test(is_admin, login_url='no-permission')
# def Assign_role(request, user_id):
#     user = User.objects.get(id=user_id)
#     form = AssignRoleForm()
#     if request.method == "POST":
#         form = AssignRoleForm(request.POST)
#         if form.is_valid():
#             role = form.cleaned_data.get('role')
#             user.groups.clear()
#             user.groups.add(role)
#             messages.success(request, f'{user.username} has been assigned to {role.name} role.')
#             return redirect('admin-dashboard')
#     return render(request, 'admin/assigned_role.html', {'form': form})

class AssignRoleView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    form_class = AssignRoleForm
    model = User
    template_name = 'admin/assigned_role.html'
    login_url = 'log-in'
    permission_required = 'events.add_event'
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('admin-dashboard')
    
    def form_valid(self, form):
        user = self.get_object()
        role = form.cleaned_data.get('role')
        user.groups.clear()
        user.groups.add(role)
        messages.success(self.request, f'{user.username} has been assigned to {role.name} role')
        return super().form_valid(form)
    


login_required
@user_passes_test(is_admin, login_url='no-permission')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have successfully created a group')
            return redirect('create-group')
    return render(request, 'admin/create_group.html', {'form': form})

@login_required
@user_passes_test(is_admin, login_url='no-permission')
def delete_group(request, group_id):
    group = Group.objects.get(id=group_id)
    if request.method == "POST":
        group.delete()
        return redirect('admin-dashboard')
    return render(request, 'admin/group_list.html')

@login_required
@user_passes_test(is_admin, login_url='no-permission')
def view_groups(request):
    groups = Group.objects.all()
    return render(request, 'admin/groups_list.html', {'groups': groups})

@login_required
@permission_required('events.add_category', login_url='no-permission')
def create_category(request):
    form = CategoryModelForm()
    if request.method == "POST":
        form = CategoryModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category has been created successfully')
            return redirect('organizer-dashboard')
    return render(request, 'create_category.html', {'form': form})

@login_required
@permission_required('events.view_category', login_url='no-permission')
def view_category(request):
    categories = Category.objects.all()
    return render(request, 'delete_category.html', {'categories': categories}) 

@login_required
@permission_required('events.delete_category', login_url='no-permission')
def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.method == "POST":
        category.delete()
        return redirect('organizer-dashboard')
    return render(request, 'delete_category.html')

@login_required
def view_participants(request):
    participants = User.objects.all()
    # if request.user.group.filter(name="Admin").exists() or request.user.group.filter(name="Organizer").exists():
    return render(request, 'admin/participants_list.html', {'participants':participants})

@login_required
@permission_required('event.delete_user', login_url='no-permission')
def delete_participant(request, participant_id):
    participant = User.objects.get(id=participant_id)
    if request.method == "POST":
        participant.delete()
        return redirect('view-participants')


def rsvp_event(request, event_id):
    event = Event.objects.get(id=event_id)
    rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)
    form = RSVPForm(instance=rsvp)
    if request.method == "POST":
        form = RSVPForm(request.POST, instance=rsvp)
        if form.is_valid():
            if not event.participants.filter(id =request.user.id).exists():
                event.participants.add(request.user)
            form.save()
            messages.success(request, 'Your RSVP has been updated. Please check your mail to activate.')
            return redirect('rsvp-event', event_id=event_id)
    return render(request, 'user/rsvp_form.html', {'form': form})

@login_required
def participant_dashboard(request):
    # this was previously called view_rsvp
    rsvps = RSVP.objects.select_related('user', 'event').filter(user=request.user)
    if request.user.groups.filter(name="Participant").exists():
        return render(request, 'user/participant_dashboard.html', {'rsvps':rsvps})


def activate_rsvp(request, event_id, token):
    try:
        rsvp = RSVP.objects.get(id=event_id)
        user = rsvp.user
        if default_token_generator.check_token(user, token):
            rsvp.is_active = True
            rsvp.save()
            messages.success(request, 'You have activated your RSVP successfully')
            return redirect('participant-dashboard')
        else:
            return HttpResponse('Invalid ID or token')
        
    except RSVP.DoesNotExist:
        return HttpResponse('RSVP not found')

@login_required
def view_dashboard(request):
    if request.user.groups.filter(name="Admin").exists():
        return redirect('admin-dashboard')
    elif request.user.groups.filter(name="Organizer").exists():
        return redirect('organizer-dashboard')
    elif request.user.groups.filter(name="Participant").exists():
        return redirect('participant-dashboard')
    else:
        return HttpResponse('<h3>you are not assigned to any valid group</h3>', status=403)
    
    


class PasswordChange(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm


class PasswordReset(PasswordResetView):
    template_name = 'registration/password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('log-in')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["protocol"] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'An email has been sent to you. Please reset the password by clicking the link provided in the email')
        print('hello')
        return super().form_valid(form)
    

class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/password_reset.html'
    success_url = reverse_lazy('log-in')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password reset successfully')
        return super().form_valid(form)
    