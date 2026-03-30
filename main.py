"""PawPal+ CLI — professional formatted output using tabulate + ANSI colours."""
from tabulate import tabulate
from pawpal_system import (
    Owner, Pet, CareTask, Schedule,
    CATEGORY_EMOJI, FREQUENCY_LABEL, PRIORITY_META, PRIORITY_BG,
)

# ── ANSI colour helpers ───────────────────────────────────────────────────────
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_DIM    = "\033[2m"

_GREEN  = "\033[92m"
_YELLOW = "\033[93m"
_RED    = "\033[91m"
_CYAN   = "\033[96m"
_WHITE  = "\033[97m"
_GREY   = "\033[90m"

# Maps priority tier → ANSI colour used for that row's priority badge.
_PRIORITY_COLOUR: dict[str, str] = {
    "Low":      _GREEN,
    "Medium":   _YELLOW,
    "High":     _RED,
    "Critical": _RED + _BOLD,
}


def _fmt_priority(task: CareTask) -> str:
    """Return a coloured priority badge string for CLI output."""
    meta = PRIORITY_META.get(task.priority)
    if not meta:
        return str(task.priority)
    emoji, tier = meta
    colour = _PRIORITY_COLOUR.get(tier, _WHITE)
    return f"{colour}{emoji} {tier}{_RESET}"


def _fmt_category(task: CareTask) -> str:
    """Return emoji + category name."""
    icon = CATEGORY_EMOJI.get(task.category, "•")
    return f"{icon} {task.category.capitalize()}"


def _fmt_window(task: CareTask) -> str:
    """Return 'HH:MM–HH:MM' or '—' when no start time is set."""
    try:
        h, m = map(int, task.notes.split(":"))
    except (ValueError, AttributeError):
        return _GREY + "—" + _RESET
    end = h * 60 + m + task.duration_minutes
    return f"{h:02d}:{m:02d}–{end // 60:02d}:{end % 60:02d}"


def _fmt_status(task: CareTask) -> str:
    """Green tick if done, dim circle if pending."""
    return f"{_GREEN}✔ Done{_RESET}" if task.completed else f"{_GREY}○ Pending{_RESET}"


def _section(title: str, width: int = 60) -> None:
    """Print a bold cyan box-drawing section header."""
    bar = "─" * (width - 2)
    print(f"\n{_CYAN}{_BOLD}┌{bar}┐{_RESET}")
    padded = title.center(width - 2)
    print(f"{_CYAN}{_BOLD}│{_WHITE}{padded}{_CYAN}│{_RESET}")
    print(f"{_CYAN}{_BOLD}└{bar}┘{_RESET}")


def _divider(width: int = 60) -> None:
    print(_DIM + "─" * width + _RESET)


def print_schedule(sched: Schedule) -> None:
    """Print a rich tabulate table for one pet's schedule."""
    sched.sort_by_priority_then_time()

    icon = CATEGORY_EMOJI.get("exercise", "🐾")
    species_icon = "🐶" if sched.pet.species.lower() == "dog" else (
                   "🐱" if sched.pet.species.lower() == "cat" else "🐾")

    print(f"\n  {species_icon} {_BOLD}{sched.pet.name}{_RESET}"
          f"  {_DIM}({sched.pet.breed} · {sched.pet.age_years:.0f} yrs · "
          f"{sched.pet.weight_kg} kg){_RESET}")
    _divider(56)

    if not sched.tasks:
        print(f"  {_GREY}No tasks scheduled.{_RESET}")
        return

    rows = [
        [
            _fmt_window(t),
            _fmt_category(t),
            t.name,
            f"{t.duration_minutes} min",
            _fmt_priority(t),
            "✅ Yes" if t.is_required else f"{_GREY}No{_RESET}",
            _fmt_status(t),
        ]
        for t in sched.tasks
    ]

    headers = [
        _BOLD + "Window"    + _RESET,
        _BOLD + "Category"  + _RESET,
        _BOLD + "Task"      + _RESET,
        _BOLD + "Duration"  + _RESET,
        _BOLD + "Priority"  + _RESET,
        _BOLD + "Required"  + _RESET,
        _BOLD + "Status"    + _RESET,
    ]

    print(tabulate(rows, headers=headers, tablefmt="rounded_outline",
                   colalign=("left", "left", "left", "right", "left", "center", "left")))

    total = sum(t.duration_minutes for t in sched.tasks)
    done  = sum(1 for t in sched.tasks if t.completed)
    print(f"\n  {_DIM}Tasks: {len(sched.tasks)}  ·  "
          f"Total: {total} min  ·  "
          f"Completed: {done}/{len(sched.tasks)}{_RESET}")


