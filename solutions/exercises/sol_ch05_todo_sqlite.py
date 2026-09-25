"""Exercise 5.7 (Complex): the same to-do tools on SQLite, plus a JSON migration."""
import json
import sqlite3
from datetime import date
from pathlib import Path

DB = Path("tasks.db")

def _con():
    con = sqlite3.connect(DB, timeout=10)
    con.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, due TEXT,
        priority TEXT DEFAULT 'normal', done INTEGER DEFAULT 0)""")
    # one OPEN task per title (case-insensitive): the database enforces idempotency
    con.execute("CREATE UNIQUE INDEX IF NOT EXISTS open_title "
                "ON tasks(lower(title)) WHERE done = 0")
    return con

def add_task(title: str, due: str | None = None, priority: str = "normal") -> str:
    with _con() as con:
        try:
            cur = con.execute("INSERT INTO tasks(title, due, priority) VALUES (?,?,?)",
                              (title, due, priority))
            return f"Added #{cur.lastrowid}: {title}"
        except sqlite3.IntegrityError:
            row = con.execute("SELECT id, title FROM tasks WHERE lower(title)=lower(?) "
                              "AND done=0", (title,)).fetchone()
            return f"Already exists: #{row[0]} {row[1]}"

def list_tasks(include_done: bool = False, due_before: str | None = None) -> str:
    sql, args = "SELECT id, title, due, priority, done FROM tasks WHERE 1=1", []
    if not include_done:
        sql += " AND done = 0"
    if due_before:
        sql += " AND due IS NOT NULL AND due <= ?"; args.append(due_before)
    with _con() as con:
        rows = con.execute(sql + " ORDER BY id", args).fetchall()
    return "\n".join(f"#{i} [{'x' if d else ' '}] {t} (due {du or '-'}, {p})"
                     for i, t, du, p, d in rows) or "No matching tasks."

def find_tasks(text: str) -> str:
    with _con() as con:
        rows = con.execute("SELECT id, title, due, priority FROM tasks WHERE done=0 AND "
                           "lower(title) LIKE ?", (f"%{text.lower()}%",)).fetchall()
    return json.dumps([{"id": i, "title": t, "due": d, "priority": p} for i, t, d, p in rows]) \
        if rows else "No open task matches."

def complete_task(task_id: int) -> str:
    with _con() as con:
        row = con.execute("SELECT title, done FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            return f"ERROR: no task with id {task_id}. Use find_tasks to get ids."
        if row[1]:
            return f"#{task_id} was already done."
        con.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
    return f"Completed #{task_id}: {row[0]}"

def today() -> str:
    return date.today().isoformat()

def migrate_from_json(path="tasks.json") -> int:
    p = Path(path)
    if not p.exists():
        return 0
    moved = 0
    with _con() as con:
        for t in json.loads(p.read_text())["tasks"]:
            con.execute("INSERT OR IGNORE INTO tasks(id, title, due, priority, done) "
                        "VALUES (?,?,?,?,?)", (t["id"], t["title"], t["due"], t["priority"],
                                               int(t["done"])))
            moved += 1
    return moved

import ch05_todo_tools as _json_version          # same descriptions: the model sees no change
TOOLS = _json_version.TOOLS
REGISTRY = {"add_task": add_task, "list_tasks": list_tasks, "find_tasks": find_tasks,
            "complete_task": complete_task, "today": today}

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

def concurrency_demo(n=200, backend="sqlite") -> int:
    """Two processes add n tasks each. Returns how many tasks survived."""
    import multiprocessing as mp
    ctx = mp.get_context("spawn")
    procs = [ctx.Process(target=_writer, args=(backend, tag, n)) for tag in ("A", "B")]
    for p in procs: p.start()
    for p in procs: p.join()
    if backend == "sqlite":
        with _con() as con:
            return con.execute("SELECT COUNT(*) FROM tasks WHERE title LIKE 'load %'").fetchone()[0]
    return sum(t["title"].startswith("load ") for t in json.loads(Path("tasks.json").read_text())["tasks"])

def _writer(backend, tag, n):
    import sys, os
    sys.path.insert(0, os.getcwd())
    mod = __import__("sol_ch05_todo_sqlite") if backend == "sqlite" else __import__("ch05_todo_tools")
    for i in range(n):
        mod.add_task(f"load {tag}{i}")
