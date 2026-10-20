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
    def create_schedule(self, owner: Owner, day: date) -> Schedule:
        """Pick the tasks due by frequency, order them by start time, and skip lower-priority tasks that overlap."""
        pass
