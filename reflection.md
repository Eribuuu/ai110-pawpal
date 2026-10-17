# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Core Tasks:
1. Owner needs to be able to add or remove a pet
2. Owner needs to be able to add or remove a task for a pet
3. Owner needs to be able to see todays tasks

Initial Classes:
1. Owner (Holds the data for the pets and tasks, who they belong to)
    - attributes:
        - name
        - pets (list)
        - tasks (list)
        - free time (in minutes)
    - methods:
        - add pet
        - remove pet
            1. When a pet is removed, also remove the tasks associated with it
        - add task
        - remove task
        - get tasks for specific pet (helper function)
2. Pet (Holds information on pets)
    - attributes:
        - name
        - species
    - methods:
        - None
3. Task (Holds information on each task)
    - attributes:
        - title (name of task)
        - duration
        - priority (will be an enum)
        - pet (the pet the task is tied to)
        - completed (boolean)
    - methods:
        - None
4. Scheduler (Creates schedule for the tasks)
    - attributes:
        - None
    - methods:
        - create schedule (creates schedule based on the tasks in the system)
5. ScheduledTask (Holds when and why a task was chosen to be scheduled)
    - attributes:
        - task (the task being scheduled)
        - start minute (minutes from the start of the owner's free time)
        - reason (why the task was chosen)
    - methods:
        - end minute (calculated from the start minute and the task's duration)
6. Schedule (Holds the result of creating a schedule)
    - attributes:
        - scheduled (list of scheduled tasks)
        - skipped (list of tasks that were skipped and why)
    - methods:
        - total minutes (total time of all scheduled tasks)

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
From AI feedback:

In UML phase:
1. added species attribute to pets
2. Changed task due_time attribute to a duration attribute and added a priority attribute
3. Added completed boolean to task 

Post First skeleton created:
1. Added a note to also delete the tasks associated with each pet that is removed by the remove pet function
2. Added a helper function to get the tasks associated with a specific pet
3. Added a note for the priority attribute to be an Enum for easier equality checks later
4. Added a scheduled task object that will bridge the gap for showing when and why a tasks is chosen to scheduled or skipped
5. Added a schedule object to hold the schedule of tasks to be displayed

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
