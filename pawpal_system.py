from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CareTask:
    name: str
    category: str           # "exercise" | "nutrition" | "medical" | "grooming" | "enrichment"
    duration_minutes: int
    priority: int           # 1 (low) → 5 (critical)
    is_required: bool
    frequency: str          # "daily" | "twice_daily" | "weekly"
    notes: str = ""

    def is_skippable(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass


@dataclass
class Vet:
    name: str
    clinic_name: str
    phone: str
    email: str
    recommended_tasks: list[CareTask] = field(default_factory=list)

    def add_recommendation(self, task: CareTask) -> None:
        pass

    def get_recommendations(self) -> list[CareTask]:
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
        pass

    def remove_task(self, task_name: str) -> None:
        pass

    def get_tasks_by_priority(self) -> list[CareTask]:
        pass

    def get_required_tasks(self) -> list[CareTask]:
        pass


@dataclass
class Owner:
    name: str
    available_time_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_name: str) -> None:
        pass

    def get_total_available_time(self) -> int:
        pass


@dataclass
class Schedule:
    date: str               # ISO format: "2026-03-28"
    owner: Owner
    pet: Pet
    tasks: list[CareTask] = field(default_factory=list)

    @property
    def total_duration_minutes(self) -> int:
        return self.get_total_duration()

    def add_task(self, task: CareTask) -> None:
        pass

    def remove_task(self, task_name: str) -> None:
        pass

    def fits_in_budget(self) -> bool:
        pass

    def get_total_duration(self) -> int:
        pass

    def sort_by_priority(self) -> None:
        pass


@dataclass
class Plan:
    schedule: Schedule
    reasoning: str = ""
    skipped_tasks: list[CareTask] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def generate(cls, owner: Owner, pet: Pet) -> Plan:
        pass

    def get_summary(self) -> str:
        pass

    def get_warnings(self) -> list[str]:
        pass
