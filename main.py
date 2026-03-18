from pawpal_system import Owner, Pet, Task, Scheduler

# Create an Owner
owner = Owner("Alice", {"prefers_morning": True}, 90)  # 90 minutes available time

# Create at least two Pets
pet1 = Pet("Max", "dog", 5, [])
pet2 = Pet("Luna", "cat", 3, [])

# Add pets to owner
owner.add_pet(pet1)
owner.add_pet(pet2)

# Create at least three Tasks with different times
task1 = Task("Morning walk", 30, 5, "walk", "daily")
task2 = Task("Feed breakfast", 10, 4, "feed", "daily")
task3 = Task("Play session", 45, 3, "play", "daily")

# Add tasks to pets
pet1.add_task(task1)
pet1.add_task(task2)
pet2.add_task(task3)

# Create Scheduler and generate plan
scheduler = Scheduler()
plan = scheduler.generate_plan(owner)

# Print Today's Schedule
print("Today's Schedule:")
for task in plan:
    print(f"- {task.description} ({task.time} min, priority {task.priority})")