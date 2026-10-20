from datetime import date, time, timedelta

from pawpal_system import Frequency, Owner, Pet, Priority, Schedule, Scheduler, Task


def main():
    today = date.today()

    owner = Owner("Eris")
    mochi = Pet("Mochi", "dog")
    kiwi = Pet("Kiwi", "cat")
    owner.add_pet(mochi)
    owner.add_pet(kiwi)

    mochi.add_task(Task("Morning walk", 30, Priority.HIGH, time(7, 30), Frequency.DAILY, today))
    mochi.add_task(Task("Evening walk", 30, Priority.HIGH, time(18, 0), Frequency.DAILY, today))
    kiwi.add_task(Task("Breakfast", 5, Priority.HIGH, time(7, 0), Frequency.DAILY, today))
    mochi.add_task(Task("Dinner", 10, Priority.MEDIUM, time(17, 30), Frequency.DAILY, today))
    kiwi.add_task(Task("Brush fur", 15, Priority.LOW, time(12, 15), Frequency.WEEKLY, today))
    kiwi.add_task(Task("Clean litter box", 10, Priority.MEDIUM, time(20, 0), Frequency.DAILY, today))
    kiwi.add_task(Task("Play time", 15, Priority.LOW, time(17, 35), Frequency.ONCE, today))  # clashes with Dinner

    scheduler = Scheduler()
    schedule = scheduler.create_schedule(owner)

    print("Today's Schedule")
    print("=" * 16)
    print(scheduler.display_schedule(schedule))
    for warning in scheduler.detect_conflicts(schedule.scheduled):
        print(f"WARNING: {warning}")

    # Finish a couple of tasks so the completion filter has something to show
    # complete_task also queues up the next occurrence of these daily tasks
    mochi.complete_task(mochi.tasks[0])  # Morning walk
    kiwi.complete_task(kiwi.tasks[0])    # Breakfast

    filters = [
        ("Mochi's tasks", {"pet_name": "mochi"}),
        ("Completed", {"completed": True}),
        ("Still to do", {"completed": False}),
        ("Kiwi, still to do", {"completed": False, "pet_name": "Kiwi"}),
    ]
    for title, kwargs in filters:
        filtered = scheduler.filter_tasks(schedule.scheduled, **kwargs)
        print()
        print(title)
        print("-" * len(title))
        print(scheduler.display_schedule(Schedule(scheduled=filtered)))

    # Only the tasks completed today have rolled over to tomorrow
    print()
    print("Tomorrow's Schedule")
    print("=" * 19)
    print(scheduler.display_schedule(scheduler.create_schedule(owner, today + timedelta(days=1))))


if __name__ == "__main__":
    main()
