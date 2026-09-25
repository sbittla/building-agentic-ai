"""Chapters 4-5 reference solutions."""
import json
import os
from pathlib import Path
from fakemodel import tool, text

def test_4_3_chapter_loop_runs(model):
    import ch04_agent, ch03_tools
    model.reset([[tool("get_current_date", {})],
                 [tool("days_between", {"start": "2026-09-23", "end": "2027-07-04"})],
                 [text("284 days, a Sunday.")]])
    answer, _, stats = ch04_agent.run_agent("July 4?", ch03_tools.TOOLS, ch03_tools.run_tool)
    assert stats["tool_calls"] == 2 and "Sunday" in answer

def test_4_4_cap_and_failing_tool(model):
    import ex4_4_cap as ex
    model.reset([[tool("get_current_date", {})]] + [[tool("always_fails", {})]] * 4)
    capped, failing = ex.main()
    assert "max_iterations=1" in capped and "max_iterations=4" in failing

def test_4_5_tracer(model, capsys):
    import ex4_5_tracer as ex, ch03_tools
    model.reset([[tool("get_current_date", {})], [text("done")]])
    answer, trace = ex.run_agent_traced("q", ch03_tools.TOOLS, ch03_tools.run_tool)
    assert answer == "done" and len(trace) == 2 and trace[0]["tools"]
    assert "total" in capsys.readouterr().out

def test_4_6_chat_remembers(model):
    import ex4_6_chat as ex
    model.reset([[text("284 days")], [text("about 40.6 weeks")]])
    answers, history = ex.chat(["How many days until July 4?", "And how many weeks is that?"])
    assert len(model.calls[1]["messages"]) == 3        # previous turn was sent again

def test_4_7_cost_profile(model, ws):
    import ex4_7_cost_profile as ex
    model.reset(default=lambda kw: [text("x")] if len(kw["messages"]) > 2
                else [tool("get_current_date", {})])
    rows, per_step = ex.profile(runs=2)
    assert len(rows) == 5 and rows[0]["steps"][0] == 2
    assert list(per_step) == [1, 2]                      # input tokens charted by step number
    assert Path(ex.chart(per_step)).exists()

def _fresh_tasks(ws):
    for f in ("tasks.json", "tasks.db"):
        (ws / f).unlink(missing_ok=True)

def test_5_3_to_5_5_todo(ws):
    _fresh_tasks(ws)
    import sol_ch05_todo_tools as t
    t.add_task("call bank", "2020-01-01"); t.add_task("buy milk", "2999-01-01")
    assert "Renamed #1" in t.run_tool("rename_task", {"task_id": 1, "new_title": "call HDFC bank"})
    assert "call HDFC bank" in t.overdue_tasks() and "buy milk" not in t.overdue_tasks()
    assert "Deleted" in t.delete_task(2) and "does not exist" in t.delete_task(2)

def test_5_6_ambiguity_is_visible(ws):
    _fresh_tasks(ws)
    import ch05_todo_tools as t
    t.add_task("Buy milk"); t.add_task("Buy oat milk")
    assert len(json.loads(t.find_tasks("milk"))) == 2   # the model sees both -> asks
    assert "ask the user" in [x for x in t.TOOLS if x["name"] == "complete_task"][0]["description"]

def test_5_6_agent_asks_then_completes(model, ws):
    _fresh_tasks(ws)
    import ch05_todo_tools as t, ch04_agent
    t.add_task("Buy milk"); t.add_task("Buy oat milk")
    model.reset([[tool("find_tasks", {"text": "milk"})], [text("Which one: #1 Buy milk or #2 Buy oat milk?")],
                 [tool("complete_task", {"task_id": 2})], [text("Done: Buy oat milk.")]])
    a1, hist, _ = ch04_agent.run_agent("complete the milk task", t.TOOLS, t.run_tool, verbose=False)
    a2, hist, _ = ch04_agent.run_agent("the oat one", t.TOOLS, t.run_tool, messages=hist, verbose=False)
    tasks = json.loads(Path("tasks.json").read_text())["tasks"]
    assert "Which one" in a1 and tasks[1]["done"] is True and tasks[0]["done"] is False

def test_5_7_sqlite(ws):
    _fresh_tasks(ws)
    import ch05_todo_tools as j
    j.add_task("old json task", "2026-10-01")
    import sol_ch05_todo_sqlite as s
    assert s.migrate_from_json() == 1
    assert "old json task" in s.list_tasks()
    assert s.add_task("Buy milk").startswith("Added") and s.add_task("buy MILK").startswith("Already")
    tid = json.loads(s.find_tasks("milk"))[0]["id"]
    assert s.complete_task(tid).startswith("Completed") and "already done" in s.complete_task(tid)
    assert s.add_task("Buy milk").startswith("Added")     # completed tasks don't block new ones
    assert s.run_tool("complete_task", {"task_id": 999}).startswith("ERROR")

def test_5_7_concurrency(ws):
    _fresh_tasks(ws)
    import sol_ch05_todo_sqlite as s
    survived = s.concurrency_demo(n=150, backend="sqlite")
    assert survived == 300


def test_4_thinking_blocks_go_back_unchanged(model):
    from types import SimpleNamespace as S
    import ch04_agent as a4, ch03_tools as t3
    thought = S(type="thinking", thinking="I need today's date first.", signature="sig-abc")
    model.reset([[thought, tool("get_current_date", {})], [text("Today is Thursday.")]])
    answer, messages, stats = a4.run_agent("What day is it?", t3.TOOLS, t3.run_tool, verbose=False,
                                           thinking={"type": "adaptive"}, effort="low")
    assert answer == "Today is Thursday."
    assert model.calls[0]["thinking"] == {"type": "adaptive"}
    assert model.calls[0]["output_config"] == {"effort": "low"}
    sent_back = model.calls[1]["messages"][1]["content"]
    assert sent_back[0] is thought                     # the same block, signature and all

def test_4_every_stop_reason_is_handled(model, monkeypatch):
    from types import SimpleNamespace as S
    import ch04_agent as a4, ch03_tools as t3
    orig = model.respond
    for reason, expect in [("max_tokens", "cut off"), ("refusal", "declined"),
                           ("model_context_window_exceeded", "no longer fits")]:
        def respond(kw, reason=reason):
            r = orig(kw); r.stop_reason = reason; return r
        monkeypatch.setattr(model, "respond", respond)
        model.reset(default=[text("Partial answer")])
        answer, _, stats = a4.run_agent("q", t3.TOOLS, t3.run_tool, verbose=False)
        assert expect in answer and "Partial answer" in answer and stats["stop_reason"] == reason
    monkeypatch.setattr(model, "respond", orig)
