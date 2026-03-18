from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_sorting_correctness_chronological_order():
    """Verify tasks are sorted in chronological HH:MM order."""
    scheduler = Scheduler()
    tasks = [
        Task("Evening walk", "18:30", 2, "walk", "daily"),
        Task("Morning feed", "08:00", 4, "feed", "daily"),
        Task("Midday play", "12:15", 3, "play", "daily"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.time for task in sorted_tasks] == ["08:00", "12:15", "18:30"]


def test_recurrence_logic_daily_completion_creates_next_day_task():
    """Confirm daily completion creates a new task due on the next day."""
    today = date.today()
    task = Task("Morning walk", "08:00", 5, "walk", "daily", due_date=today)

    next_task = task.mark_complete()

    assert task.completion_status is True
    assert next_task is not None
    assert next_task.completion_status is False
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.description == task.description


def test_conflict_detection_flags_duplicate_times():
    """Verify scheduler returns warnings when multiple tasks share the same time."""
    owner = Owner("Jordan", {}, 600)
    pet1 = Pet("Max", "dog", 4, [])
    pet2 = Pet("Luna", "cat", 3, [])
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    pet1.add_task(Task("Walk", "08:00", 5, "walk", "daily"))
    pet2.add_task(Task("Feed", "08:00", 4, "feed", "daily"))

    scheduler = Scheduler()
    warnings = scheduler.detect_time_conflicts(owner)

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Max: Walk" in warnings[0]
    assert "Luna: Feed" in warnings[0]