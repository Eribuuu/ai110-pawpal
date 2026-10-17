from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Pet:
    name: str
    species: str


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    pet: Pet
    completed: bool = False


@dataclass
class ScheduledTask:
    task: Task
    start_minute: int  # minutes from the start of the owner's free time
    reason: str  # why the task was chosen

    @property
    def end_minute(self) -> int:
        return self.start_minute + self.task.duration_minutes


@dataclass
class Schedule:
    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[tuple[Task, str]] = field(default_factory=list)  # (task, why it was skipped)

    @property
    def total_minutes(self) -> int:
        return sum(s.task.duration_minutes for s in self.scheduled)


class Owner:
    def __init__(self, name: str, free_time_minutes: int):
        self.name = name
        self.free_time_minutes = free_time_minutes
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet along with all of its tasks."""
        self.pets.remove(pet)
        self.tasks = [t for t in self.tasks if t.pet is not pet]

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)

    def get_tasks_for(self, pet: Pet) -> list[Task]:
        return [t for t in self.tasks if t.pet is pet]


class Scheduler:
    def create_schedule(self, owner: Owner) -> Schedule:
        pass
