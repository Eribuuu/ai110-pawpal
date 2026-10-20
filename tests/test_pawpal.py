from datetime import date, time, timedelta

from pawpal_system import Frequency, Pet, Priority, Scheduler, ScheduledTask, Task


def make_task(title="Walk", frequency=Frequency.DAILY, start=time(8, 0), duration=30):
    return Task(title, duration, Priority.MEDIUM, start, frequency, date.today())


def test_mark_complete_sets_completed():
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(make_task())

    assert len(pet.tasks) == 1


def test_completing_daily_task_adds_one_for_tomorrow():
    pet = Pet("Mochi", "dog")
    task = make_task()
    pet.add_task(task)

    upcoming = pet.complete_task(task)

    assert task.completed is True
    assert upcoming is not None
    assert upcoming in pet.tasks
    assert upcoming.due_date == date.today() + timedelta(days=1)
    assert upcoming.completed is False
    assert upcoming.title == task.title


def test_completing_weekly_task_adds_one_for_next_week():
    pet = Pet("Mochi", "dog")
    task = make_task(frequency=Frequency.WEEKLY)
    pet.add_task(task)

    upcoming = pet.complete_task(task)

    assert upcoming is not None
    assert upcoming.due_date == date.today() + timedelta(days=7)


def test_completing_once_task_adds_nothing():
    pet = Pet("Mochi", "dog")
    task = make_task(frequency=Frequency.ONCE)
    pet.add_task(task)

    assert pet.complete_task(task) is None
    assert pet.tasks == [task]


def test_daily_task_only_due_tomorrow_after_completion():
    pet = Pet("Mochi", "dog")
    task = make_task()
    pet.add_task(task)
    tomorrow = date.today() + timedelta(days=1)

    assert pet.get_tasks(date.today()) == [task]
    assert pet.get_tasks(tomorrow) == []

    pet.complete_task(task)

    assert len(pet.get_tasks(tomorrow)) == 1


def test_detect_conflicts_warns_on_overlap_across_pets():
    mochi, kiwi = Pet("Mochi", "dog"), Pet("Kiwi", "cat")
    scheduled = [
        ScheduledTask(mochi, make_task("Walk", start=time(8, 0), duration=30), "due daily"),
        ScheduledTask(kiwi, make_task("Breakfast", start=time(8, 15), duration=10), "due daily"),
    ]

    warnings = Scheduler().detect_conflicts(scheduled)

    assert len(warnings) == 1
    assert "Mochi's Walk" in warnings[0] and "Kiwi's Breakfast" in warnings[0]


def test_detect_conflicts_allows_back_to_back_tasks():
    pet = Pet("Mochi", "dog")
    scheduled = [
        ScheduledTask(pet, make_task("Walk", start=time(8, 0), duration=30), "due daily"),
        ScheduledTask(pet, make_task("Breakfast", start=time(8, 30), duration=10), "due daily"),
    ]

    assert Scheduler().detect_conflicts(scheduled) == []
