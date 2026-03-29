from pawpal_system import CareTask, Pet


def make_task(name="Walk"):
    return CareTask(
        name=name,
        category="exercise",
        duration_minutes=20,
        priority=3,
        is_required=True,
        frequency="daily",
    )


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
