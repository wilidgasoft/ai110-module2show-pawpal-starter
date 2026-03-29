import streamlit as st
from datetime import date
import pawpal_system as pawpal

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Owner ────────────────────────────────────────────────────────────────────
st.header("1. Owner")

owner_name = st.text_input("Owner name", value="Jordan")
available_time = st.number_input(
    "Available time today (minutes)", min_value=10, max_value=480, value=120
)

if st.button("Save Owner"):
    st.session_state.owner = pawpal.Owner(
        name=owner_name,
        available_time_minutes=int(available_time),
    )
    st.success(f"Owner '{owner_name}' saved!")

# Ensure owner always exists so the rest of the app can reference it safely
if "owner" not in st.session_state:
    st.session_state.owner = pawpal.Owner(
        name=owner_name,
        available_time_minutes=int(available_time),
    )

owner: pawpal.Owner = st.session_state.owner

st.divider()

# ── Add a Pet ────────────────────────────────────────────────────────────────
st.header("2. Add a Pet")

col1, col2 = st.columns(2)
with col1:
    pet_name    = st.text_input("Pet name", value="Mochi")
    species     = st.selectbox("Species", ["Dog", "Cat", "Other"])
with col2:
    breed       = st.text_input("Breed", value="Mixed")
    age         = st.number_input("Age (years)", min_value=0.0, max_value=30.0, value=2.0, step=0.5)
    weight      = st.number_input("Weight (kg)", min_value=0.1, max_value=200.0, value=5.0, step=0.1)

if st.button("Add Pet"):
    new_pet = pawpal.Pet(
        name=pet_name,
        species=species,
        breed=breed,
        age_years=float(age),
        weight_kg=float(weight),
    )
    owner.add_pet(new_pet)          # calls Owner.add_pet()
    st.success(f"Pet '{pet_name}' added to {owner.name}'s profile!")

if owner.pets:
    st.write(f"**{owner.name}'s pets:** " + ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet — add one above.")

st.divider()

# ── Schedule a Task ───────────────────────────────────────────────────────────
st.header("3. Schedule a Task")

if not owner.pets:
    st.warning("Add at least one pet before scheduling tasks.")
else:
    target_pet_name = st.selectbox(
        "Assign task to", [p.name for p in owner.pets]
    )
    target_pet = next(p for p in owner.pets if p.name == target_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_name = st.text_input("Task name", value="Morning walk")
        category  = st.selectbox(
            "Category",
            ["exercise", "nutrition", "medical", "grooming", "enrichment"],
        )
    with col2:
        duration  = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        priority  = st.slider("Priority (1 low → 5 critical)", 1, 5, 3)
    with col3:
        frequency   = st.selectbox("Frequency", ["daily", "twice_daily", "weekly"])
        is_required = st.checkbox("Required?", value=True)
        notes       = st.text_input("Start time (HH:MM, 24-hr)", value="07:00")

    if st.button("Add Task"):
        new_task = pawpal.CareTask(
            name=task_name,
            category=category,
            duration_minutes=int(duration),
            priority=priority,
            is_required=is_required,
            frequency=frequency,
            notes=notes,
        )
        target_pet.add_task(new_task)   # calls Pet.add_task()
        st.success(f"Task '{task_name}' added to {target_pet.name}!")

st.divider()

# ── Today's Schedule ──────────────────────────────────────────────────────────
st.header("4. Today's Schedule")

sort_mode = st.radio("Sort tasks by", ["Time", "Priority"], horizontal=True)

if st.button("Generate Schedule"):
    if not owner.pets or all(len(p.care_tasks) == 0 for p in owner.pets):
        st.warning("Add pets and tasks first.")
    else:
        today = date.today().isoformat()
        total_minutes = 0

        for pet in owner.pets:
            if not pet.care_tasks:
                continue

            # Build a Schedule and sort it using the Scheduler methods
            schedule = pawpal.Schedule(
                date=today, owner=owner, pet=pet, tasks=list(pet.care_tasks)
            )
            if sort_mode == "Time":
                schedule.sort_by_time()
            else:
                schedule.sort_by_priority()

            st.subheader(f"🐾 {pet.name} ({pet.breed})")

            # ── Conflict warnings ────────────────────────────────────────────
            conflicts = schedule.get_conflicts()
            if conflicts:
                st.error(
                    f"**{len(conflicts)} scheduling conflict(s) detected** — "
                    "fix these before starting your day:"
                )
                for conflict in conflicts:
                    # Strip the "CONFLICT [PetName]  " prefix for plain-English display
                    readable = conflict.split("  ", 1)[-1] if "  " in conflict else conflict
                    st.warning(f"**Overlap:** {readable}")
            else:
                st.success("No scheduling conflicts — all clear!")

            # ── Task table ───────────────────────────────────────────────────
            rows = [
                {
                    "Task": t.name,
                    "Start": t.notes or "—",
                    "Duration": f"{t.duration_minutes} min",
                    "Category": t.category,
                    "Priority": f"{t.priority}/5",
                    "Required": "Yes" if t.is_required else "No",
                }
                for t in schedule.tasks
            ]
            st.table(rows)

            total_minutes += sum(t.duration_minutes for t in schedule.tasks)

        # ── Budget summary ───────────────────────────────────────────────────
        st.divider()
        budget_ok = total_minutes <= owner.available_time_minutes
        if budget_ok:
            st.success(
                f"Total care time: **{total_minutes} min** — "
                f"fits within your {owner.available_time_minutes} min budget."
            )
        else:
            over = total_minutes - owner.available_time_minutes
            st.error(
                f"Total care time: **{total_minutes} min** — "
                f"exceeds your {owner.available_time_minutes} min budget by **{over} min**. "
                "Consider removing optional tasks."
            )
