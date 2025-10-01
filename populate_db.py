import os
import django
import random
from faker import Faker

# ---------------------------
# CHANGE THIS to your project
# ---------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "event_management.settings")
django.setup()
# ---------------------------

from events.models import Category, Event, Participant

fake = Faker()

# Realistic category names (you can add/remove entries)
CATEGORY_NAMES = [
    "Music", "Technology", "Business", "Sports", "Education",
    "Health", "Social", "Art", "Food", "Travel", "Science", "Community"
]

EVENT_PREFIXES = ["International", "Annual", "Local", "Global", "Summer", "Winter", "Monthly"]
EVENT_TYPES = ["Conference", "Festival", "Meetup", "Workshop", "Hackathon", "Concert", "Seminar"]

def populate(n_categories=6, n_events=30, n_participants=100):
    # wipe old data so script is idempotent
    Participant.objects.all().delete()
    Event.objects.all().delete()
    Category.objects.all().delete()

    # ensure n_categories doesn't exceed available names — allow repeats if requested number is larger
    if n_categories <= len(CATEGORY_NAMES):
        chosen_names = random.sample(CATEGORY_NAMES, n_categories)
    else:
        # pick all once, then fill remaining with random choices
        chosen_names = CATEGORY_NAMES[:] + [random.choice(CATEGORY_NAMES) for _ in range(n_categories - len(CATEGORY_NAMES))]

    # Create categories (explicit name field)
    categories = []
    for name in chosen_names:
        cat = Category.objects.create(
            name=name,
            description=fake.sentence(nb_words=8)
        )
        categories.append(cat)

    # Show created category names
    print("Created categories:")
    for c in categories:
        print(f" - {c.name}")

    # Create events and attach to categories
    events = []
    for _ in range(n_events):
        name = f"{random.choice(EVENT_PREFIXES)} {random.choice(EVENT_TYPES)}"
        ev = Event.objects.create(
            name=name,
            description=fake.text(max_nb_chars=150),
            date=fake.date_between(start_date="+1d", end_date="+180d"),
            time=fake.time_object(),
            location=fake.city(),
            category=random.choice(categories)
        )
        events.append(ev)

    # Create participants (your model requires email, so we still fill it)
    for _ in range(n_participants):
        p = Participant.objects.create(
            name=fake.name(),
            email=fake.unique.email()
        )
        # give each participant between 1 and 4 event memberships
        p.event.add(*random.sample(events, k=random.randint(1, min(4, len(events)))))

    print(f"\n✅ Populated DB with {len(categories)} categories, {len(events)} events, {n_participants} participants.")
    print("Example of event -> category (first 10):")
    for ev in Event.objects.all()[:10]:
        print(f" - {ev.name}  ->  {ev.category.name}")

if __name__ == "__main__":
    populate()
