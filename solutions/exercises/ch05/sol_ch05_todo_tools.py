"""Chapter 5 reference solution: exercises 5.4 (delete, rename) and 5.5 (overdue)."""
import ch05_todo_tools as base
from ch05_todo_tools import _load, _save, add_task, list_tasks, find_tasks, complete_task, today

def delete_task(task_id: int) -> str:
    data = _load()
    before = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    if len(data["tasks"]) == before:
        return f"#{task_id} does not exist (already deleted?)."     # idempotent
    _save(data)
    return f"Deleted #{task_id}."

def rename_task(task_id: int, new_title: str) -> str:
    data = _load()
    for t in data["tasks"]:
        if t["id"] == task_id:
            old, t["title"] = t["title"], new_title
            _save(data)
            return f"Renamed #{task_id}: '{old}' -> '{new_title}'"
    return f"ERROR: no task with id {task_id}. Use find_tasks to get ids."

def overdue_tasks() -> str:
    """Open tasks whose due date is before today."""
    now = today()
    late = [t for t in _load()["tasks"] if not t["done"] and t["due"] and t["due"] < now]
    return "\n".join(f"#{t['id']} {t['title']} (was due {t['due']})" for t in late) \
        or "Nothing overdue."

REGISTRY = {**base.REGISTRY, "delete_task": delete_task, "rename_task": rename_task,
            "overdue_tasks": overdue_tasks}
TOOLS = base.TOOLS + [
    {"name": "delete_task", "description": "Delete a task by id (use find_tasks first).",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"}},
                      "required": ["task_id"]}},
    {"name": "rename_task", "description": "Change a task's title by id.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"},
                      "new_title": {"type": "string"}}, "required": ["task_id", "new_title"]}},
    {"name": "overdue_tasks", "description": "Open tasks that are past their due date.",
     "input_schema": {"type": "object", "properties": {}}},
]
SYSTEM = ("You manage the user's to-do list. Always use the tools; never invent tasks. "
          "For 'this week', call today and pass due_before = the coming Sunday. "
          "If several tasks match the user's words, ask which one before changing anything.")

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"
