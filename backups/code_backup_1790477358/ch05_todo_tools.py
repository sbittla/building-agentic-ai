"""Chapter 5: an agent with state that survives restarts (tasks.json)."""
import json
from datetime import date
from pathlib import Path

STORE = Path("tasks.json")

def _load() -> dict:
    if STORE.exists():
        return json.loads(STORE.read_text())
    return {"next_id": 1, "tasks": []}

def _save(data: dict) -> None:
    tmp = STORE.with_suffix(".tmp")          # write-then-rename: never half-written
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(STORE)

def add_task(title: str, due: str | None = None, priority: str = "normal") -> str:
    data = _load()
    for t in data["tasks"]:                  # idempotent: no duplicate open tasks
        if t["title"].lower() == title.lower() and not t["done"]:
            return f"Already exists: #{t['id']} {t['title']}"
    task = {"id": data["next_id"], "title": title, "due": due,
            "priority": priority, "done": False}
    data["tasks"].append(task)
    data["next_id"] += 1
    _save(data)
    return f"Added #{task['id']}: {title}"

def list_tasks(include_done: bool = False, due_before: str | None = None) -> str:
    tasks = [t for t in _load()["tasks"] if include_done or not t["done"]]
    if due_before:
        tasks = [t for t in tasks if t["due"] and t["due"] <= due_before]
    if not tasks:
        return "No matching tasks."
    return "\n".join(
        f"#{t['id']} [{'x' if t['done'] else ' '}] {t['title']}"
        f" (due {t['due'] or '-'}, {t['priority']})" for t in tasks)

def find_tasks(text: str) -> str:
    hits = [t for t in _load()["tasks"]
            if text.lower() in t["title"].lower() and not t["done"]]
    return json.dumps(hits) if hits else "No open task matches."

def complete_task(task_id: int) -> str:
    data = _load()
    for t in data["tasks"]:
        if t["id"] == task_id:
            if t["done"]:
                return f"#{task_id} was already done."
            t["done"] = True
            _save(data)
            return f"Completed #{task_id}: {t['title']}"
    return f"ERROR: no task with id {task_id}. Use find_tasks to get ids."

def today() -> str:
    return date.today().isoformat()

REGISTRY = {"add_task": add_task, "list_tasks": list_tasks, "find_tasks": find_tasks,
            "complete_task": complete_task, "today": today}

TOOLS = [
    {"name": "add_task", "description": "Add a to-do. Dates are YYYY-MM-DD.",
     "input_schema": {"type": "object", "properties": {
         "title": {"type": "string"}, "due": {"type": "string"},
         "priority": {"type": "string", "enum": ["low", "normal", "high"]}},
         "required": ["title"]}},
    {"name": "list_tasks", "description": "List open tasks, optionally only those "
     "due on or before a date.", "input_schema": {"type": "object", "properties": {
         "include_done": {"type": "boolean"}, "due_before": {"type": "string"}}}},
    {"name": "find_tasks", "description": "Find open tasks whose title contains text. "
     "Use this to get a task's id before completing it.",
     "input_schema": {"type": "object", "properties": {"text": {"type": "string"}},
                      "required": ["text"]}},
    {"name": "complete_task", "description": "Mark a task done by its numeric id. "
     "If several tasks could match the user's words, ask the user which one first.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"}},
                      "required": ["task_id"]}},
    {"name": "today", "description": "Today's date (YYYY-MM-DD).",
     "input_schema": {"type": "object", "properties": {}}},
]

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

if __name__ == "__main__":
    from ch04_agent import run_agent
    system = ("You manage the user's to-do list. Always use the tools; never "
              "invent tasks. Resolve relative dates with the today tool.")
    history = []
    while (q := input("You: ")) not in ("quit", "exit"):
        answer, history, _ = run_agent(q, TOOLS, run_tool, system=system,
                                       messages=history)
        print("Agent:", answer)
