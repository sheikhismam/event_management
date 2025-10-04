#!/usr/bin/env python
import os
import django
import random
import traceback
from faker import Faker
from datetime import timedelta

# --- Django setup ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "event_management.settings")
django.setup()

# --- Models ---
from events.models import Category, Event, Participant

fake = Faker()

CATEGORY_NAMES = [
    "Music", "Technology", "Business", "Sports", "Education",
    "Health", "Social", "Art", "Food", "Travel", "Science", "Community"
]

EVENT_PREFIXES = ["International", "Annual", "Local", "Global", "Summer", "Winter", "Monthly"]
EVENT_TYPES = ["Conference", "Festival", "Meetup", "Workshop", "Hackathon", "Concert", "Seminar"]

def populate(n_categories=6, n_events=30, n_participants=100):
    try:
        Participant.objects.all().delete()
        Event.objects.all().delete()
        Category.objects.all().delete()
    except Exception:
        print("Failed clearing DB:")
        traceback.print_exc()
        return

    # --- Create categories ---
    if n_categories <= len(CATEGORY_NAMES):
        chosen_names = random.sample(CATEGORY_NAMES, n_categories)
    else:
        chosen_names = CATEGORY_NAMES[:] + [
            random.choice(CATEGORY_NAMES) for _ in range(n_categories - len(CATEGORY_NAMES))
        ]

    categories = []
    for name in chosen_names:
        cat = Category.objects.create(
            name=name,
            description=fake.sentence(nb_words=8)
        )
        categories.append(cat)

    print("Created categories:")
    for c in categories:
        print(f" - {c.name}")

    # --- Create events ---
    events = []
    for _ in range(n_events):
        name = f"{random.choice(EVENT_PREFIXES)} {random.choice(EVENT_TYPES)}"

        # start_date between +1 and +90 days
        start_date = fake.date_between(start_date="+1d", end_date="+90d")

        # sometimes no end_date (30% chance), otherwise ensure end >= start
        if random.random() < 0.30:
            end_date = None
        else:
            # choose an end date between start_date and start_date + 90 days
            end_date = start_date + timedelta(days=random.randint(0, 90))

        ev = Event.objects.create(
            name=name,
            description=fake.text(max_nb_chars=150),
            start_date=start_date,
            end_date=end_date,
            time=fake.time_object(),
            location=fake.city(),
            category=random.choice(categories)
        )
        events.append(ev)

    # --- Create participants and attach to events ---
    for _ in range(n_participants):
        try:
            p = Participant.objects.create(
                name=fake.name(),
                email=fake.unique.email()
            )
        except Exception:
            # show error and continue (so one bad row won't stop the whole run)
            print("Error creating participant:")
            traceback.print_exc()
            continue

        # choose how many events to attach this participant to
        if not events:
            continue
        k = random.randint(1, min(4, len(events)))
        sample_events = random.sample(events, k=k)

        attached = False

        # 1) Try common ManyToMany attribute names on Participant instance
        for attr_name in ("events", "event", "registered_events", "registered_event"):
            try:
                attr = getattr(p, attr_name, None)
                if attr is not None and callable(getattr(attr, "add", None)):
                    attr.add(*sample_events)
                    attached = True
                    break
            except Exception:
                # try next option
                pass

        if attached:
            continue

        # 2) Try to set a ForeignKey field on Participant that points to Event
        try:
            for f in Participant._meta.get_fields():
                # look for many_to_one (ForeignKey) pointing to Event
                if getattr(f, "many_to_one", False) and getattr(f, "related_model", None) is Event:
                    # set to one random event (FK can only point to single Event)
                    setattr(p, f.name, sample_events[0])
                    p.save()
                    attached = True
                    break
        except Exception:
            traceback.print_exc()

        if attached:
            continue

        # 3) Try to attach via reverse relation on Event (common names: participants, participant_set)
        try:
            for e in sample_events:
                try:
                    # common reverse name
                    if hasattr(e, "participants") and callable(getattr(e.participants, "add", None)):
                        e.participants.add(p)
                        attached = True
                        continue
                except Exception:
                    pass

                try:
                    e.participant_set.add(p)
                    attached = True
                except Exception:
                    pass
        except Exception:
            traceback.print_exc()

        if not attached:
            print(f"⚠️ Could not attach participant {p.pk} to events. Check Participant/Event relation in models.")

    # --- Summary ---
    print(f"\n✅ Populated DB with {len(categories)} categories, {len(events)} events, {n_participants} participants.")
    print("Example of event -> category (first 10):")
    for ev in Event.objects.all()[:10]:
        print(f" - {ev.name}  ->  {ev.category.name}")


if __name__ == "__main__":
    populate()
