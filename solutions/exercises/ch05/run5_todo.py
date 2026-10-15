"""Exercises 5.3-5.6, run end to end as conversations with the to-do agent.

    python run5_todo.py restart   5.3: add tasks, end the process's session, and a NEW
                                  session (empty history) still sees them (tasks.json)
    python run5_todo.py rename    5.4: "Rename 'call bank' to 'call HDFC bank'" goes through
                                  find_tasks then rename_task (sol_ch05_todo_tools)
    python run5_todo.py due       5.5: "What's due this week?" and "What's overdue?" with past,
                                  current and future tasks (sol_ch05_todo_tools)
    python run5_todo.py clarify   5.6: two milk tasks; the agent asks which one, then
                                  completes "Buy oat milk"
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import ch05_todo_tools as base
from ch04_agent import run_agent

SYSTEM = ("You manage the user's to-do list. Always use the tools; never invent tasks. "
          "Resolve relative dates with the today tool.")
CLARIFY = SYSTEM + " If more than one task matches, ask which one; never guess."

def chat(lines, tools, run_tool, system=SYSTEM, history=None):
    history = history or []
    for line in lines:
        print(f"\nYou: {line}")
        answer, history, _ = run_agent(line, tools, run_tool, system=system, messages=history)
        print(f"Agent: {answer}")
    return history

def tasks():
    return json.loads(base.STORE.read_text())["tasks"] if base.STORE.exists() else []

def fresh():
    if base.STORE.exists():
        base.STORE.unlink()

def restart():
    fresh()
    chat(["Add 'call the bank' due 2026-11-02 and 'book flights' due 2026-11-20."],
         base.TOOLS, base.run_tool)
    print("\n---- restart: a new session with an empty history ----")
    chat(["What's on my to-do list?"], base.TOOLS, base.run_tool)
    print(f"\ntasks.json after the restart: {[t['title'] for t in tasks()]}")

def rename():
    import sol_ch05_todo_tools as sol
    fresh()
    base.add_task("call bank")
    chat(["Rename 'call bank' to 'call HDFC bank'."], sol.TOOLS, sol.run_tool, system=sol.SYSTEM)
    print(f"\ntasks.json: {[t['title'] for t in tasks()]}")

def due():
    import sol_ch05_todo_tools as sol
    fresh()
    today = date.today()
    for title, when in [("pay old invoice", today - timedelta(days=10)),
                        ("renew insurance", today - timedelta(days=1)),
                        ("team lunch", today + timedelta(days=2)),
                        ("dentist", today + timedelta(days=5)),
                        ("holiday booking", today + timedelta(days=40))]:
        base.add_task(title, due=when.isoformat())
    sunday = today + timedelta(days=6 - today.weekday())        # the coming Sunday
    print("test data:", [(t["title"], t["due"]) for t in tasks()])
    week = [t["title"] for t in tasks() if t["due"] <= sunday.isoformat()]
    print(f"expected this week (due on or before Sunday {sunday}): {week}")
    print("expected overdue: pay old invoice, renew insurance")
    chat(["What's due this week?"], sol.TOOLS, sol.run_tool, system=sol.SYSTEM)
    chat(["What's overdue?"], sol.TOOLS, sol.run_tool, system=sol.SYSTEM)

def clarify():
    fresh()
    base.add_task("Buy milk")
    base.add_task("Buy oat milk")
    chat(["Complete the milk task.", "The oat one."], base.TOOLS, base.run_tool, system=CLARIFY)
    done = [t["title"] for t in tasks() if t.get("done")]
    print(f"\ncompleted: {done}")

if __name__ == "__main__":
    {"restart": restart, "rename": rename, "due": due, "clarify": clarify}[sys.argv[1]]()
