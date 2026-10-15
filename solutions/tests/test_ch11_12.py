"""Chapters 11-12 reference solutions."""
import asyncio
import sys
import pytest
from fakemodel import tool, text, last_user_text

def _team_script(unsupported):
    """Plan -> 2 subagents (1 step each) -> draft -> critic -> (revision)."""
    def respond(kw):
        tools = [t["name"] for t in kw.get("tools", [])]
        forced = (kw.get("tool_choice") or {}).get("name")
        if forced == "make_plan":
            return [tool("make_plan", {"subtasks": [
                {"objective": "cost", "out_of_scope": "freshness", "effort": "quick"},
                {"objective": "freshness", "out_of_scope": "cost", "effort": "deep"}]})]
        if forced == "review":
            return [tool("review", {"unsupported_claims": unsupported})]
        if "search_files" in tools:
            return [text("- finding (rag-overview.md:1)")]
        if last_user_text(kw).startswith("Revise"):
            return [text("revised answer")]
        return [text("draft answer")]
    return respond

def test_11_3_team_runs(model):
    import ch11_research_team as r
    model.reset(default=lambda kw: [tool("make_plan", {"subtasks": ["a", "b"]})]
                if (kw.get("tool_choice") or {}).get("name") == "make_plan" else [text("ok")])
    assert asyncio.run(r.research("q")) == "ok"

def test_11_3_plan_sent_as_text(model, monkeypatch):
    """A small model once sent the list as one string; the lead then ran a subagent
    per character and 16.8 timed out. The lead must recover the sub-questions."""
    import ch11_research_team as r
    seen = []
    async def fake_sub(task, max_iterations=6):
        seen.append(task); return "- f"
    monkeypatch.setattr(r, "run_subagent", fake_sub)
    model.reset(default=lambda kw: [tool("make_plan", {"subtasks": '["a b", "c d", "e"],'})]
                if (kw.get("tool_choice") or {}).get("name") == "make_plan" else [text("ok")])
    assert asyncio.run(r.research("q")) == "ok" and seen == ["a b", "c d", "e"]

def test_11_4_effort_sets_steps(model, monkeypatch):
    import sol_ch11_research_team as t, ch11_research_team as base
    seen = []
    async def fake_sub(task, max_iterations=6):
        seen.append((task.splitlines()[0], max_iterations)); return "- f"
    monkeypatch.setattr(base, "run_subagent", fake_sub)
    model.reset(default=_team_script([]))
    r = asyncio.run(t.research("q"))
    assert seen == [("Objective: cost", 3), ("Objective: freshness", 8)]
    assert r["answer"] == "draft answer" and r["unsupported"] == []

def test_11_4_one_subtask_plan_is_asked_again(model, monkeypatch):
    import sol_ch11_research_team as t, ch11_research_team as base
    seen, plans = [], []
    async def fake_sub(task, max_iterations=6):
        seen.append(task.splitlines()[0]); return "- f"
    monkeypatch.setattr(base, "run_subagent", fake_sub)
    team = _team_script([])
    def respond(kw):
        if (kw.get("tool_choice") or {}).get("name") == "make_plan":
            plans.append(kw["messages"])
            if len(plans) == 1:      # a small model's one-subtask plan
                return [tool("make_plan", {"subtasks": [
                    {"objective": "everything", "out_of_scope": "-", "effort": "quick"}]})]
        return team(kw)
    model.reset(default=respond)
    asyncio.run(t.research("q"))
    assert len(plans) == 2 and plans[1][-1]["content"][0]["type"] == "tool_result"
    assert seen == ["Objective: cost", "Objective: freshness"]

def test_11_5_critic_triggers_revision(model):
    import sol_ch11_research_team as t
    model.reset(default=_team_script(["RAG is free"]))
    r = asyncio.run(t.research("q"))
    assert r["unsupported"] == ["RAG is free"] and r["answer"] == "revised answer"

def test_11_6_compare(model, monkeypatch):
    import ex11_6_compare as ex
    def respond(kw):
        if (kw.get("tool_choice") or {}).get("name") == "score":
            return [tool("score", {"completeness": 4, "accuracy": 4, "citations": 3})]
        return _team_script([])(kw)
    model.reset(default=respond)
    rows = ex.main()
    assert len(rows) == 10 and {r["approach"] for r in rows} == {"single", "team"}

def test_12_4_print_goes_to_stderr(ws):
    import ex12_4_print_break as ex
    results = ex.main()
    assert results["print"] == ('{"name": "Pune"}', True)
    assert results["logging"] == ('{"name": "Pune"}', True)

def test_12_6_calc_server(ws):
    from mcp import Client, StdioServerParameters
    from mcp.client.stdio import stdio_client
    import os
    from pathlib import Path
    server = Path(__file__).parents[1] / "exercises" / "ex12_6_calc_server.py"
    async def go():
        params = StdioServerParameters(command=sys.executable, args=[str(server)],
                                       env={**os.environ})
        async with Client(stdio_client(params)) as c:
            names = sorted(t.name for t in (await c.list_tools()).tools)
            r = await c.call_tool("convert_units", {"value": 26.2, "from_unit": "mi", "to_unit": "km"})
            bad = await c.call_tool("calculate", {"expression": "1/0"})
            res = await c.read_resource("calc://units")
            p = await c.get_prompt("countdown", {"event": "Diwali", "date": "2026-11-08"})
            return names, r.content[0].text, bad.is_error, res.contents[0].text, p.messages[0].content.text
    names, conv, bad_err, units, prompt = asyncio.run(go())
    assert names == ["calculate", "convert_units", "days_between", "get_current_date"]
    assert "42.1648 km" in conv and bad_err and "kg, lb, g" in units and "Diwali" in prompt
