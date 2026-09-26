"""Section 13.7 and exercise 13.9: A2A agents, end to end with the real a2a-sdk (server and
client) and the scripted stand-in model. Offline."""
import asyncio
import json
import socket
import threading
import time

import httpx
import pytest
from fakemodel import text, tool

pytest.importorskip("a2a")
uvicorn = pytest.importorskip("uvicorn")


def _serve(app):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    return server, f"http://127.0.0.1:{port}"


def _card(url, name="Shop data analyst"):
    from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
    return AgentCard(name=name, description="test", version="1.0.0",
                     default_input_modes=["text/plain"], default_output_modes=["text/plain"],
                     capabilities=AgentCapabilities(streaming=True),
                     supported_interfaces=[AgentInterface(protocol_binding="JSONRPC", url=url,
                                                          protocol_version="1.0")],
                     skills=[AgentSkill(id="s", name="s", description="d", tags=["t"])])


@pytest.fixture
def analyst(ws, model):
    """The Chapter 13 analyst on a free port, with a card that points at that port."""
    import ch13_a2a_server as srv
    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(srv.build_app(_card(f"http://127.0.0.1:{port}")),
                                           host="127.0.0.1", port=port, log_level="error"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True


def test_card_is_public_and_describes_the_skill(analyst):
    card = httpx.get(f"{analyst}/.well-known/agent-card.json").json()
    assert card["name"] == "Shop data analyst" and card["skills"][0]["id"] == "s"
    assert card["supportedInterfaces"][0]["protocolBinding"] == "JSONRPC"


def test_task_runs_the_agent_and_returns_an_artifact(analyst, model):
    from ch13_a2a_client import ask_remote_agent
    model.reset([[tool("run_query", {"sql": "SELECT COUNT(*) AS n FROM orders WHERE status='cancelled'"})],
                 [text("88 orders were cancelled.")]])
    answer = asyncio.run(ask_remote_agent(analyst, "How many orders were cancelled?", show=False))
    assert answer == "88 orders were cancelled."
    assert "How many orders were cancelled?" in json.dumps(model.calls[0]["messages"], default=str)


def test_unfinished_agent_is_a_failed_task(analyst, model):
    from ch13_a2a_client import ask_remote_agent
    model.reset(default=lambda kw: [tool("run_query", {"sql": "SELECT 1"})])   # never stops
    with pytest.raises(RuntimeError, match="no answer"):
        asyncio.run(ask_remote_agent(analyst, "Loop forever", show=False))


def test_token_protects_everything_but_the_card(ws, model, monkeypatch):
    import ch13_a2a_server as srv
    import ch13_a2a_client as cli
    monkeypatch.setattr(srv, "TOKEN", "s3cret")
    server, url = _serve(srv.build_app(_card("http://unused")))
    try:
        assert httpx.get(f"{url}/.well-known/agent-card.json").status_code == 200
        assert httpx.post(url, json={"jsonrpc": "2.0", "id": 1, "method": "SendMessage"}).status_code == 401
        assert httpx.post(url, json={}, headers={"Authorization": "Bearer wrong"}).status_code == 401
    finally:
        server.should_exit = True


def test_remote_agent_as_a_coordinator_tool(analyst, model):
    from ch04_agent import run_agent
    from ch13_a2a_client import a2a_tool
    t, run = a2a_tool(analyst, "ask_shop_analyst", "Ask the analyst.")
    model.reset([[tool("ask_shop_analyst", {"question": "Top city?"})],   # coordinator delegates
                 [text("Berlin, with 14 customers.")],                    # the remote analyst answers
                 [text("The top city is Berlin.")]])                      # coordinator finishes
    answer, messages, stats = run_agent("Which city is top?", [t], run, verbose=False)
    assert answer == "The top city is Berlin." and stats["tool_calls"] == 1
    assert "Berlin, with 14 customers." in json.dumps(messages[2]["content"], default=str)


def test_exercise_13_10_team_of_two_agents(ws, model, monkeypatch):
    import ex13_9_a2a_team as team
    monkeypatch.setattr(team, "ANALYST_PORT", _free_port())
    monkeypatch.setattr(team, "TODO_PORT", _free_port())
    import ch13_a2a_server as srv
    monkeypatch.setattr(srv, "CARD", _card(f"http://127.0.0.1:{team.ANALYST_PORT}"))
    monkeypatch.setattr(srv.build_app, "__defaults__", (srv.CARD, None))
    analyst_url, todo_url = team.start_team()
    from ch13_a2a_client import ask_remote_agent
    model.reset([[tool("add_task", {"title": "Plan a promotion in Berlin", "due": "2026-10-02"})],
                 [text("Added: Plan a promotion in Berlin.")]])
    answer = asyncio.run(ask_remote_agent(todo_url, "Add a task to plan a promotion in Berlin", show=False))
    assert "Berlin" in answer
    assert "Plan a promotion in Berlin" in (ws / "tasks.json").read_text()
    card = httpx.get(f"{todo_url}/.well-known/agent-card.json").json()
    assert card["name"] == "To-do keeper" and card["skills"][0]["id"] == "todo_list"


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
