"""Exercises 8.5 and 8.6, run end to end with sol_ch08_sql_tools.

    python run8_5_tables.py budget    8.5: a self-correction lands in query_log.jsonl, and
                                      forced repeated failures hit the retry budget
    python run8_5_tables.py confirm   8.6: the user rejects a proposed table (typed on stdin)
                                      and the agent adapts its query
"""
import json
import os
import sys

import sol_ch08_sql_tools as sol
from ch04_agent import run_agent

def show_log(since: int = 0):
    lines = open(sol.LOG).read().splitlines()[since:] if os.path.exists(sol.LOG) else []
    for line in lines:
        e = json.loads(line)
        print(f"  {'ok   ' if e['ok'] else 'ERROR'} {e['sql'][:90]!r}"
              + (f"  -> {e['error'][:60]}" if e["error"] else ""))
    return lines

def budget():
    if os.path.exists(sol.LOG):
        os.remove(sol.LOG)
    no_tables = [sol.TOOLS[0], sol.TOOLS[2]]          # 8.5 on its own: no table proposals
    print("1. A sabotaged prompt (customers are 'in the clients table'):")
    sol.new_question()
    from ex8_4_self_correct import WRONG_SYSTEM
    answer, _, _ = run_agent("Which city has the most customers?", no_tables, sol.run_tool,
                             system=WRONG_SYSTEM, verbose=False)
    print(f"Agent: {answer[:300]}\nquery log:")
    first = show_log()
    fixed = any(not json.loads(l)["ok"] for l in first) and json.loads(first[-1])["ok"]
    print(f"self-corrected (a failed query, then a working one): {fixed}")

    print("\n2. Forced repeated failures: the database file is gone, so every query fails:")
    sol.new_question()
    saved, sol.base.DB_PATH = sol.base.DB_PATH, "missing_shop.db"
    try:
        answer, _, _ = run_agent("How many orders are there? If a query fails, retry it.",
                                 no_tables, sol.run_tool, system=sol.base.SYSTEM,
                                 verbose=False, max_iterations=8)
        print(f"Agent: {answer[:300]}")
        while sol.state["failed"] < sol.MAX_FAILED:     # the model gave up early: keep going
            sol.run_tool("run_query", {"sql": "SELECT COUNT(*) FROM orders"})
        print("the next query gets:", sol.run_tool("run_query", {"sql": "SELECT 1"}))
    finally:
        sol.base.DB_PATH = saved
    print("query log:")
    show_log(len(first))
    print(f"retry budget used up: {sol.state['failed'] >= sol.MAX_FAILED} "
          f"({sol.state['failed']} failed queries, budget {sol.MAX_FAILED})")

def confirm():
    sol.new_question()
    question = "Which city has the most customers who have placed at least one order?"
    print(f"You: {question}")
    print("(at every table prompt the user types: customers  -- i.e. rejects 'orders')")
    answer, messages, _ = run_agent(question, sol.TOOLS, sol.run_tool, system=sol.SYSTEM)
    print(f"Agent: {answer}")
    print(f"approved tables: {sorted(sol.state['approved_tables'] or [])}")
    queries = [b.input["sql"] for m in messages if m["role"] == "assistant"
               for b in m["content"] if getattr(b, "type", "") == "tool_use"
               and b.name == "run_query"]
    last = queries[-1] if queries else ""
    print(f"final query: {last!r}")
    print(f"agent adapted to the user's tables: {bool(last) and 'orders' not in last.lower()}")

if __name__ == "__main__":
    {"budget": budget, "confirm": confirm}[sys.argv[1] if len(sys.argv) > 1 else "budget"]()
