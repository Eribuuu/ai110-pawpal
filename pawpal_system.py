from dataclasses import dataclass, field, replace
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
    frequency: Frequency  # how far ahead the next occurrence is created once this one is completed
    due_date: date  # the day this occurrence happens
    completed: bool = False

    @property
    def end_time(self) -> time:
        """The time this task finishes, from its start time plus duration."""
        start = datetime.combine(date.today(), self.start_time)
        return (start + timedelta(minutes=self.duration_minutes)).time()

    def is_due_on(self, day: date) -> bool:
        """Whether this occurrence happens on the given day."""
        return day == self.due_date

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """A fresh copy due one day (DAILY) or one week (WEEKLY) later; None for ONCE."""
        if self.frequency is Frequency.ONCE:
            return None
        step = timedelta(days=1 if self.frequency is Frequency.DAILY else 7)
        return replace(self, due_date=self.due_date + step, completed=False)


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task done and, if it recurs, add its next occurrence; returns that new task."""
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            self.add_task(upcoming)
        return upcoming

    def get_tasks(self, day: date | None = None) -> list[Task]:
        """This pet's tasks ordered by date then start time; only those due on `day` if one is given."""
        tasks = self.tasks if day is None else [t for t in self.tasks if t.is_due_on(day)]
        return sorted(tasks, key=lambda t: (t.due_date, t.start_time))

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
        """Total minutes of all scheduled tasks."""
        return sum(s.task.duration_minutes for s in self.scheduled)


class Owner:
    def __init__(self, name: str):
        """Create an owner with a name and no pets."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
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
        schedule.scheduled = self.sort_by_time(schedule.scheduled)
        return schedule

    def sort_by_time(self, scheduled: list[ScheduledTask]) -> list[ScheduledTask]:
        """Order tasks by start time; ties go to higher priority, then shorter duration."""
        return sorted(
            scheduled,
            key=lambda s: (s.task.start_time, -s.task.priority.value, s.task.duration_minutes),
        )

    def filter_tasks(
        self,
        scheduled: list[ScheduledTask],
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[ScheduledTask]:
        """Keep tasks matching the given completion status and/or pet name (case-insensitive); None means don't filter."""
        return [
            s for s in scheduled
            if (completed is None or s.task.completed == completed)
            and (pet_name is None or s.pet.name.lower() == pet_name.lower())
        ]

    def detect_conflicts(self, scheduled: list[ScheduledTask]) -> list[str]:
        """A warning for each pair of tasks whose time slots overlap; never changes the schedule."""
        def minutes(s: ScheduledTask) -> tuple[int, int]:
            # Plain minutes rather than end_time, so a task running past midnight doesn't wrap to 00:xx
            start = s.task.start_time.hour * 60 + s.task.start_time.minute
            return start, start + s.task.duration_minutes

        warnings = []
        for i, a in enumerate(scheduled):
            a_start, a_end = minutes(a)
            for b in scheduled[i + 1:]:
                b_start, b_end = minutes(b)
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"Conflict: {a.pet.name}'s {a.task.title} ({a.task.start_time:%H:%M}-{a.task.end_time:%H:%M}) "
                        f"overlaps {b.pet.name}'s {b.task.title} ({b.task.start_time:%H:%M}-{b.task.end_time:%H:%M})"
                    )
        return warnings

    def display_schedule(self, schedule: Schedule) -> str:
        """One line per task, showing which pet it belongs to."""
        if not schedule.scheduled:
            return "No tasks scheduled."
        return "\n".join(
            f"{s.task.start_time:%H:%M}  {s.pet.name}: {s.task.title} ({s.task.duration_minutes} min)"
            for s in schedule.scheduled
        )
