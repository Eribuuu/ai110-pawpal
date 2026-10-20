from datetime import date, time

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


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

    scheduler = Scheduler()
    schedule = scheduler.create_schedule(owner)

    print("Today's Schedule")
    print("=" * 16)
    print(scheduler.display_schedule(schedule))


if __name__ == "__main__":
    main()
