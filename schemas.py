"""Marshmallow schemas for PawPal+ dataclasses.

Each schema mirrors its dataclass exactly. @post_load decorators reconstruct
the live Python objects after deserialization so callers always get typed
instances back — never raw dicts.

Import order matters: CareTaskSchema must be defined before VetSchema
and PetSchema because both nest it.
"""
from __future__ import annotations

from marshmallow import Schema, fields, post_load

from pawpal_system import CareTask, Vet, Pet, Owner


class CareTaskSchema(Schema):
    id = fields.Str()
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    duration_minutes = fields.Int(required=True)
    priority = fields.Int(required=True)
    is_required = fields.Bool(required=True)
    frequency = fields.Str(required=True)
    notes = fields.Str(load_default="")
    completed = fields.Bool(load_default=False)
    scheduled_date = fields.Str()

    @post_load
    def make(self, data: dict, **_) -> CareTask:
        return CareTask(**data)


class VetSchema(Schema):
    name = fields.Str(required=True)
    clinic_name = fields.Str(required=True)
    phone = fields.Str(required=True)
    email = fields.Str(required=True)
    recommended_tasks = fields.List(fields.Nested(CareTaskSchema), load_default=[])

    @post_load
    def make(self, data: dict, **_) -> Vet:
        return Vet(**data)


class PetSchema(Schema):
    name = fields.Str(required=True)
    species = fields.Str(required=True)
    breed = fields.Str(required=True)
    age_years = fields.Float(required=True)
    weight_kg = fields.Float(required=True)
    medical_notes = fields.Str(load_default="")
    vet = fields.Nested(VetSchema, allow_none=True, load_default=None)
    care_tasks = fields.List(fields.Nested(CareTaskSchema), load_default=[])

    @post_load
    def make(self, data: dict, **_) -> Pet:
        return Pet(**data)


class OwnerSchema(Schema):
    name = fields.Str(required=True)
    available_time_minutes = fields.Int(required=True)
    preferences = fields.List(fields.Str(), load_default=[])
    pets = fields.List(fields.Nested(PetSchema), load_default=[])

    @post_load
    def make(self, data: dict, **_) -> Owner:
        return Owner(**data)
