from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    start_time: time
    frequency: Frequency
    start_date: date  # ONCE: the only day; DAILY: first day; WEEKLY: sets the weekday
    completed: bool = False

    @property
    def end_time(self) -> time:
        start = datetime.combine(date.today(), self.start_time)
        return (start + timedelta(minutes=self.duration_minutes)).time()

    def is_due_on(self, day: date) -> bool:
        """Whether this task happens on the given day, based on its frequency."""
        if day < self.start_date:
            return False
        if self.frequency is Frequency.ONCE:
            return day == self.start_date
        if self.frequency is Frequency.WEEKLY:
            return day.weekday() == self.start_date.weekday()
        return True  # DAILY


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)

    def get_tasks(self, day: date | None = None) -> list[Task]:
        """This pet's tasks ordered by start time; only those due on `day` if one is given."""
        tasks = self.tasks if day is None else [t for t in self.tasks if t.is_due_on(day)]
        return sorted(tasks, key=lambda t: t.start_time)

    def display_tasks(self, day: date | None = None) -> str:
        """A readable list of this pet's tasks, one per line."""
        tasks = self.get_tasks(day)
        header = f"{self.name} ({self.species})"
        if not tasks:
            return f"{header}\n  No tasks."
        lines = [header]
        for t in tasks:
            check = "x" if t.completed else " "
            lines.append(
                f"  [{check}] {t.start_time:%H:%M}-{t.end_time:%H:%M}  {t.title}"
                f"  ({t.duration_minutes} min, {t.priority.name.lower()}, {t.frequency.value})"
            )
        return "\n".join(lines)


@dataclass
class ScheduledTask:
    pet: Pet
    task: Task
    reason: str  # why the task was chosen


@dataclass
class Schedule:
    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[tuple[Pet, Task, str]] = field(default_factory=list)  # (pet, task, why it was skipped)

    @property
    def total_minutes(self) -> int:
        return sum(s.task.duration_minutes for s in self.scheduled)


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet; its tasks go with it."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Every task across all pets, paired with the pet it belongs to."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    def create_schedule(self, owner: Owner, day: date | None = None) -> Schedule:
        """Gather every pet's tasks due on `day` (default today) from the owner, ordered by start time."""
        day = day or date.today()
        schedule = Schedule()
        for pet, task in owner.get_all_tasks():
            if task.is_due_on(day):
                schedule.scheduled.append(ScheduledTask(pet, task, f"due {task.frequency.value}"))
        schedule.scheduled.sort(key=lambda s: s.task.start_time)
        return schedule

    def display_schedule(self, schedule: Schedule) -> str:
        """One line per task, showing which pet it belongs to."""
        if not schedule.scheduled:
            return "No tasks scheduled."
        return "\n".join(
            f"{s.task.start_time:%H:%M}  {s.pet.name}: {s.task.title} ({s.task.duration_minutes} min)"
            for s in schedule.scheduled
        )
