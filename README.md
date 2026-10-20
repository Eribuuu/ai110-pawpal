# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Features

- **Daily schedule across all pets**: `Scheduler.create_schedule()` collects every task, from every pet, that is due on the chosen day (today by default). Each one is labeled with the pet it belongs to.
- **Sorting by time**: tasks are sorted by start time. If two start at the same time, the higher-priority one goes first, then the shorter one. A single pet's task list is sorted by due date, then start time.
- **Filtering by pet and status**: `Scheduler.filter_tasks()` narrows the schedule to one pet (ignoring upper/lower case), to pending or completed tasks, or to both. The results stay in time order.
- **Conflict warnings**: `Scheduler.detect_conflicts()` compares every pair of tasks on the same day, across all pets, and warns about each pair whose times overlap. Back-to-back tasks don't count. It only warns and never moves or removes a task. Overlaps are checked in minutes, so a task that runs past midnight is still checked correctly.
- **Daily and weekly recurrence**: completing a daily task adds a new copy due the next day, and completing a weekly task adds one due 7 days later. One-off tasks don't repeat. Month and year rollovers are handled.
- **Completion guard**: completing a task that's already done raises a `ValueError` instead of quietly creating a duplicate next occurrence.

## Implementation Summary

The core logic lives in `pawpal_system.py`:

- **`Task`**: one occurrence of a care task, with a title, duration, priority, start time, due date, and frequency (once, daily, or weekly). `is_due_on(day)` checks whether it falls on a given day, `mark_complete()` marks it done, and `next_occurrence()` returns a copy due one day or one week later (or `None` for one-off tasks).
- **`Pet`**: holds a pet's tasks. You can add or remove tasks, get them sorted by date and start time, and print them as a list. `complete_task(task)` marks a task done and adds its next occurrence if it recurs.
- **`Owner`**: holds the owner's pets. `get_all_tasks()` returns every task across all pets, each paired with its pet.
- **`Scheduler`**: builds and prints the daily schedule.
- **`Schedule` / `ScheduledTask`**: hold the result. Each scheduled task keeps a link to its pet.

### How the classes interact

1. An `Owner` has many `Pet`s, and each `Pet` has many `Task`s.
2. The `Scheduler` never reads from a single pet. It calls `Owner.get_all_tasks()` to get every `(pet, task)` pair across all pets.
3. For each pair, the `Scheduler` asks the task whether it's due that day with `Task.is_due_on(day)`.
4. Each due task is wrapped in a `ScheduledTask` along with its `Pet`. That's how the schedule knows which pet each task belongs to.
5. The `ScheduledTask`s are sorted by start time and stored in a `Schedule`. `Scheduler.display_schedule()` then prints the `Schedule`.

```
Owner --has--> Pet --has--> Task
  |
  | get_all_tasks()
  v
Scheduler --create_schedule()--> Schedule --contains--> ScheduledTask (pet + task)
```

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule
================
07:00  Kiwi: Breakfast (5 min)
07:30  Mochi: Morning walk (30 min)
12:15  Kiwi: Brush fur (15 min)
17:30  Mochi: Dinner (10 min)
18:00  Mochi: Evening walk (30 min)
20:00  Kiwi: Clean litter box (10 min)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

### What the tests cover

- **Recurring tasks**: daily tasks repeat the next day, weekly tasks 7 days later, and one-off tasks don't repeat. Also covers month/year rollovers, and that completing a task twice raises an error.
- **Filtering**: by completed/pending, by pet name (ignores upper/lower case), or both. A blank filter returns everything.
- **Conflict detection**: overlapping times are flagged, while back-to-back tasks and tasks on different days are not.

Sample test output:

```
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.7.0
collected 43 items

tests/test_pawpal.py ...........................................   [100%]

43 passed in 0.19s
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Pet.get_tasks()` | Tasks are ordered by start time. When two start at the same time, the higher-priority one goes first, then the shorter one. `create_schedule()` sorts automatically. |
| Filtering | `Scheduler.filter_tasks()` | Filters by completion status (`completed=True/False`), by pet name (`pet_name=`, ignores upper/lower case), or both. Leaving a filter out (or passing a blank name) skips it. The original order is kept, so results stay sorted by time. |
| Conflict handling | `Scheduler.detect_conflicts()` | Checks every pair of same-day tasks for overlapping times, across all pets, and returns one warning per clash. It only warns and never moves or drops a task. Back-to-back tasks (one ends at 08:30, the next starts at 08:30) don't count as a conflict. Warnings appear in the CLI output and as `st.warning` in the app. |
| Recurring tasks | `Pet.complete_task()`, `Task.next_occurrence()` | Each `Task` is one occurrence with a `due_date`. Completing a daily task adds a copy due the next day, and a weekly task adds one due 7 days later. One-off tasks add nothing. Completing a task that's already done raises a `ValueError`. Tasks that aren't completed stay on their original date and don't carry forward. |

