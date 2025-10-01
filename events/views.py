from events.forms import EventModelForm, ParticipantModelForm, CategoryModelForm
from events.models import Event, Participant, Category
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date, datetime
from django.shortcuts import get_object_or_404

def details(request, id):
    event = Event.objects.select_related("category").prefetch_related("participants").get(id=id)
    return render(request, 'event_details.html', {'event': event})


def organizer_dashboard(request):
    type = request.GET.get('type', 'all')

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

    todays_events = Event.objects.filter(start_date=date.today())

    context = {
        'events': events,
        'participants': participants,
        'participant_count': participant_count,
        'event_counts': event_counts,
        'type': type,
        'todays_events': todays_events
    }
    return render(request, 'organizer_dashboard.html', context)


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



def update_event(request, id):
    event = get_object_or_404(Event, id=id)
    event_form = EventModelForm(instance=event)

    if request.method == "POST":
        event_form = EventModelForm(request.POST, instance=event)
        if event_form.is_valid():
            event = event_form.save()
            messages.success(request, 'Event updated successfully')
            return redirect('event-details', id=event.pk) 

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


def delete_event(request, id):
    event = Event.objects.get(id=id)

    if request.method == "POST":
        event.delete()
        return redirect('manager-dashboard')

    return render(request, "delete_event.html", {"event": event})


def view_events(request):
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
