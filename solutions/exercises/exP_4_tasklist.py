"""Exercise P.4 (solution): a class of your own."""
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

    def add(self, title, due=None) -> int:
        task = Task(len(self.tasks) + 1, title, due)
        self.tasks.append(task)
        return task.id

    def complete(self, task_id) -> bool:
        for t in self.tasks:
            if t.id == task_id:
                t.done = True
                return True
        return False

    def open_tasks(self) -> list[str]:
        return [t.title for t in self.tasks if not t.done]

if __name__ == "__main__":
    t = TaskList(); t.add("buy milk"); t.add("call bank"); t.complete(1); print(t.open_tasks())
