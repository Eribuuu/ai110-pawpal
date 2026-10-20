from datetime import date, time, timedelta

import pytest

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, ScheduledTask, Task

# A fixed day keeps results independent of when the tests run
DAY = date(2026, 1, 15)


def make_task(title="Walk", frequency=Frequency.DAILY, start=time(8, 0), duration=30, due=DAY, completed=False):
    return Task(title, duration, Priority.MEDIUM, start, frequency, due, completed)


def next_of(task):
    upcoming = task.next_occurrence()
    assert upcoming is not None
    return upcoming


def complete(pet, task):
    upcoming = pet.complete_task(task)
    assert upcoming is not None
    return upcoming


def make_scheduled(pet, title="Walk", start=time(8, 0), duration=30, completed=False, due=DAY):
    return ScheduledTask(pet, make_task(title, start=start, duration=duration, due=due, completed=completed), "due daily")


# --- Basics ---

def test_mark_complete_sets_completed():
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_mark_complete_twice_raises():
    task = make_task()
    task.mark_complete()

    with pytest.raises(ValueError, match="already completed"):
        task.mark_complete()


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(make_task())

    assert len(pet.tasks) == 1


# --- Recurring events ---

def test_completing_daily_task_adds_one_for_tomorrow():
    pet = Pet("Mochi", "dog")
    task = make_task()
    pet.add_task(task)

    upcoming = pet.complete_task(task)

    assert task.completed is True
    assert upcoming is not None
    assert upcoming in pet.tasks
    assert upcoming.due_date == DAY + timedelta(days=1)
    assert upcoming.completed is False
    assert upcoming.title == task.title


def test_completing_weekly_task_adds_one_for_next_week():
    pet = Pet("Mochi", "dog")
    task = make_task(frequency=Frequency.WEEKLY)
    pet.add_task(task)

    upcoming = pet.complete_task(task)

    assert upcoming is not None
    assert upcoming.due_date == DAY + timedelta(days=7)


def test_completing_once_task_adds_nothing():
    pet = Pet("Mochi", "dog")
    task = make_task(frequency=Frequency.ONCE)
    pet.add_task(task)

    assert pet.complete_task(task) is None
    assert pet.tasks == [task]


def test_next_occurrence_keeps_task_details():
    task = Task("Meds", 5, Priority.HIGH, time(21, 30), Frequency.WEEKLY, DAY)

    upcoming = next_of(task)

    assert (upcoming.title, upcoming.duration_minutes, upcoming.priority, upcoming.start_time, upcoming.frequency) == (
        "Meds", 5, Priority.HIGH, time(21, 30), Frequency.WEEKLY
    )


def test_next_occurrence_is_independent_of_original():
    pet = Pet("Mochi", "dog")
    task = make_task()
    pet.add_task(task)

    upcoming = complete(pet, task)
    upcoming.mark_complete()
    upcoming.title = "Long walk"

    assert upcoming is not task
    assert task.title == "Walk"


def test_completing_a_chain_of_daily_tasks():
    pet = Pet("Mochi", "dog")
    task = make_task()
    pet.add_task(task)

    day2 = complete(pet, task)
    day3 = complete(pet, day2)

    assert day3.due_date == DAY + timedelta(days=2)
    assert len(pet.tasks) == 3


def test_late_completion_schedules_from_due_date_not_completion_day():
    # Yesterday's walk finished late is followed by today's walk, not tomorrow's
    yesterday = DAY - timedelta(days=1)
    task = make_task(due=yesterday)

    assert next_of(task).due_date == DAY


@pytest.mark.parametrize("frequency, due, expected", [
    (Frequency.DAILY, date(2026, 1, 31), date(2026, 2, 1)),
    (Frequency.DAILY, date(2026, 12, 31), date(2027, 1, 1)),
    (Frequency.WEEKLY, date(2026, 12, 28), date(2027, 1, 4)),
])
def test_recurrence_crosses_month_and_year_boundaries(frequency, due, expected):
    assert next_of(make_task(frequency=frequency, due=due)).due_date == expected


def test_completing_already_completed_task_raises_and_adds_nothing():
    pet = Pet("Mochi", "dog")
    task = make_task()
    pet.add_task(task)
    pet.complete_task(task)

    with pytest.raises(ValueError, match="already completed"):
        pet.complete_task(task)

    assert len(pet.tasks) == 2  # the original plus one next occurrence, no duplicate


def test_daily_task_only_due_tomorrow_after_completion():
    pet = Pet("Mochi", "dog")
    task = make_task()
    pet.add_task(task)
    tomorrow = DAY + timedelta(days=1)

    assert pet.get_tasks(DAY) == [task]
    assert pet.get_tasks(tomorrow) == []

    pet.complete_task(task)

    assert len(pet.get_tasks(tomorrow)) == 1


def test_tomorrows_schedule_includes_next_occurrence():
    owner = Owner("Sam")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    task = make_task()
    pet.add_task(task)

    pet.complete_task(task)
    tomorrow = Scheduler().create_schedule(owner, DAY + timedelta(days=1))

    assert [s.task.title for s in tomorrow.scheduled] == ["Walk"]
    assert tomorrow.scheduled[0].task.completed is False


# --- Filtering ---

@pytest.fixture
def mixed_schedule():
    """Mochi and Kiwi each have one done and one pending task."""
    mochi, kiwi = Pet("Mochi", "dog"), Pet("Kiwi", "cat")
    return [
        make_scheduled(mochi, "Walk", time(8, 0), completed=True),
        make_scheduled(kiwi, "Breakfast", time(8, 30), completed=True),
        make_scheduled(mochi, "Dinner", time(18, 0)),
        make_scheduled(kiwi, "Litter", time(19, 0)),
    ]


