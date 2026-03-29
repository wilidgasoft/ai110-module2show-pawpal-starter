from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from itertools import combinations
from uuid import uuid4

# Built once at import time; reused by every CareTask.next_occurrence() call.
_FREQUENCY_DELTA: dict[str, timedelta] = {
    "daily":       timedelta(days=1),
    "twice_daily": timedelta(hours=12),
    "weekly":      timedelta(weeks=1),
}


@dataclass
class CareTask:
    name: str
    category: str  # "exercise" | "nutrition" | "medical" | "grooming" | "enrichment"
    duration_minutes: int
    priority: int  # 1 (low) → 5 (critical)
    is_required: bool
    frequency: str  # "daily" | "twice_daily" | "weekly"
    notes: str = ""
    completed: bool = False
    scheduled_date: str = field(default_factory=lambda: date.today().isoformat())
    id: str = field(default_factory=lambda: str(uuid4()))

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> CareTask | None:
        """Return a new CareTask scheduled for the next occurrence based on this task's frequency.

        Looks up the time delta from the module-level _FREQUENCY_DELTA constant and
        adds it to scheduled_date. The returned task is a fresh instance with a new id
        so it can be tracked independently.

        Returns:
            A new CareTask with scheduled_date advanced by the frequency delta,
            or None if the frequency value is not recognised as recurring.
        """
        _delta = _FREQUENCY_DELTA.get(self.frequency)
        if _delta is None:
            return None
        next_date = date.fromisoformat(self.scheduled_date) + _delta
        return CareTask(
            name=self.name,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            is_required=self.is_required,
            frequency=self.frequency,
            notes=self.notes,
            scheduled_date=next_date.isoformat(),
        )

    def is_skippable(self) -> bool:
        """Return True if the task is optional and can be skipped."""
        return not self.is_required

    def to_dict(self) -> dict:
        """Serialize the task to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "is_required": self.is_required,
            "frequency": self.frequency,
            "notes": self.notes,
        }


@dataclass
class Vet:
    name: str
    clinic_name: str
    phone: str
    email: str
    recommended_tasks: list[CareTask] = field(default_factory=list)

    def add_recommendation(self, task: CareTask) -> None:
        """Add a care task to this vet's list of recommendations."""
        pass

    def get_recommendations(self) -> list[CareTask]:
        """Return all tasks recommended by this vet."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age_years: float
    weight_kg: float
    medical_notes: str = ""
    vet: Vet | None = None
    care_tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Append a care task to this pet's task list."""
        self.care_tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet's care list by its unique id.

        Rebuilds care_tasks excluding the matching task. Silently does nothing
        if no task with the given id exists.

        Args:
            task_id: The UUID string of the task to remove.
        """
        self.care_tasks = [t for t in self.care_tasks if t.id != task_id]

    def get_tasks_by_priority(self) -> list[CareTask]:
        """Return a sorted copy of care tasks from highest to lowest priority.

        Does not modify the original care_tasks list.

        Returns:
            A new list of CareTask objects ordered by priority descending (5 → 1).
        """
        return sorted(self.care_tasks, key=lambda t: t.priority, reverse=True)

    def get_required_tasks(self) -> list[CareTask]:
        """Return only the tasks that are marked as required for this pet.

        Returns:
            A list of CareTask objects where is_required is True.
            Returns an empty list if no required tasks exist.
        """
        return [t for t in self.care_tasks if t.is_required]

    def sync_vet_tasks(self) -> None:
        """Merge vet-recommended tasks into care_tasks, skipping any already present.

        Compares by task id to avoid duplicates. Does nothing if no vet is assigned.
        """
        if self.vet is None:
            return
        existing_ids = {t.id for t in self.care_tasks}
        for task in self.vet.recommended_tasks:
            if task.id not in existing_ids:
                self.care_tasks.append(task)


@dataclass
class Owner:
    name: str
    available_time_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet from this owner's list by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_tasks_by_pet(self, pet_name: str) -> list[CareTask]:
        """Return a copy of all care tasks belonging to the named pet.

        Uses next() to find the first pet whose name matches, then returns
        a shallow copy of that pet's care_tasks list.

        Args:
            pet_name: The exact name of the pet to look up (case-sensitive).

        Returns:
            A list of CareTask objects for the matched pet,
            or an empty list if no pet with that name is registered.
        """
        pet = next((p for p in self.pets if p.name == pet_name), None)
        return list(pet.care_tasks) if pet else []


@dataclass
class Schedule:
    date: str  # ISO format: "2026-03-28"
    owner: Owner
    pet: Pet
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a care task to this schedule."""
        pass

    def remove_task(self, task_id: str) -> None:
        """Remove a task by its unique id."""
        pass

    def get_total_duration(self) -> int:
        """Return the sum of all task durations in minutes."""
        pass

    def fits_in_budget(self) -> bool:
        """Check whether total task duration fits within owner's available time."""
        pass

    def sort_by_priority(self) -> None:
        """Sort the schedule's task list in-place from highest to lowest priority.

        Mutates self.tasks directly using list.sort() with priority as the key.
        Tasks with equal priority retain their relative order (stable sort).
        """
        self.tasks.sort(key=lambda task: task.priority, reverse=True)

    def sort_by_time(self) -> None:
        """Sort the schedule's task list in-place by start time in HH:MM format.

        Delegates time parsing to _to_minutes(). Tasks without a valid HH:MM
        value in notes are treated as time 0 (midnight) and sorted first.
        """
        self.tasks.sort(key=lambda task: self._to_minutes(task.notes) or 0)

    def mark_task_complete(self, task_id: str) -> CareTask | None:
        """Mark a task as done and automatically append its next occurrence to the schedule.

        Finds the task by id, calls mark_complete() on it, then calls
        next_occurrence() to generate the following instance. If the task
        recurs, the new instance is appended to self.tasks immediately.

        Args:
            task_id: The UUID string of the task to complete.

        Returns:
            The newly created next-occurrence CareTask if the task recurs,
            or None if the task id was not found or the task does not recur.
        """
        for task in self.tasks:
            if task.id == task_id:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task is not None:
                    self.tasks.append(next_task)
                return next_task
        return None

    @staticmethod
    def _to_minutes(time_str: str) -> int | None:
        """Convert an 'HH:MM' string to total minutes since midnight.

        Used as the sort key for sort_by_time() and as the interval
        start point for get_conflicts().

        Args:
            time_str: A time string in 'HH:MM' 24-hour format (e.g. '07:30').

        Returns:
            An integer representing minutes since midnight (e.g. 450 for '07:30'),
            or None if the string is missing, empty, or not in HH:MM format.
        """
        try:
            h, m = time_str.split(":")
            return int(h) * 60 + int(m)
        except (ValueError, AttributeError):
            return None

    def get_conflicts(self) -> list[str]:
        """Detect and return warning messages for all overlapping task time windows.

        Builds a list of (task, start, end) tuples for every task that has a
        valid HH:MM time in notes, then checks every unique pair using
        itertools.combinations. Two tasks conflict when one starts before the
        other ends: start_A < end_B and start_B < end_A.

        Returns:
            A list of human-readable warning strings, one per conflicting pair.
            Returns an empty list when no conflicts are detected.
        """
        timed = [
            (task, s, s + task.duration_minutes)
            for task in self.tasks
            if (s := self._to_minutes(task.notes)) is not None
        ]
        return [
            f"CONFLICT [{self.pet.name}]  "
            f"'{a.name}' ({a.notes}, {a.duration_minutes} min)  overlaps  "
            f"'{b.name}' ({b.notes}, {b.duration_minutes} min)"
            for (a, a_start, a_end), (b, b_start, b_end) in combinations(timed, 2)
            if a_start < b_end and b_start < a_end
        ]

    def filter_tasks(self, *, completed: bool | None = None, pet_name: str | None = None) -> list[CareTask]:
        """Return a filtered subset of this schedule's tasks in a single pass.

        Both filters are optional. Passing None for a parameter disables that
        filter entirely. Both conditions are combined with AND, so only tasks
        that satisfy every active filter are included.

        Args:
            completed: If True, return only completed tasks. If False, return
                only incomplete tasks. If None, completion status is ignored.
            pet_name: If provided, return tasks only when the schedule's pet
                name matches exactly. If None, pet name is not checked.

        Returns:
            A new list of CareTask objects matching all active filters.
            Returns an empty list if no tasks match.
        """
        return [
            t for t in self.tasks
            if (completed is None or t.completed == completed)
            and (pet_name is None or self.pet.name == pet_name)
        ]


@dataclass
class Plan:
    schedule: Schedule
    reasoning: str = ""
    skipped_tasks: list[CareTask] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def generate(cls, owner: Owner, pet: Pet, date: str) -> Plan:
        """
        Core scheduling logic:
        1. Sync vet-recommended tasks into pet.care_tasks.
        2. Always include required tasks first (regardless of time budget).
        3. Fill remaining time with optional tasks sorted by priority (high → low).
        4. Record skipped tasks and emit warnings for any skipped required tasks.
        """
        pass

    def get_summary(self) -> str:
        """Return a human-readable summary of the plan and its scheduled tasks."""
        pass

    def get_warnings(self) -> list[str]:
        """Return any warnings generated during plan creation (e.g. skipped required tasks)."""
        pass
