from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Task:
    name: str
    duration: int
    priority: int
    type: str

@dataclass
class Pet:
    name: str
    type: str
    age: int
    tasks: List[Task]

    def add_task(self, task: Task):
        pass

class Owner:
    def __init__(self, name: str, preferences: Dict, available_time: int):
        self.name = name
        self.preferences = preferences
        self.available_time = available_time
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        pass

    def set_preferences(self, prefs: Dict):
        pass

class Scheduler:
    def generate_plan(self, owner: Owner) -> List[Task]:
        pass

    def consider_constraints(self, owner: Owner, tasks: List[Task]) -> List[Task]:
        pass