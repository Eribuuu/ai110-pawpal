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

## Implementation Summary

The core logic lives in `pawpal_system.py`:

- **`Task`**: a care task with a title, duration, priority, start time, and frequency (once, daily, or weekly). `is_due_on(day)` checks whether it happens on a given day, and `mark_complete()` marks it done.
- **`Pet`**: holds a pet's tasks. You can add or remove tasks, get them sorted by start time, and print them as a list.
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

`main.py` builds a sample owner with two pets and prints today's schedule. `tests/test_pawpal.py` checks that `mark_complete()` works and that `add_task()` grows a pet's task list.

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

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
