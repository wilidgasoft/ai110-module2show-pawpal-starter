from pawpal_system import Owner, Pet, CareTask, Schedule

owner = Owner(name="Alex Rivera", available_time_minutes=180)
buddy = Pet(name="Buddy", species="Dog",  breed="Golden Retriever", age_years=3.0, weight_kg=28.5)
luna  = Pet(name="Luna",  species="Cat",  breed="Siamese",          age_years=5.0, weight_kg=4.2)
owner.add_pet(buddy)
owner.add_pet(luna)

# ── Buddy's tasks — two deliberately overlap ──────────────────────────────────
#   Morning Walk   07:00 → 07:30   (30 min)
#   Vet Check      07:20 → 07:50   (30 min)  ← starts inside Morning Walk
#   Lunch Feeding  12:00 → 12:10   (10 min)  ← no conflict
t_walk    = CareTask("Morning Walk",  "exercise",  30, priority=4, is_required=True,  frequency="daily",  notes="07:00", scheduled_date="2026-03-28")
t_vet     = CareTask("Vet Check",     "medical",   30, priority=5, is_required=True,  frequency="weekly", notes="07:20", scheduled_date="2026-03-28")
t_lunch   = CareTask("Lunch Feeding", "nutrition", 10, priority=3, is_required=True,  frequency="daily",  notes="12:00", scheduled_date="2026-03-28")

# ── Luna's tasks — two overlap ────────────────────────────────────────────────
#   Morning Feed   08:00 → 08:05   (5 min)
#   Brushing       08:00 → 08:15   (15 min)  ← exact same start time
#   Evening Feed   19:00 → 19:05   (5 min)   ← no conflict
t_feed_am = CareTask("Morning Feeding", "nutrition", 5,  priority=5, is_required=True,  frequency="twice_daily", notes="08:00", scheduled_date="2026-03-28")
t_brush   = CareTask("Brushing",        "grooming",  15, priority=2, is_required=False, frequency="daily",       notes="08:00", scheduled_date="2026-03-28")
t_feed_pm = CareTask("Evening Feeding", "nutrition", 5,  priority=5, is_required=True,  frequency="twice_daily", notes="19:00", scheduled_date="2026-03-28")

for t in [t_walk, t_vet, t_lunch]:
    buddy.add_task(t)
for t in [t_feed_am, t_brush, t_feed_pm]:
    luna.add_task(t)

buddy_sched = Schedule(date="2026-03-28", owner=owner, pet=buddy, tasks=list(buddy.care_tasks))
luna_sched  = Schedule(date="2026-03-28", owner=owner, pet=luna,  tasks=list(luna.care_tasks))

# ── Helper ────────────────────────────────────────────────────────────────────
def print_schedule(sched: Schedule) -> None:
    sched.sort_by_time()
    print(f"\n  {sched.pet.name} ({sched.pet.breed})")
    print("  " + "-" * 44)
    for t in sched.tasks:
        h, m = map(int, t.notes.split(":"))
        end_min = h * 60 + m + t.duration_minutes
        end_str = f"{end_min // 60:02d}:{end_min % 60:02d}"
        print(f"    {t.notes}–{end_str}  {t.name}  ({t.duration_minutes} min)")

# ── Today's Schedule ──────────────────────────────────────────────────────────
print("=" * 52)
print("TODAY'S SCHEDULE  —  2026-03-28")
print("=" * 52)
for sched in (buddy_sched, luna_sched):
    print_schedule(sched)

# ── Conflict Detection ────────────────────────────────────────────────────────
print("\n" + "=" * 52)
print("CONFLICT REPORT")
print("=" * 52)

all_conflicts = buddy_sched.get_conflicts() + luna_sched.get_conflicts()

if all_conflicts:
    for warning in all_conflicts:
        print(f"  ⚠  {warning}")
else:
    print("  No conflicts detected.")

print("=" * 52)
