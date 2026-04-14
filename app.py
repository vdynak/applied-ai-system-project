import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from ai_scheduler import AIScheduler, AIScheduleResult


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


def ai_task_rows(owner: Owner, result: AIScheduleResult, scheduler: Scheduler) -> list[dict]:
    """Convert AI schedule result into table rows with reasoning."""
    rows = []
    for i, task in enumerate(result.tasks, 1):
        rows.append(
            {
                "#": i,
                "Pet": find_pet_name_for_task(owner, task),
                "Task": task.description,
                "Time": task.time,
                "Priority": task.priority,
                "Type": task.type,
            }
        )
    return rows


# --- Session State Initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", {}, 120)
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

owner = st.session_state.owner

# --- Page Config ---
st.set_page_config(page_title="PawPal+ AI", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+ AI")
st.caption("AI-powered pet care scheduling with explainable reasoning")

# --- Sidebar: API Key & Settings ---
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key to enable AI-powered scheduling. "
             "Without it, the app uses rule-based scheduling as a fallback.",
    )
    st.divider()
    st.markdown(
        "**How AI Scheduling Works**\n\n"
        "PawPal+ sends your pet and task info to OpenAI's GPT model, "
        "which generates an optimized schedule and explains its reasoning. "
        "Your data is only sent when you click 'Generate AI Schedule'. "
        "No data is stored by the AI service."
    )
    st.divider()
    st.markdown(
        "**Responsible AI Design**\n\n"
        "- Inputs are validated before AI processing\n"
        "- AI output is parsed and verified against time constraints\n"
        "- Rule-based fallback if AI is unavailable\n"
        "- Confidence level shown for every schedule\n"
        "- All reasoning is transparent and explainable"
    )

# --- Owner Setup ---
st.subheader("Owner Profile")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value=owner.name)
    if owner_name != owner.name:
        owner.name = owner_name
with col2:
    available_time = st.number_input(
        "Available time (minutes)",
        min_value=10,
        max_value=480,
        value=owner.available_time,
    )
    if available_time != owner.available_time:
        owner.available_time = available_time

# --- Pet Management ---
st.subheader("Your Pets")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
with col3:
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add Pet", use_container_width=True):
    new_pet = Pet(pet_name, species, pet_age, [])
    owner.add_pet(new_pet)
    st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    for pet in owner.pets:
        st.write(f"**{pet.name}** — {pet.type}, age {pet.age}")
else:
    st.info("No pets added yet. Add a pet above to get started.")

# --- Task Management ---
st.subheader("Add Task")
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
        priority = st.selectbox("Priority (1-5)", [1, 2, 3, 4, 5], index=4)
    with col4:
        task_type = st.selectbox("Type", ["walk", "feed", "play", "groom", "meds", "enrichment", "vet", "training"])

    frequency = st.selectbox("Frequency", ["daily", "weekly"])

    if st.button("Add Task", key="add_task_btn", use_container_width=True):
        time_str = f"{duration // 60:02d}:{duration % 60:02d}"
        new_task = Task(task_desc, time_str, priority, task_type, frequency)
        selected_pet.add_task(new_task)
        st.success(f"Added '{task_desc}' to {selected_pet.name}")
else:
    st.info("Add a pet first to add tasks.")

# --- Task Overview ---
st.subheader("Task Overview")
if owner.pets:
    scheduler = Scheduler()
    all_tasks = owner.get_all_tasks()
    incomplete = scheduler.get_incomplete_tasks(owner)

    if all_tasks:
        tab1, tab2 = st.tabs(["All Tasks", "Incomplete Only"])
        with tab1:
            st.table(task_rows(owner, all_tasks, scheduler))
        with tab2:
            if incomplete:
                st.table(task_rows(owner, incomplete, scheduler))
            else:
                st.success("All tasks completed!")
    else:
        st.info("No tasks yet. Add tasks above.")

st.divider()

# --- AI Schedule Generation ---
st.subheader("AI-Powered Schedule")
st.caption(
    "Generate an intelligent daily plan with explanations. "
    "The AI considers pet welfare, task priority, time constraints, and spacing."
)

col1, col2 = st.columns(2)
with col1:
    use_ai = st.toggle("Enable AI Scheduling", value=True)
with col2:
    show_debug = st.toggle("Show AI transparency details", value=False)

if st.button("Generate Schedule", type="primary", use_container_width=True):
    if not owner.pets or not any(pet.tasks for pet in owner.pets):
        st.error("Add pets and tasks first.")
    else:
        with st.spinner("Generating your schedule..."):
            if use_ai:
                ai_sched = AIScheduler(api_key=api_key if api_key else None)
                result = ai_sched.generate_ai_schedule(owner)
            else:
                # Pure rule-based scheduling
                ai_sched = AIScheduler()
                result = ai_sched._fallback_schedule(owner, "Rule-based mode selected.")

            st.session_state.ai_result = result

# --- Display Results ---
result = st.session_state.ai_result
if result:
    # Confidence indicator
    confidence_colors = {"high": "green", "medium": "orange", "low": "red"}
    confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
    conf = result.confidence
    st.markdown(
        f"**Schedule Confidence:** {confidence_emoji.get(conf, '⚪')} {conf.capitalize()}"
    )

    if result.used_fallback:
        st.info("ℹ️ This schedule was generated using the rule-based fallback system.")

    # AI Reasoning
    st.markdown("#### Why this schedule?")
    st.markdown(f"> {result.reasoning}")

    # Schedule table
    if result.tasks:
        scheduler = Scheduler()
        st.markdown("#### Your Daily Plan")
        st.table(ai_task_rows(owner, result, scheduler))

        total_time = sum(scheduler.time_to_minutes(t.time) for t in result.tasks)
        st.success(
            f"Total scheduled time: {total_time} min / {owner.available_time} min available"
        )
    else:
        st.warning("No tasks could be scheduled within the available time.")

    # Warnings
    if result.warnings:
        st.markdown("#### Warnings")
        for w in result.warnings:
            st.warning(w)

    # Transparency details
    if show_debug:
        st.markdown("#### AI Transparency Details")
        st.json(
            {
                "used_fallback": result.used_fallback,
                "confidence": result.confidence,
                "num_tasks_scheduled": len(result.tasks),
                "num_warnings": len(result.warnings),
                "ai_model": "gpt-4o-mini" if not result.used_fallback else "rule-based",
            }
        )
