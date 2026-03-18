import pytest
from pawpal_system import Task, Pet

def test_task_completion():
    """Verify that calling mark_complete() changes the task's status."""
    task = Task("Test task", 10, 3, "test", "daily")
    assert task.completion_status == False
    task.mark_complete()
    assert task.completion_status == True

def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("TestPet", "dog", 2, [])
    initial_count = len(pet.tasks)
    task = Task("New task", 15, 4, "play", "daily")
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1