## Demo Walkthrough

Start the app with `streamlit run app.py`, or run the CLI demo with `python main.py`.

### Main UI features

- **Owner and pets**: set the owner's name, then add pets with a name and species (dog, cat, or other). The "Current pets" table shows each pet and how many tasks it has. A blank pet name shows an error.
- **Tasks**: choose a pet and add a task with a title, duration, priority (low/medium/high), start time, frequency (once/daily/weekly), and due date. Under the form, each pet's tasks are listed in a table sorted by date and start time, with end times filled in.
- **Build Schedule**: pick a day and click "Generate schedule". This builds one plan from every pet's tasks that are due on that day.
- **Filters**: narrow the schedule by pet ("All pets" or one pet) and by status (All, Pending, Done). A summary line shows how many tasks are shown and their total minutes.
- **Mark complete**: choose a pending task from the dropdown and click "Complete". A message confirms it, and for a recurring task it also gives the date the next one is due.

### Example workflow

1. Enter an owner name, add a dog named Mochi, then add a cat named Kiwi.
2. Choose Mochi and add "Dinner": 10 minutes, medium priority, 17:30, daily, due today.
3. Choose Kiwi and add "Play time": 15 minutes, low priority, 17:35, once, due today.
4. Under "Build Schedule", leave the day set to today and click "Generate schedule". Both tasks appear in start-time order, each labeled with its pet. Above the table, a warning says that Dinner (17:30-17:40) overlaps Play time (17:35-17:50).
5. Set the pet filter to "Kiwi" to see only Kiwi's tasks. Then set the status filter to "Pending" to hide anything already done.
6. Mark Mochi's Dinner complete. The message says the next one is due tomorrow. Change the schedule day to tomorrow, and Dinner appears there, but the one-off Play time does not.

### Key scheduler behaviors shown

- **Sorting by time**: tasks are added out of order, but the schedule always lists them by start time. If two start at the same time, the higher-priority one goes first, then the shorter one.
- **Multiple pets in one plan**: one schedule combines Mochi's and Kiwi's tasks, and every row is labeled with its pet.
- **Conflict warnings**: overlapping tasks are flagged even when they belong to different pets. The warning doesn't move or remove anything.
- **Filtering**: filtering by pet and by status can be combined, and the results stay in time order.
- **Recurrence**: completing a daily or weekly task creates its next occurrence. A task that hasn't been completed doesn't carry over to the next day.

### Sample CLI output (`python main.py`)

The script sets up Mochi (dog) and Kiwi (cat) with seven tasks, one of which clashes on purpose. It prints today's schedule, completes two tasks, shows four filtered views, and then shows tomorrow's schedule:

```
Today's Schedule
================
07:00  Kiwi: Breakfast (5 min)
07:30  Mochi: Morning walk (30 min)
12:15  Kiwi: Brush fur (15 min)
17:30  Mochi: Dinner (10 min)
17:35  Kiwi: Play time (15 min)
18:00  Mochi: Evening walk (30 min)
20:00  Kiwi: Clean litter box (10 min)
WARNING: Conflict: Mochi's Dinner (17:30-17:40) overlaps Kiwi's Play time (17:35-17:50)

Mochi's tasks
-------------
07:30  Mochi: Morning walk (30 min)
17:30  Mochi: Dinner (10 min)
18:00  Mochi: Evening walk (30 min)

Completed
---------
07:00  Kiwi: Breakfast (5 min)
07:30  Mochi: Morning walk (30 min)

Still to do
-----------
12:15  Kiwi: Brush fur (15 min)
17:30  Mochi: Dinner (10 min)
17:35  Kiwi: Play time (15 min)
18:00  Mochi: Evening walk (30 min)
20:00  Kiwi: Clean litter box (10 min)

Kiwi, still to do
-----------------
12:15  Kiwi: Brush fur (15 min)
17:35  Kiwi: Play time (15 min)
20:00  Kiwi: Clean litter box (10 min)

Tomorrow's Schedule
===================
07:00  Kiwi: Breakfast (5 min)
07:30  Mochi: Morning walk (30 min)
```

Only Breakfast and Morning walk show up tomorrow, because they're the only tasks completed today. The other daily tasks stay on today's date until they're done.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
