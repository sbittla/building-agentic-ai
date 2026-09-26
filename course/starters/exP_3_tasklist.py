from dataclasses import dataclass


@dataclass
class Task:
    id: int
    title: str
    due: str | None = None
    done: bool = False


class TaskList:
    def __init__(self):
        self.tasks: list[Task] = []

    def add(self, title: str, due: str | None = None) -> int:
        """Add a task; return its id (1, 2, 3, ...)."""
        raise NotImplementedError

    def complete(self, task_id: int) -> bool:
        """Mark a task done. True if it existed, False otherwise."""
        raise NotImplementedError

    def open_tasks(self) -> list[str]:
        """Titles of tasks not done yet, oldest first."""
        raise NotImplementedError


if __name__ == "__main__":
    t = TaskList(); t.add("buy milk"); t.add("call bank", "2026-10-01"); t.complete(1)
    print(t.open_tasks())                                  # ['call bank']
