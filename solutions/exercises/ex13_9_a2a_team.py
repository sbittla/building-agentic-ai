"""Exercise 13.9 (Medium): a team of A2A agents.

Publish the Chapter 5 to-do agent as a second A2A agent, with its own agent card and skill,
next to the Chapter 13 shop analyst. Then a coordinator agent that knows neither agent's
code finds both through their cards and delegates to each.

Run:  ./course.sh ex 13.9      (or: ./course.sh python exercises/ex13_9_a2a_team.py)"""
import asyncio
import os
import sys
import threading
import time

import uvicorn
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill

import ch05_todo_tools as todo
from ch04_agent import run_agent
from ch13_a2a_client import a2a_tool, show_card
from ch13_a2a_server import AgentLoopExecutor, build_app

ANALYST_PORT, TODO_PORT = 9999, 9998

def todo_card(url: str) -> AgentCard:
    """The to-do agent describes itself: what it does, one skill, and how to reach it."""
    return AgentCard(
        name="To-do keeper",
        description="Keeps the team's to-do list: adds, lists and completes tasks.",
        version="1.0.0",
        default_input_modes=["text/plain"], default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[AgentInterface(protocol_binding="JSONRPC", url=url, protocol_version="1.0")],
        skills=[AgentSkill(id="todo_list", name="Manage to-dos",
                           description="Add a task (with an optional due date), list tasks or mark one done.",
                           tags=["tasks", "todo"], examples=["Add a task: call the supplier on Friday"])],
    )

def serve(app, port: int) -> str:
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.1)
    return f"http://127.0.0.1:{port}"

def start_team() -> tuple[str, str]:
    analyst = serve(build_app(), ANALYST_PORT)          # the card in ch13_a2a_server (section 13.7)
    todo_url = f"http://127.0.0.1:{TODO_PORT}"
    todo_system = getattr(todo, "SYSTEM", "You manage a to-do list. Use the tools; confirm what you changed.")
    todo_app = build_app(todo_card(todo_url),
                         AgentLoopExecutor(todo.TOOLS, todo.run_tool, todo_system,
                                           working="Updating the to-do list..."))
    return analyst, serve(todo_app, TODO_PORT)

if __name__ == "__main__":
    os.environ.setdefault("A2A_PUBLIC_URL", f"http://127.0.0.1:{ANALYST_PORT}")
    analyst_url, todo_url = start_team()
    for url in (analyst_url, todo_url):
        asyncio.run(show_card(url))
    tools, routes = [], {}
    for url, name, what in [
        (analyst_url, "ask_shop_analyst", "Ask the shop's data analyst agent one question about "
                                          "customers, products, orders or revenue."),
        (todo_url, "ask_todo_keeper", "Ask the to-do agent to add, list or complete tasks. "
                                      "Say exactly what the task is.")]:
        tool, run = a2a_tool(url, name, what)
        tools.append(tool)
        routes[name] = run
    question = " ".join(sys.argv[1:]) or (
        "Find the city with the most customers, then add a to-do to plan a promotion there next week.")
    print(f"\nCoordinator: {question}")
    answer, messages, stats = run_agent(
        question, tools, lambda name, args: routes[name](name, args),
        system="You coordinate two specialist agents. Delegate: data questions to the analyst, "
               "task changes to the to-do keeper. Pass each one a complete, self-contained request.")
    print(answer)
    kind = lambda b: b.get("type") if isinstance(b, dict) else getattr(b, "type", None)
    name = lambda b: b.get("name") if isinstance(b, dict) else b.name
    print("Delegations:", [name(b) for m in messages if m["role"] == "assistant"
                           and isinstance(m["content"], list) for b in m["content"] if kind(b) == "tool_use"])
