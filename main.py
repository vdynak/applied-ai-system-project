from pawpal_system import Owner, Pet, Task, Scheduler

# Create an Owner
owner = Owner("Alice", {"prefers_morning": True}, 90)  # 90 minutes available time

# Create at least two Pets
pet1 = Pet("Max", "dog", 5, [])
pet2 = Pet("Luna", "cat", 3, [])

# Add pets to owner
owner.add_pet(pet1)
owner.add_pet(pet2)

# Create tasks (including two at the same time to test conflict detection)
task1 = Task("Morning walk", "08:00", 5, "walk", "daily")
task2 = Task("Feed breakfast", "08:00", 4, "feed", "daily")  # Same time as task1
task3 = Task("Play session", "09:15", 3, "play", "daily")
task4 = Task("Evening walk", "18:30", 4, "walk", "daily")

# Add tasks to pets
pet1.add_task(task1)
pet1.add_task(task4)  # Add out of order
pet2.add_task(task2)
pet2.add_task(task3)

# Create Scheduler and generate plan
scheduler = Scheduler()
plan = scheduler.generate_plan(owner)

# Print Today's Schedule
print("Today's Schedule:")
for task in plan:
    print(f"- {task.description} ({task.time}, priority {task.priority})")

# Demonstrate completing a task and auto-creating the next occurrence
print("\nMarking the first task complete (recurring tasks will auto-recreate):")
next_task = task1.mark_complete()
if next_task:
    pet1.add_task(next_task)
    print(f"Created next occurrence due on {next_task.due_date}")

# Demonstrate sorting by time
print("\nTasks sorted by time:")
sorted_tasks = scheduler.sort_by_time(owner.get_all_tasks())
for task in sorted_tasks:
    print(f"- {task.description} ({task.time}, priority {task.priority})")

# Demonstrate filtering by pet
print("\nTasks for Max:")
max_tasks = scheduler.get_tasks_for_pet(owner, "Max")
for task in max_tasks:
    print(f"- {task.description} ({task.time}, priority {task.priority})")

# Demonstrate filtering by status
print("\nIncomplete tasks:")
incomplete = scheduler.get_incomplete_tasks(owner)
for task in incomplete:
    print(f"- {task.description} ({task.time}, priority {task.priority})")

# Demonstrate lightweight same-time conflict detection
print("\nSchedule conflict warnings:")
warnings = scheduler.detect_time_conflicts(owner)
if warnings:
    for warning in warnings:
        print(f"- {warning}")
else:
    print("- No time conflicts detected.")