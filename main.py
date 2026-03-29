from pawpal_system import Owner, Pet, CareTask

# Create owner
owner = Owner(name="Alex Rivera", available_time_minutes=120)

# Create two pets
buddy = Pet(name="Buddy", species="Dog", breed="Golden Retriever", age_years=3.0, weight_kg=28.5)
luna  = Pet(name="Luna",  species="Cat", breed="Siamese",           age_years=5.0, weight_kg=4.2)

owner.add_pet(buddy)
owner.add_pet(luna)

# Tasks for Buddy (morning, midday, evening)
buddy.add_task(CareTask(
    name="Morning Walk",
    category="exercise",
    duration_minutes=30,
    priority=4,
    is_required=True,
    frequency="daily",
    notes="7:00 AM – around the block",
))
buddy.add_task(CareTask(
    name="Lunch Feeding",
    category="nutrition",
    duration_minutes=10,
    priority=3,
    is_required=True,
    frequency="daily",
    notes="12:00 PM – one cup dry food",
))
buddy.add_task(CareTask(
    name="Evening Play Session",
    category="enrichment",
    duration_minutes=20,
    priority=2,
    is_required=False,
    frequency="daily",
    notes="6:00 PM – fetch in the backyard",
))

# Tasks for Luna
luna.add_task(CareTask(
    name="Morning Feeding",
    category="nutrition",
    duration_minutes=5,
    priority=5,
    is_required=True,
    frequency="twice_daily",
    notes="8:00 AM – wet food",
))
luna.add_task(CareTask(
    name="Brushing",
    category="grooming",
    duration_minutes=15,
    priority=2,
    is_required=False,
    frequency="daily",
    notes="3:00 PM – reduce shedding",
))
luna.add_task(CareTask(
    name="Evening Feeding",
    category="nutrition",
    duration_minutes=5,
    priority=5,
    is_required=True,
    frequency="twice_daily",
    notes="7:00 PM – wet food",
))

# Print Today's Schedule
print("=" * 40)
print("       TODAY'S SCHEDULE")
print(f"       Owner: {owner.name}")
print("=" * 40)

for pet in owner.pets:
    print(f"\n{pet.name} ({pet.breed})")
    print("-" * 30)
    for task in pet.get_tasks_by_priority():
        required_tag = "[REQUIRED]" if task.is_required else "[optional]"
        print(f"  {required_tag} {task.name}")
        print(f"    Category : {task.category}")
        print(f"    Duration : {task.duration_minutes} min")
        print(f"    Time     : {task.notes}")

print("\n" + "=" * 40)
total = sum(
    t.duration_minutes for pet in owner.pets for t in pet.care_tasks
)
print(f"Total care time today : {total} min")
print(f"Owner time budget     : {owner.available_time_minutes} min")
print("=" * 40)
