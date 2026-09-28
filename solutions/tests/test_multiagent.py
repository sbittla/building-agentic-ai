"""Chapter 11 patterns (router, handoff, evaluator-optimizer, voting), exercise 11.7, and an
agent published as an MCP server (section 13.6, exercise 13.8). Offline."""
import asyncio
import json
import os
import sys
from pathlib import Path
import pytest
from fakemodel import text, tool

def example(schema, pick=None):
    pick = pick or {}
    t = schema.get("type")
    if "enum" in schema:
        return schema["enum"][0]
    if t == "object":
        return {k: pick.get(k, example(v, pick)) for k, v in schema.get("properties", {}).items()}
    if t == "array":
        return [example(schema.get("items", {"type": "string"}), pick) for _ in range(2)]
    return {"integer": 3, "number": 3.0, "boolean": True}.get(t, "example text")

def json_or_text(pick=None, text_reply="There were 400 orders."):
    def respond(kw):
        fmt = (kw.get("output_config") or {}).get("format")
        if fmt:
            return [text(json.dumps(example(fmt["schema"], pick)))]
        return [text(text_reply)]
    return respond

def test_router_picks_one_specialist(model, ws):
    import ch11_patterns as p
    model.reset(default=json_or_text())
    choice, answer = p.route("How many orders?")
    assert choice["specialist"] == "sales_data" and "400" in answer
    router_call = model.calls[0]
    assert router_call["output_config"]["format"]["schema"]["properties"]["specialist"]["enum"][-1] == "none"
    assert model.calls[1]["system"] == __import__("ch08_sql_tools").SYSTEM   # the specialist ran

def test_router_none_route(model, ws):
    import ch11_patterns as p
    model.reset(default=json_or_text(pick={"specialist": "none"}))
    choice, answer = p.route("Book me a flight")
    assert choice["specialist"] == "none" and "only help" in answer and len(model.calls) == 1

def test_handoff_writer_has_no_tools(model, ws):
    import ch11_patterns as p
    model.reset(default=json_or_text())
    findings, summary = p.handoff("Revenue?")
    assert findings["facts"] and summary == "example text"
    assert "tools" not in model.calls[-1]                       # the writer can't query anything
    assert "findings" in model.calls[-1]["messages"][0]["content"]

def test_refine_stops_when_approved(model, ws):
    import ch11_patterns as p
    model.reset([[text(json.dumps({"text": "draft 1"}))],
                 [text(json.dumps({"approved": False, "problems": ["too long"]}))],
                 [text(json.dumps({"text": "draft 2"}))],
                 [text(json.dumps({"approved": True, "problems": []}))]])
    final, history = p.refine("Write two lines.")
    assert final == "draft 2" and [h["approved"] for h in history] == [False, True]
    assert "too long" in model.calls[2]["messages"][0]["content"]

def test_refine_caps_rounds(model, ws):
    import ch11_patterns as p
    model.reset(default=json_or_text(pick={"approved": False, "problems": ["no"], "text": "d"}))
    _, history = p.refine("x", rounds=2)
    assert len(history) == 2 and len(model.calls) == 1 + 2 * 2

def test_vote_majority(model, ws):
    import ch11_patterns as p
    ballots = iter(["high", "low", "high"])
    model.reset(default=lambda kw: [text(json.dumps({"choice": next(ballots), "reason": "r"}))])
    winner, all_ballots = p.vote("urgent?", ["low", "medium", "high"], n=3)
    assert winner == "high" and len(all_ballots) == 3

def test_11_7_solution(model, ws):
    import ex11_7_patterns as ex
    model.reset(default=json_or_text())
    results = ex.main()
    assert set(results) == {"a router", "b evaluator-optimizer", "c voting", "d handoff"}
    assert results["c voting"]["model_calls"] == 15 and len(results["c voting"]["labels"]) == 5

def test_agent_as_mcp_server(ws):
    """The analyst agent runs in its own process (with the offline model there, too) and is
    reached like any other MCP tool."""
    import ch13_mcp_agent as m
    site = str(Path(__file__).parent / "fake_model_site")
    cfg = {"servers": {"analyst": {"command": sys.executable, "args": ["ch13_agent_server.py"],
                                   "env": {"FAKE_MODEL": "1", "PYTHONPATH": f"{site}:{ws}",
                                           "ANTHROPIC_API_KEY": "sk-test-offline"}}}}
    async def go():
        async with m.MCPHub(cfg) as hub:
            names = [t["name"] for t in hub.tools]
            out, is_error = await hub.call("analyst__ask_sql_analyst", {"question": "How many orders?"})
            return names, out, is_error
    names, out, is_error = asyncio.run(go())
    assert names == ["analyst__ask_sql_analyst"] and not is_error and "offline" in out

def test_13_8_config_passes_only_named_secrets():
    cfg = json.loads((Path(__file__).parents[1] / "exercises" / "servers_with_analyst.json").read_text())
    analyst = cfg["servers"]["analyst"]
    assert analyst["args"] == ["ch13_agent_server.py"] and "ANTHROPIC_API_KEY" in analyst["pass_env"]
    assert "pass_env" not in cfg["servers"]["todo"]

def test_13_8_coordinator(model, ws):
    import ex13_8_coordinator as ex
    import ch13_mcp_agent as m
    model.reset([[tool("analyst__ask_sql_analyst", {"question": "Top 3 customers by revenue?"})],
                 [tool("todo__add_task", {"title": "Thank Customer 7"}),
                  tool("todo__add_task", {"title": "Thank Customer 12"}),
                  tool("todo__add_task", {"title": "Thank Customer 3"})],
                 [text("Done: three to-dos added.")]])
    site = str(Path(__file__).parent / "fake_model_site")
    cfg = {"servers": {"todo": {"command": sys.executable, "args": ["ch13_todo_server.py"]},
                       "analyst": {"command": sys.executable, "args": ["ch13_agent_server.py"],
                                   "env": {"FAKE_MODEL": "1", "PYTHONPATH": f"{site}:{ws}",
                                           "ANTHROPIC_API_KEY": "sk-test-offline"}}}}
    answer, calls = asyncio.run(ex.main(cfg))
    assert calls.count("todo__add_task") == 3 and calls[0] == "analyst__ask_sql_analyst"
