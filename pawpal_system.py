from dataclasses import dataclass, field
from typing import List, Dict
from datetime import date, datetime, timedelta

@dataclass
class Task:
    description: str
    time: str  # Changed to str in "HH:MM" format
    priority: int  # 1-5, higher is more important
    type: str  # e.g., 'walk', 'feed'
    frequency: str  # e.g., 'daily', 'weekly'
    completion_status: bool = False  # False by default
    due_date: date = field(default_factory=date.today)

    def mark_complete(self):
        """Mark the task as completed."""
        self.completion_status = True
        # For recurring tasks, automatically create the next occurrence
        if self.frequency in ("daily", "weekly"):
            delta = timedelta(days=1 if self.frequency == "daily" else 7)
            next_due = self.due_date + delta
            return Task(
                description=self.description,
                time=self.time,
                priority=self.priority,
                type=self.type,
                frequency=self.frequency,
                completion_status=False,
                due_date=next_due,
            )
        return None

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
        """Generate a daily plan using priority, time limits, and lightweight conflict checks."""
        all_tasks = owner.get_all_tasks()
        constrained_tasks = self.consider_constraints(owner, all_tasks)
        # Sort by priority descending, then by time ascending
        constrained_tasks.sort(key=lambda t: (-t.priority, self.time_to_minutes(t.time)))
        plan = []
        conflicts = []
        timeline = []  # List of (start_min, end_min, type)
        current_time = 0  # Start at 0 minutes
        for task in constrained_tasks:
            task_duration = self.time_to_minutes(task.time)
            start = current_time
            end = start + task_duration
            if end <= owner.available_time:
                # Check for conflicts: e.g., no two same type within 10 min
                if not any(t_type == task.type and abs(start - t_end) < 10 for t_start, t_end, t_type in timeline):
                    plan.append(task)
                    timeline.append((start, end, task.type))
                    current_time = end
                else:
                    conflicts.append(f"Conflict: {task.description} too close to another {task.type}")
            else:
                conflicts.append(f"Time conflict: {task.description} exceeds available time")
        self.conflicts = conflicts
        return plan

    def time_to_minutes(self, time_str: str) -> int:
        """Convert a HH:MM time string to total minutes."""
        h, m = map(int, time_str.split(':'))
        return h * 60 + m

    def consider_constraints(self, owner: Owner, tasks: List[Task]) -> List[Task]:
        """Filter tasks by recurrence rules for the current day."""
        today = datetime.now().weekday()  # 0=Monday, 6=Sunday
        filtered = []
        for task in tasks:
            if task.frequency == "daily":
                filtered.append(task)
            elif task.frequency == "weekly" and today == 0:  # Example: only on Mondays
                filtered.append(task)
        return filtered

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by HH:MM time, then by priority descending."""
        def time_to_minutes(t: str) -> int:
            h, m = map(int, t.split(':'))
            return h * 60 + m
        return sorted(tasks, key=lambda t: (time_to_minutes(t.time), -t.priority))

    def detect_time_conflicts(self, owner: Owner) -> List[str]:
        """Return warning strings for same-time task collisions across all pets."""
        slots: Dict[str, List[str]] = {}
        for pet in owner.pets:
            for task in pet.tasks:
                slots.setdefault(task.time, []).append(f"{pet.name}: {task.description}")

        warnings = []
        for time_slot, entries in sorted(slots.items()):
            if len(entries) > 1:
                warnings.append(
                    f"Warning: {len(entries)} tasks are scheduled at {time_slot} -> "
                    + "; ".join(entries)
                )
        return warnings

    def get_tasks_for_pet(self, owner: Owner, pet_name: str) -> List[Task]:
        """Return all tasks that belong to the specified pet."""
        return [task for pet in owner.pets if pet.name == pet_name for task in pet.tasks]

    def get_incomplete_tasks(self, owner: Owner) -> List[Task]:
        """Return all tasks that are not marked completed."""
        all_tasks = owner.get_all_tasks()
        return [task for task in all_tasks if not task.completion_status]