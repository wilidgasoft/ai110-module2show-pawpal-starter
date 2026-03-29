from pawpal_system import CareTask, Owner, Pet, Schedule


def make_task(name="Walk", *, priority=3, notes="", frequency="daily",
              duration_minutes=20, scheduled_date="2026-03-28"):
    return CareTask(
        name=name,
        category="exercise",
        duration_minutes=duration_minutes,
        priority=priority,
        is_required=True,
        frequency=frequency,
        notes=notes,
        scheduled_date=scheduled_date,
    )


def make_schedule(tasks=None):
    owner = Owner(name="Alex", available_time_minutes=120)
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age_years=2.0, weight_kg=25.0)
    schedule = Schedule(date="2026-03-28", owner=owner, pet=pet, tasks=list(tasks or []))
    return schedule


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False   # starts incomplete
    task.mark_complete()
    assert task.completed is True    # now marked done


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age_years=2.0, weight_kg=25.0)
    assert len(pet.care_tasks) == 0
    pet.add_task(make_task("Morning Walk"))
    pet.add_task(make_task("Evening Walk"))
    assert len(pet.care_tasks) == 2


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_sort_by_time_orders_tasks_chronologically():
    """Tasks with notes in HH:MM format should come out earliest-first."""
    t1 = make_task("Dinner",        notes="18:00")
    t2 = make_task("Morning Walk",  notes="07:00")
    t3 = make_task("Midday Meal",   notes="12:00")
    schedule = make_schedule([t1, t2, t3])

    schedule.sort_by_time()

    names = [t.name for t in schedule.tasks]
    assert names == ["Morning Walk", "Midday Meal", "Dinner"]


def test_sort_by_time_empty_schedule_does_not_crash():
    """sort_by_time() on an empty task list should return without error."""
    schedule = make_schedule()
    schedule.sort_by_time()  # must not raise
    assert schedule.tasks == []


def test_sort_by_time_tasks_without_notes_sorted_first():
    """Tasks missing a valid HH:MM in notes fall back to 0 (midnight) and sort first."""
    t_no_time  = make_task("Grooming",      notes="")
    t_morning  = make_task("Morning Walk",  notes="07:00")
    schedule   = make_schedule([t_morning, t_no_time])

    schedule.sort_by_time()

    assert schedule.tasks[0].name == "Grooming"
    assert schedule.tasks[1].name == "Morning Walk"


# ---------------------------------------------------------------------------
# Recurrence
# ---------------------------------------------------------------------------

def test_daily_task_creates_next_day_occurrence():
    """Completing a daily task must generate a new task dated one day later."""
    task     = make_task("Morning Walk", frequency="daily", scheduled_date="2026-03-28")
    schedule = make_schedule([task])

    next_task = schedule.mark_task_complete(task.id)

    assert next_task is not None
    assert next_task.scheduled_date == "2026-03-29"


def test_next_occurrence_resets_completed_flag():
    """The generated next-occurrence task must start as incomplete."""
    task = make_task(frequency="daily", scheduled_date="2026-03-28")
    task.mark_complete()

    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.completed is False


def test_next_occurrence_has_new_id():
    """Each recurrence must get a fresh UUID so it can be tracked independently."""
    task      = make_task(frequency="daily", scheduled_date="2026-03-28")
    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.id != task.id


def test_non_recurring_task_returns_none():
    """next_occurrence() on an unrecognised frequency should return None."""
    task = make_task(frequency="monthly")   # not in _FREQUENCY_DELTA
    assert task.next_occurrence() is None


def test_mark_task_complete_unknown_id_returns_none():
    """mark_task_complete() with a non-existent id should return None silently."""
    schedule = make_schedule([make_task()])
    result   = schedule.mark_task_complete("no-such-id")
    assert result is None


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_get_conflicts_flags_exact_same_start_time():
    """Two tasks starting at the same time must be reported as a conflict."""
    t1 = make_task("Feeding",  notes="08:00", duration_minutes=15)
    t2 = make_task("Brushing", notes="08:00", duration_minutes=10)
    schedule = make_schedule([t1, t2])

    conflicts = schedule.get_conflicts()

    assert len(conflicts) == 1
    assert "Feeding"  in conflicts[0]
    assert "Brushing" in conflicts[0]


def test_get_conflicts_flags_overlapping_tasks():
    """A task starting mid-way through another must be flagged."""
    t1 = make_task("Morning Walk", notes="07:00", duration_minutes=30)  # 07:00–07:30
    t2 = make_task("Vet Check",    notes="07:20", duration_minutes=30)  # 07:20–07:50
    schedule = make_schedule([t1, t2])

    conflicts = schedule.get_conflicts()

    assert len(conflicts) == 1


def test_get_conflicts_no_false_positives_for_sequential_tasks():
    """Tasks that end exactly when the next one starts should NOT conflict."""
    t1 = make_task("Walk",    notes="07:00", duration_minutes=30)  # ends 07:30
    t2 = make_task("Feeding", notes="07:30", duration_minutes=15)  # starts 07:30
    schedule = make_schedule([t1, t2])

    assert schedule.get_conflicts() == []


def test_get_conflicts_empty_schedule_returns_empty_list():
    """get_conflicts() on an empty schedule must return an empty list."""
    assert make_schedule().get_conflicts() == []


def test_get_conflicts_skips_tasks_without_time():
    """Tasks with no HH:MM in notes must be excluded from conflict checking."""
    t1 = make_task("Grooming",     notes="",      duration_minutes=30)
    t2 = make_task("Morning Walk", notes="07:00", duration_minutes=30)
    schedule = make_schedule([t1, t2])

    # Grooming has no parseable time — only one timed task, so no conflict possible.
    assert schedule.get_conflicts() == []
