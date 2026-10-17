from dataclasses import dataclass


@dataclass
class Pet:
    name: str
    species: str


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    pet: Pet
    completed: bool = False


class Owner:
    def __init__(self, name: str, free_time_minutes: int):
        self.name = name
        self.free_time_minutes = free_time_minutes
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass


class Scheduler:
    def create_schedule(self, owner: Owner) -> list[Task]:
        pass
