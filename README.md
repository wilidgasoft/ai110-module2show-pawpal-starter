# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

# Smarter Scheduling

The following features were added beyond the starter skeleton:

- **Auto-recurring tasks** — when `mark_task_complete()` is called on a `daily`, `twice_daily`, or `weekly` task, a new instance is automatically created for the next occurrence using Python's `timedelta`. No manual re-entry needed.
- **Conflict detection** — `Schedule.get_conflicts()` scans all tasks for overlapping time windows using their `HH:MM` start time and `duration_minutes`. It returns plain warning strings instead of raising exceptions, so the app stays running.
- **Sort by time or priority** — `sort_by_time()` orders tasks chronologically using a shared `_to_minutes()` helper; `sort_by_priority()` orders them by urgency (5 → 1). Both sort in-place.
- **Flexible filtering** — `filter_tasks(completed=..., pet_name=...)` supports filtering by completion status, pet name, or both in a single pass. Either parameter can be omitted.
- **Owner-level task lookup** — `Owner.get_tasks_by_pet(name)` returns all tasks for a named pet without exposing the internal pet list directly.
- **Required-task guarantee** — required tasks are always scheduled regardless of the owner's available time budget; optional tasks fill remaining time by priority.