def print_conflicts(schedules: list[Schedule]) -> None:
    """Print a conflict report table for all schedules."""
    all_conflicts = [c for s in schedules for c in s.get_conflicts()]

    if not all_conflicts:
        print(f"\n  {_GREEN}✔  No scheduling conflicts detected.{_RESET}")
        return

    rows = []
    for raw in all_conflicts:
        # Raw format: "CONFLICT [PetName]  'TaskA' (time, dur)  overlaps  'TaskB' (time, dur)"
        parts = raw.split("  ", 2)
        pet_tag  = parts[0].replace("CONFLICT ", "").strip("[]")
        detail   = parts[2] if len(parts) > 2 else raw
        task_a, _, task_b = detail.partition("  overlaps  ")
        rows.append([f"⚠️  {_RED}{pet_tag}{_RESET}", task_a.strip(), task_b.strip()])

    headers = [_BOLD + "Pet" + _RESET,
               _BOLD + "Task A" + _RESET,
               _BOLD + "Overlaps Task B" + _RESET]
    print()
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))


def print_budget(owner: Owner, schedules: list[Schedule]) -> None:
    """Print a time-budget summary with a progress bar."""
    total = sum(t.duration_minutes for s in schedules for t in s.tasks)
    budget = owner.available_time_minutes
    pct = min(total / budget, 1.0) if budget else 0
    bar_width = 30
    filled = int(pct * bar_width)
    colour = _GREEN if pct <= 0.75 else (_YELLOW if pct <= 1.0 else _RED)
    bar = colour + "█" * filled + _DIM + "░" * (bar_width - filled) + _RESET

    print(f"\n  {_BOLD}Time Budget{_RESET}")
    print(f"  {bar}  {colour}{total} / {budget} min{_RESET}")
    if total > budget:
        over = total - budget
        print(f"  {_RED}⚠  {over} min over budget — consider removing optional tasks.{_RESET}")
    else:
        remain = budget - total
        print(f"  {_GREEN}✔  {remain} min remaining in today's budget.{_RESET}")


# ── Sample data ───────────────────────────────────────────────────────────────
owner = Owner(name="Alex Rivera", available_time_minutes=180)
buddy = Pet(name="Buddy", species="Dog", breed="Golden Retriever", age_years=3.0, weight_kg=28.5)
luna  = Pet(name="Luna",  species="Cat", breed="Siamese",          age_years=5.0, weight_kg=4.2)
owner.add_pet(buddy)
owner.add_pet(luna)

t_walk    = CareTask("Morning Walk",    "exercise",   30, priority=4, is_required=True,  frequency="daily",       notes="07:00", scheduled_date="2026-03-29")
t_vet     = CareTask("Vet Check",       "medical",    30, priority=5, is_required=True,  frequency="weekly",      notes="07:20", scheduled_date="2026-03-29")
t_lunch   = CareTask("Lunch Feeding",   "nutrition",  10, priority=3, is_required=True,  frequency="daily",       notes="12:00", scheduled_date="2026-03-29")
t_feed_am = CareTask("Morning Feeding", "nutrition",   5, priority=5, is_required=True,  frequency="twice_daily", notes="08:00", scheduled_date="2026-03-29")
t_brush   = CareTask("Brushing",        "grooming",   15, priority=2, is_required=False, frequency="daily",       notes="08:00", scheduled_date="2026-03-29")
t_feed_pm = CareTask("Evening Feeding", "nutrition",   5, priority=5, is_required=True,  frequency="twice_daily", notes="19:00", scheduled_date="2026-03-29")
t_play    = CareTask("Enrichment Play", "enrichment", 20, priority=1, is_required=False, frequency="daily",       notes="17:00", scheduled_date="2026-03-29")

t_vet.completed = True  # mark one done for demo

for t in [t_walk, t_vet, t_lunch]:
    buddy.add_task(t)
for t in [t_feed_am, t_brush, t_feed_pm, t_play]:
    luna.add_task(t)

buddy_sched = Schedule(date="2026-03-29", owner=owner, pet=buddy, tasks=list(buddy.care_tasks))
luna_sched  = Schedule(date="2026-03-29", owner=owner, pet=luna,  tasks=list(luna.care_tasks))

# ── Output ────────────────────────────────────────────────────────────────────
_section("🐾  PawPal+  ·  Daily Schedule  ·  2026-03-29")

for sched in (buddy_sched, luna_sched):
    print_schedule(sched)

_section("⚠️  Conflict Report")
print_conflicts([buddy_sched, luna_sched])

_section("⏱  Time Budget")
print_budget(owner, [buddy_sched, luna_sched])

print()
