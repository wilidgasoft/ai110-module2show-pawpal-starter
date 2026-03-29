from __future__ import annotations
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class CareTask:
    name: str
    category: str           # "exercise" | "nutrition" | "medical" | "grooming" | "enrichment"
    duration_minutes: int
    priority: int           # 1 (low) → 5 (critical)
    is_required: bool
    frequency: str          # "daily" | "twice_daily" | "weekly"
    notes: str = ""
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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
        """Remove a task by its unique id."""
        self.care_tasks = [t for t in self.care_tasks if t.id != task_id]

    def get_tasks_by_priority(self) -> list[CareTask]:
        """Return care tasks sorted from highest to lowest priority."""
        return sorted(self.care_tasks, key=lambda t: t.priority, reverse=True)

    def get_required_tasks(self) -> list[CareTask]:
        """Return only the tasks marked as required."""
        return [t for t in self.care_tasks if t.is_required]

    def sync_vet_tasks(self) -> None:
        """Merge vet-recommended tasks into care_tasks (avoid duplicates by id)."""
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


@dataclass
class Schedule:
    date: str               # ISO format: "2026-03-28"
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
        """Sort scheduled tasks in-place from highest to lowest priority."""
        pass


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
