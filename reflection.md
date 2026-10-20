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

Time handling refactor:
1. Removed the owner's free time budget; each task now has its own start time (datetime.time) and duration, with an end time calculated from the two
2. Added a frequency attribute to tasks (Enum: once, daily, weekly) so the scheduler can tell which tasks are due
3. Removed the start minute from the scheduled task object since the start and end times now come from the task itself
4. Added a start date to tasks so frequency has a reference point (once = only that date, daily = every day from then on, weekly = same weekday as the start date), plus an is_due_on helper the scheduler will use to pick a day's tasks

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Currently the constraints for the scheduler are time and priority. I decided that priority was the constraint that mattered most as it is defined by the user that they would want this task done
as soon as possible or before other tasks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Right now one tradeoff is that all conflicts happen based on any pet, no discrimination between pets. This is fine in this case because it is not implied that there will be multiple people handling these pets.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI to help with all aspects of the project. The most help was refactoring when seeing the requirements for the project.
The prompts that were most helpful were the prompts that asked for feedback on design choices. Keeping claude in manual mode allowed for better implementations and rejections

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment where I did not accept a suggestion from claude was when it tried to one-shot the scheduler implementation. It was going beyond what was being asked for the current step of the project.
It was adding helper functions and also trying to implement algorithms before I indicated that I wanted to add that feature.
I evaluated the suggestion by reading the code that was generated and deciding that this was beyond the scope of what I needed at the moment.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the algorithm features. I tested these because these were the most complicated features in the project and not as simple to look at and see if they work as intended from main.
These tests were important becasue it solidifed what functionality was being completed by those features.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I would say a 4, I wasn't able to test the entirety of the system such as all the classes and methods made prior.
I would test invalid inputs in my dataclasses.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
