from events.forms import EventModelForm, ParticipantModelForm, CategoryModelForm
from events.models import Event, Participant, Category
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date, datetime
from django.shortcuts import get_object_or_404
from events.forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

def details(request, id):
    event = Event.objects.select_related("category").prefetch_related("participants").get(id=id)
    return render(request, 'event_details.html', {'event': event})


def organizer_dashboard(request):
    type = request.GET.get('type', '')

    events = Event.objects.select_related("category").prefetch_related("participants")
    participants = Participant.objects.all()

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
        past=Count('id', filter=Q(end_date__lt=date.today()))
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
    return render(request, 'dashboard/organizer_dashboard.html', context)

@login_required
@permission_required('events.add_event', login_url='no-permission')
def create_event(request):
    event_form = EventModelForm()
    participant_form = ParticipantModelForm()

    if request.method == "POST":
        event_form = EventModelForm(request.POST)
        participant_form = ParticipantModelForm(request.POST)

        if event_form.is_valid():
            event = event_form.save()
            if participant_form.is_valid():
                participant = participant_form.save()
                participant.event.add(event)

            messages.success(request, 'Event created successfully')
            return redirect('view-events')

    categories = Category.objects.all()
    context = {
        'event_form': event_form,
        'participant_form': participant_form,
        'categories': categories
    }
    return render(request, 'event_form.html', context)


@login_required
@permission_required('events.change_event', login_url='no-permission')
def update_event(request, id):
    event = get_object_or_404(Event, id=id)  
    event_form = EventModelForm(instance=event)

    if request.method == "POST":
        event_form = EventModelForm(request.POST, instance=event)
        if event_form.is_valid():
            event = event_form.save()
            messages.success(request, 'Event updated successfully')
            return redirect('event-details', id=event.id) 

    context = {
        'event_form': event_form,
        'categories': Category.objects.all()
    }
    return render(request, 'event_form.html', context)


def update_participant(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        return render(request, "404.html", status=404)

    if request.method == "POST":
        participant_form = ParticipantModelForm(request.POST)
        if participant_form.is_valid():
            participant = participant_form.save()
            event.participants.add(participant)
            messages.success(request, "Participant updated successfully.")
            return redirect("event-details", id=event.id)
    else:
        participant_form = ParticipantModelForm()

    return render(request, "update_participant.html", {"form": participant_form, "event": event})

@login_required
@user_passes_test('events.change_category', login_url='no-permission')
def update_category(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        return render(request, "404.html", status=404)

    if request.method == "POST":
        category_form = CategoryModelForm(request.POST, instance=event.category)
        if category_form.is_valid():
            category_form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("event-details", id=event.id)
    else:
        category_form = CategoryModelForm(instance=event.category)

    return render(request, "update_category.html", {"form": category_form, "event": event})

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

    return render(request, 'event_home.html', {'events': events})


def register(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            messages.success(request, 'You have registered successfully. An activation email has been sent. Please check your email')
            return redirect('log-in')
    return render(request, 'registration/register.html', {'form':form})

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


def is_organizer(user):
    return user.groups.filter(name='Manager').exists()


def Assign_role():
    pass

def create_group():
    pass