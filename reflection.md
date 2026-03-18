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

My scheduler currently considers three main constraints: (1) owner available time budget, (2) task priority, and (3) recurrence/day rules (daily tasks always eligible, weekly tasks filtered by day). It also includes lightweight conflict checks that warn when tasks share the same scheduled time. I prioritized available time and priority first because they directly affect whether a daily plan is realistic and useful to a busy pet owner. Recurrence and conflict warnings are layered on top so the schedule stays practical without becoming overly complex.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff in my scheduler is conflict detection: it only checks for exact time-string matches (for example, two tasks both at 08:00) instead of calculating partial overlaps between durations (for example, 08:00-08:30 overlapping with 08:15-08:45). I reviewed a more Pythonic approach that builds richer time intervals and checks every pair, which is more complete but harder to read for this project stage. I kept the simpler exact-match warning method because it is lightweight, easy to explain, and gives useful feedback without making the app brittle or overly complex for a beginner-friendly pet planning scenario.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

VS Code Copilot was most effective for turning high-level requirements into incremental implementation steps. I used it to draft class skeletons from UML, generate method stubs, suggest test cases, and refactor display logic in Streamlit to show sorted/filtered tasks and warnings clearly. The most helpful prompts were specific and code-anchored, such as asking how Scheduler should retrieve tasks from Owner, how to sort HH:MM strings with lambda keys, and how to design lightweight conflict detection that returns warnings instead of failing.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One example I did not accept as-is was a suggestion to use more advanced interval-based conflict detection for overlapping task durations. While technically stronger, it added complexity that was harder to explain and maintain for this project scope. I chose a simpler exact time-match warning strategy and verified it with targeted tests plus terminal demos to confirm it produced useful user-facing warnings without breaking plan generation.

Using separate Copilot chat sessions for different phases (design, implementation, testing, and reflection) helped me stay organized and reduced context mixing. I could focus each chat on one goal, which made prompts more precise and made it easier to evaluate AI output against phase-specific requirements.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested three core behaviors with pytest: chronological sorting correctness, recurrence logic for daily tasks, and conflict detection for duplicate times. These tests are important because they validate the scheduler's key promises to the user: ordering tasks correctly, automatically handling recurring care, and warning about schedule issues before execution.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

My confidence level is 4/5 based on a passing automated suite and manual UI/terminal verification of core flows. With more time, I would test additional edge cases such as overlapping-duration conflicts (not just exact same-time matches), malformed time strings, large multi-pet task sets, and recurrence behavior across week boundaries.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with evolving the project from a simple class skeleton into a working system with reusable scheduler methods, automated tests, and a Streamlit interface that clearly presents plans and warnings.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

In another iteration, I would redesign conflict handling to support real interval overlap detection, add editable task start times in the UI, and improve planner flexibility by allowing users to switch between priority-first and time-first scheduling policies in one place.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

My key takeaway is that the developer must stay the lead architect when using powerful AI tools: AI can accelerate coding and brainstorming, but strong outcomes come from setting clear constraints, validating suggestions with tests, and choosing designs that balance correctness, clarity, and maintainability for the actual project context.
