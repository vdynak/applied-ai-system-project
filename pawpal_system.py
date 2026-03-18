from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Task:
    description: str
    time: int  # duration in minutes
    priority: int  # 1-5, higher is more important
    type: str  # e.g., 'walk', 'feed'
    frequency: str  # e.g., 'daily', 'weekly'
    completion_status: bool = False  # False by default

    def mark_complete(self):
        """Mark the task as completed."""
        self.completion_status = True

@dataclass
class Pet:
    name: str
    type: str
    age: int
    tasks: List[Task]

    def add_task(self, task: Task):
        """Add a task to the pet's task list."""
        self.tasks.append(task)

class Owner:
    def __init__(self, name: str, preferences: Dict, available_time: int):
        self.name = name
        self.preferences = preferences
        self.available_time = available_time
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def set_preferences(self, prefs: Dict):
        """Update the owner's preferences."""
        self.preferences.update(prefs)

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks from all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

class Scheduler:
    def generate_plan(self, owner: Owner) -> List[Task]:
        """Generate a daily plan based on owner's tasks and constraints."""
        all_tasks = owner.get_all_tasks()
        constrained_tasks = self.consider_constraints(owner, all_tasks)
        # Sort by priority descending, then by time ascending
        constrained_tasks.sort(key=lambda t: (-t.priority, t.time))
        plan = []
        total_time = 0
        for task in constrained_tasks:
            if total_time + task.time <= owner.available_time:
                plan.append(task)
                total_time += task.time
        return plan

    def consider_constraints(self, owner: Owner, tasks: List[Task]) -> List[Task]:
        """Apply constraints to the list of tasks."""
        # For now, filter tasks based on preferences if any, but keep all
        # Could add logic to exclude based on frequency or preferences
        return tasks  # Placeholder: return all tasks