def titles(scheduled):
    return [s.task.title for s in scheduled]


def test_filter_completed_only(mixed_schedule):
    assert titles(Scheduler().filter_tasks(mixed_schedule, completed=True)) == ["Walk", "Breakfast"]


def test_filter_pending_only(mixed_schedule):
    assert titles(Scheduler().filter_tasks(mixed_schedule, completed=False)) == ["Dinner", "Litter"]


def test_filter_by_pet_name(mixed_schedule):
    assert titles(Scheduler().filter_tasks(mixed_schedule, pet_name="Mochi")) == ["Walk", "Dinner"]


def test_filter_by_pet_and_status(mixed_schedule):
    assert titles(Scheduler().filter_tasks(mixed_schedule, completed=False, pet_name="Kiwi")) == ["Litter"]


@pytest.mark.parametrize("name", ["mochi", "MOCHI", "mOcHi"])
def test_filter_pet_name_is_case_insensitive(mixed_schedule, name):
    assert titles(Scheduler().filter_tasks(mixed_schedule, pet_name=name)) == ["Walk", "Dinner"]


@pytest.mark.parametrize("name", [None, ""])
def test_filter_with_no_criteria_returns_everything_in_order(mixed_schedule, name):
    assert Scheduler().filter_tasks(mixed_schedule, pet_name=name) == mixed_schedule


def test_filter_unknown_pet_returns_empty(mixed_schedule):
    assert Scheduler().filter_tasks(mixed_schedule, pet_name="Rex") == []


def test_filter_empty_list_returns_empty():
    assert Scheduler().filter_tasks([], completed=True, pet_name="Mochi") == []


def test_filter_matches_every_pet_sharing_a_name():
    first, second = Pet("Max", "dog"), Pet("Max", "cat")
    scheduled = [make_scheduled(first, "Walk"), make_scheduled(second, "Brush", time(9, 0))]

    assert titles(Scheduler().filter_tasks(scheduled, pet_name="max")) == ["Walk", "Brush"]


# --- Conflict detection ---

def test_detect_conflicts_warns_on_overlap_across_pets():
    mochi, kiwi = Pet("Mochi", "dog"), Pet("Kiwi", "cat")
    scheduled = [
        make_scheduled(mochi, "Walk", time(8, 0), 30),
        make_scheduled(kiwi, "Breakfast", time(8, 15), 10),
    ]

    warnings = Scheduler().detect_conflicts(scheduled)

    assert len(warnings) == 1
    assert "Mochi's Walk" in warnings[0] and "Kiwi's Breakfast" in warnings[0]


@pytest.mark.parametrize("a, b", [
    ((time(8, 0), 30), (time(8, 15), 30)),   # partial overlap
    ((time(8, 0), 30), (time(8, 0), 10)),    # same start time
    ((time(8, 0), 60), (time(8, 15), 15)),   # one inside the other
    ((time(8, 15), 30), (time(8, 0), 30)),   # later task listed first
    ((time(8, 0), 30), (time(8, 29), 5)),    # one minute of overlap
])
def test_detect_conflicts_overlapping_slots(a, b):
    pet = Pet("Mochi", "dog")
    scheduled = [make_scheduled(pet, "A", *a), make_scheduled(pet, "B", *b)]

    assert len(Scheduler().detect_conflicts(scheduled)) == 1


@pytest.mark.parametrize("a, b", [
    ((time(8, 0), 30), (time(8, 30), 10)),   # back to back
    ((time(8, 0), 30), (time(9, 0), 10)),    # gap between them
    ((time(9, 0), 10), (time(8, 0), 30)),    # out of order, no overlap
])
def test_detect_conflicts_separate_slots(a, b):
    pet = Pet("Mochi", "dog")
    scheduled = [make_scheduled(pet, "A", *a), make_scheduled(pet, "B", *b)]

    assert Scheduler().detect_conflicts(scheduled) == []


def test_detect_conflicts_reports_each_overlapping_pair():
    pet = Pet("Mochi", "dog")
    scheduled = [
        make_scheduled(pet, "A", time(8, 0), 60),
        make_scheduled(pet, "B", time(8, 10), 30),
        make_scheduled(pet, "C", time(8, 20), 30),
    ]

    assert len(Scheduler().detect_conflicts(scheduled)) == 3


@pytest.mark.parametrize("count", [0, 1])
def test_detect_conflicts_needs_at_least_two_tasks(count):
    pet = Pet("Mochi", "dog")
    scheduled = [make_scheduled(pet)][:count]

    assert Scheduler().detect_conflicts(scheduled) == []


def test_detect_conflicts_task_running_past_midnight():
    pet = Pet("Mochi", "dog")
    scheduled = [
        make_scheduled(pet, "Night walk", time(23, 30), 60),
        make_scheduled(pet, "Meds", time(23, 45), 5),
    ]

    assert len(Scheduler().detect_conflicts(scheduled)) == 1


def test_detect_conflicts_ignores_tasks_on_different_days():
    pet = Pet("Mochi", "dog")
    scheduled = [
        make_scheduled(pet, "Walk", time(8, 0), due=DAY),
        make_scheduled(pet, "Walk", time(8, 0), due=DAY + timedelta(days=1)),
    ]

    assert Scheduler().detect_conflicts(scheduled) == []


def test_detect_conflicts_does_not_change_schedule():
    pet = Pet("Mochi", "dog")
    scheduled = [make_scheduled(pet, "A", time(8, 0)), make_scheduled(pet, "B", time(8, 15))]
    before = list(scheduled)

    Scheduler().detect_conflicts(scheduled)

    assert scheduled == before
