from datetime import date, time

import streamlit as st

from pawpal_system import (
    Frequency,
    Owner,
    Pet,
    Priority,
    Schedule,
    ScheduledTask,
    Scheduler,
    Task,
)

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

st.subheader("Quick Demo Inputs (UI only)")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner

owner.name = st.text_input("Owner name", value=owner.name)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Pet name can't be empty.")
    else:
        owner.add_pet(Pet(pet_name.strip(), species))
        st.toast(f"Added {pet_name.strip()} the {species} to {owner.name}'s pets.")

if owner.pets:
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species, "tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add care tasks to a pet. These feed into the scheduler below.")


def add_task() -> None:
    """Build a Task from the form inputs and attach it to the selected pet."""
    title = st.session_state.task_title.strip()
    if not title:
        st.session_state.task_error = "Task title can't be empty."
        return
    pet = owner.pets[st.session_state.task_pet]
    pet.add_task(
        Task(
            title=title,
            duration_minutes=int(st.session_state.task_duration),
            priority=Priority[st.session_state.task_priority.upper()],
            start_time=st.session_state.task_start_time,
            frequency=Frequency(st.session_state.task_frequency),
            due_date=st.session_state.task_due_date,
        )
    )
    st.toast(f"Added '{title}' to {pet.name}'s tasks.")


if not owner.pets:
    st.info("Add a pet before adding tasks.")
else:
    st.selectbox(
        "Pet",
        range(len(owner.pets)),
        format_func=lambda i: owner.pets[i].name,
        key="task_pet",
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Task title", value="Morning walk", key="task_title")
    with col2:
        st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key="task_duration")
    with col3:
        st.selectbox("Priority", ["low", "medium", "high"], index=2, key="task_priority")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.time_input("Start time", value=time(8, 0), key="task_start_time")
    with col5:
        st.selectbox("Frequency", [f.value for f in Frequency], key="task_frequency")
    with col6:
        st.date_input("Due date", value=date.today(), key="task_due_date")

    st.button("Add task", on_click=add_task)
    if error := st.session_state.pop("task_error", None):
        st.error(error)

    for pet in owner.pets:
        tasks = pet.get_tasks()
        st.write(f"**{pet.name}** ({pet.species})")
        if tasks:
            st.table(
                [
                    {
                        "title": t.title,
                        "start": f"{t.start_time:%H:%M}",
                        "end": f"{t.end_time:%H:%M}",
                        "duration (min)": t.duration_minutes,
                        "priority": t.priority.name.lower(),
                        "frequency": t.frequency.value,
                        "due date": t.due_date.isoformat(),
                        "done": t.completed,
                    }
                    for t in tasks
                ]
            )
        else:
            st.caption("No tasks yet.")

st.divider()

st.subheader("Build Schedule")
st.caption("Builds a plan from every pet's tasks due on the chosen day.")

schedule_day = st.date_input("Schedule for", value=date.today(), key="schedule_day")

if st.button("Generate schedule"):
    scheduler = Scheduler()
    schedule = scheduler.create_schedule(owner, schedule_day)
    for warning in scheduler.detect_conflicts(schedule.scheduled):
        st.warning(warning)
    if not schedule.scheduled:
        st.info(f"No tasks due on {schedule_day:%A, %b %d}.")
    else:
        st.success(
            f"{len(schedule.scheduled)} task(s) scheduled, {schedule.total_minutes} min total."
        )
        st.table(
            [
                {
                    "time": f"{s.task.start_time:%H:%M}-{s.task.end_time:%H:%M}",
                    "pet": s.pet.name,
                    "task": s.task.title,
                    "duration (min)": s.task.duration_minutes,
                    "priority": s.task.priority.name.lower(),
                    "why": s.reason,
                }
                for s in schedule.scheduled
            ]
        )
    for pet, task, why in schedule.skipped:
        st.warning(f"Skipped {pet.name}: {task.title} ({why})")
