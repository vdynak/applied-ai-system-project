# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The initial UML design includes four classes: Owner, Pet, Task, and Scheduler. The Owner class represents the pet owner and manages their profile, including name, preferences, available time, and a list of pets. It has methods to add pets and update preferences. The Pet class represents individual pets with attributes like name, type, age, and a list of associated tasks, and includes a method to add tasks. The Task class is a simple data holder for care tasks, with attributes for name, duration, priority, and type. The Scheduler class handles the core logic for generating daily plans, with methods to create a plan based on the owner and consider constraints like time and priorities.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the design changed slightly during implementation. Initially, the methods in the Owner and Pet classes were left as empty stubs. After reviewing the skeleton, I implemented the add_task method in Pet to append tasks to the list, add_pet in Owner to append pets, and set_preferences to update the preferences dictionary. This was done to make the classes functional for basic operations, ensuring the relationships (Owner has Pets, Pet has Tasks) are properly maintained without adding unnecessary complexity.

**c. Core User Actions**

Based on the project requirements outlined in the README, the three core actions a user should be able to perform with PawPal+ are:

1. Enter basic owner and pet information to establish their profile and preferences.
2. Add or edit pet care tasks, specifying details such as duration and priority for each task.
3. Generate and view a daily schedule or plan that organizes tasks considering time constraints, priorities, and owner preferences.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff in my scheduler is conflict detection: it only checks for exact time-string matches (for example, two tasks both at 08:00) instead of calculating partial overlaps between durations (for example, 08:00-08:30 overlapping with 08:15-08:45). I reviewed a more Pythonic approach that builds richer time intervals and checks every pair, which is more complete but harder to read for this project stage. I kept the simpler exact-match warning method because it is lightweight, easy to explain, and gives useful feedback without making the app brittle or overly complex for a beginner-friendly pet planning scenario.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
