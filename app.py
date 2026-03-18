import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler


def find_pet_name_for_task(owner: Owner, target_task: Task) -> str:
    """Return the pet name for a given task object."""
    for pet in owner.pets:
        if target_task in pet.tasks:
            return pet.name
    return "Unknown"


def task_rows(owner: Owner, tasks: list[Task], scheduler: Scheduler) -> list[dict]:
    """Convert task objects into table rows for Streamlit display."""
    rows = []
    for task in tasks:
        rows.append(
            {
                "Pet": find_pet_name_for_task(owner, task),
                "Task": task.description,
                "Time": task.time,
                "Minutes": scheduler.time_to_minutes(task.time),
                "Priority": task.priority,
                "Type": task.type,
                "Frequency": task.frequency,
                "Completed": task.completion_status,
            }
        )
    return rows

# Initialize Owner in session state if it doesn't exist
if 'owner' not in st.session_state:
    st.session_state.owner = Owner("Jordan", {}, 120)  # Default values

# Access the persistent Owner
owner = st.session_state.owner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value=owner.name)
if st.button("Update Owner Name"):
    owner.name = owner_name
    st.success(f"Owner name updated to {owner.name}")

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet"):
    new_pet = Pet(pet_name, species, 1, [])  # Default age 1
    owner.add_pet(new_pet)
    st.success(f"Added pet: {pet_name} ({species})")

if owner.pets:
    st.write("Your Pets:")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.type})")
else:
    st.info("No pets added yet.")

st.markdown("### Add Task")
if owner.pets:
    pet_options = [pet.name for pet in owner.pets]
    selected_pet_name = st.selectbox("Select Pet for Task", pet_options)
    selected_pet = next(pet for pet in owner.pets if pet.name == selected_pet_name)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_desc = st.text_input("Task Description", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", [1, 2, 3, 4, 5], index=4)
    with col4:
        task_type = st.selectbox("Type", ["walk", "feed", "play", "groom"])

    if st.button("Add Task"):
        time_str = f"{duration//60:02d}:{duration%60:02d}"
        new_task = Task(task_desc, time_str, priority, task_type, "daily")
        selected_pet.add_task(new_task)
        st.success(f"Added task '{task_desc}' to {selected_pet.name}")
else:
    st.info("Add a pet first to add tasks.")

st.markdown("### Task Overview")
if owner.pets:
    scheduler = Scheduler()
    all_tasks = owner.get_all_tasks()
    incomplete = scheduler.get_incomplete_tasks(owner)

    if all_tasks:
        st.write("All Tasks")
        st.table(task_rows(owner, all_tasks, scheduler))
    else:
        st.info("No tasks yet. Add tasks above.")

    if incomplete:
        st.write("Incomplete Tasks")
        st.table(task_rows(owner, incomplete, scheduler))
    else:
        st.info("All tasks completed!")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate your daily pet care plan.")

sort_by_time = st.checkbox("Sort by time (ascending) instead of priority")
filter_pet = st.selectbox("Filter by pet (optional)", ["All"] + [pet.name for pet in owner.pets]) if owner.pets else None
show_incomplete_only = st.checkbox("Show only incomplete tasks", value=True)

if st.button("Generate Schedule"):
    if owner.pets and any(pet.tasks for pet in owner.pets):
        scheduler = Scheduler()
        all_tasks = owner.get_all_tasks()
        if filter_pet and filter_pet != "All":
            all_tasks = scheduler.get_tasks_for_pet(owner, filter_pet)
        incomplete_tasks = scheduler.get_incomplete_tasks(owner)
        tasks_to_plan = incomplete_tasks if show_incomplete_only else all_tasks
        if show_incomplete_only and not tasks_to_plan:
            tasks_to_plan = all_tasks

        constrained_tasks = scheduler.consider_constraints(owner, tasks_to_plan)
        if sort_by_time:
            constrained_tasks = scheduler.sort_by_time(constrained_tasks)
        else:
            constrained_tasks.sort(key=lambda t: (-t.priority, scheduler.time_to_minutes(t.time)))

        # Build a UI plan from the filtered/sorted task set and available time.
        plan = []
        total_time = 0
        for task in constrained_tasks:
            minutes = scheduler.time_to_minutes(task.time)
            if total_time + minutes <= owner.available_time:
                plan.append(task)
                total_time += minutes

        if plan:
            st.success("Schedule generated!")
            st.table(task_rows(owner, plan, scheduler))
            st.success(f"Total scheduled time: {total_time} min / {owner.available_time} min available")

            # Lightweight conflict warnings from Scheduler.
            warnings = scheduler.detect_time_conflicts(owner)
            if warnings:
                st.warning("Potential scheduling conflicts found. Review these before starting your day:")
                for warning in warnings:
                    st.write(f"- {warning}")
        else:
            st.warning("No tasks fit within available time.")
    else:
        st.error("Add pets and tasks first.")
