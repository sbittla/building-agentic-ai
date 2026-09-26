"""Part 9 (chapters 27-29): trajectories, AgentOps and cost engineering. Offline."""
import json

import pytest
from fakemodel import last_user_text, text, tool, tool_results

def _analyst(sql_for):
    """A scripted SQL analyst: schema first, then the query sql_for(question) gives,
    then an answer that repeats the query's result."""
    def policy(kw):
        q = next(m["content"] for m in kw["messages"] if m["role"] == "user"
                 and isinstance(m["content"], str))
        turn = sum(m["role"] == "assistant" for m in kw["messages"])
        plan = sql_for(q)
        if plan is None:
            return [text("I can help with questions about the shop's data.")]
        if turn == 0:
            return [tool("get_schema", {})]
        if turn == 1:
            return [tool("run_query", {"sql": plan})]
        return [text(f"The answer is {tool_results(kw)[0]}.")]
    return policy

SQL = {"cancelled": "SELECT COUNT(*) FROM orders WHERE status = 'cancelled'",
       "Delete": "SELECT COUNT(*) FROM orders WHERE status = 'cancelled'"}

def test_27_trajectory_and_process_checks(model, ws):
    import ch08_sql_tools as sql, ch27_trajectory as t
    model.reset(default=_analyst(lambda q: SQL["cancelled"] if "cancel" in q.lower()
                                 else None))
    case = {"id": "c", "question": "How many orders were cancelled?",
            "answer_sql": SQL["cancelled"], "expect_sequence": ["get_schema", "run_query"],
            "arg_checks": [{"tool": "run_query", "arg": "sql", "must_match": "cancel",
                            "must_not_match": "DELETE"}], "max_steps": 4}
    r = t.grade(case, sql.TOOLS, sql.run_tool, sql.SYSTEM)
    assert r["outcome"] and r["process"] and [s["tool"] for s in r["trajectory"]] == \
        ["get_schema", "run_query"]
    bad = t.check_process({"expect_sequence": ["run_query", "get_schema"],
                           "forbidden_tools": ["run_query"], "max_steps": 1},
                          r["trajectory"])
    assert len(bad) == 3
    loop = [{"tool": "run_query", "args": {"sql": "x"}, "error": True, "result": ""}] * 2
    assert "repeated a failing call" in t.check_process({}, loop)[0]
    assert "without recovering" in t.check_process({"must_recover": True}, loop[:1])[0]
    assert t.tool_overlap(r["trajectory"], ["run_query"]) == {"precision": 0.5,
                                                              "recall": 1.0}

def test_27_right_answer_wrong_path(model, ws):
    import ch08_sql_tools as sql, ch27_trajectory as t
    def policy(kw):                                 # tries a DELETE first, then answers
        turn = sum(m["role"] == "assistant" for m in kw["messages"])
        steps = [[tool("run_query", {"sql": "DELETE FROM orders WHERE status='x'"})],
                 [tool("run_query", {"sql": SQL["cancelled"]})]]
        return steps[turn] if turn < 2 else [text(f"It is {tool_results(kw)[0]}.")]
    model.reset(default=policy)
    case = {"id": "c", "question": "How many cancelled?", "answer_sql": SQL["cancelled"],
            "arg_checks": [{"tool": "run_query", "arg": "sql", "must_not_match": "DELETE"}]}
    r = t.grade(case, sql.TOOLS, sql.run_tool, sql.SYSTEM)
    assert r["outcome"] and not r["process"] and not r["pass"]

def test_27_gate_and_drift():
    import ch27_trajectory as t
    assert t.gate([True] * 18 + [False] * 2, [True] * 12 + [False] * 8)["block"]
    assert not t.gate([True] * 18 + [False] * 2, [True] * 17 + [False] * 3)["block"]
    assert t.drift([0.9] * 8 + [0.7]) and not t.drift([0.9] * 8 + [0.88])
    runs = [{"flagged": i % 10 == 0} for i in range(100)]
    sample = t.sample_for_review(runs, rate=0.05, seed=1)
    assert all(r in sample for r in runs if r["flagged"]) and len(sample) < 30

def test_27_6_trajectory_cases(model, ws):
    import ex27_6_trajectory as ex
    def sql_for(q):
        if "2025" in q:
            return "SELECT COUNT(*) FROM customers WHERE joined LIKE '2025%'"
        if "March 2026" in q:
            return "SELECT COUNT(*) FROM orders WHERE order_date LIKE '2026-03%'"
        if "expensive" in q:
            return "SELECT name FROM products ORDER BY price DESC LIMIT 1"
        if "order table" in q:
            return "SELECT COUNT(*) FROM orders"
        if "pending" in q:
            return "SELECT COUNT(*) FROM orders WHERE status = 'pending'"
        return None
    def policy(kw):
        q = last_user_text(kw) if not tool_results(kw) else next(
            m["content"] for m in kw["messages"] if m["role"] == "user"
            and isinstance(m["content"], str))
        if "SQL stand" in q:
            return [text("SQL stands for Structured Query Language.")]
        return _analyst(sql_for)(kw)
    model.reset(default=policy)
    rows = ex.main(trials=1)
    by = {r["id"]: r for r in rows}
    assert by["schema_then_query"]["pass"] and by["no_tools_needed"]["pass"]
    assert by["never_writes"]["pass"]                         # it only read
    assert all(r["pass"] for r in rows), [(r["id"], r["failures"]) for r in rows]

def test_27_7_online_drift():
    import ex27_7_online as ex
    daily, alerts = ex.main(days=14, drop_day=12)
    assert alerts and min(alerts) >= 12 and all(a >= 12 for a in alerts)

# ================================================================ 28: AgentOps
def _spans(tmp, runs):
    """Write spans the way ch28_otel.py does, for crafted runs."""
    path = tmp / "spans_test.jsonl"
    with open(path, "w") as f:
        for tid, (stop, tools, ms) in runs.items():
            f.write(json.dumps({"name": "invoke_agent", "trace_id": tid, "span_id": "r",
                                "parent_id": None, "ms": ms,
                                "attributes": {"agent.stop_reason": stop}}) + "\n")
            f.write(json.dumps({"name": "chat claude-sonnet-5", "trace_id": tid,
                                "span_id": "c", "parent_id": "r", "ms": ms / 2,
                                "attributes": {"gen_ai.request.model": "claude-sonnet-5",
                                               "gen_ai.usage.input_tokens": 1000,
                                               "gen_ai.usage.output_tokens": 100}}) + "\n")
            for name, err in tools:
                f.write(json.dumps({"name": f"execute_tool {name}", "trace_id": tid,
                                    "span_id": "t", "parent_id": "r", "ms": 50,
                                    "attributes": {"gen_ai.tool.name": name,
                                                   "error": err}}) + "\n")
    return path

def test_28_summarize_classify_report_alerts(ws):
    import ch28_agentops as ops
    path = _spans(ws, {
        "a": ("end_turn", [("run_query", False)], 2000),
        "b": ("end_turn", [("run_query", True)] * 3, 3000),           # tool loop
        "c": ("max_tokens", [], 1000),                                 # cut off
        "d": ("tool_use", [("get_schema", False)] * 8, 9000),          # step limit
        "e": ("end_turn", [], 45_000)})                                # too slow
    runs = [ops.summarize(t, s) for t, s in ops.load_spans(str(path)).items()]
    assert runs[0]["cost"] == pytest.approx((1000 * 2 + 100 * 10) / 1e6)
    classes = [ops.classify(r) for r in runs]
    assert classes == ["ok", "tool_loop", "cut_off", "step_limit", "too_slow"]
    assert ops.classify(runs[0], passed_eval=False) == "wrong_answer"
    rep = ops.report(runs, classes)
    assert rep["success_rate"] == 0.2 and rep["tools"]["run_query"]["error_rate"] == 0.75
    assert any("run_query" in a for a in ops.alerts(rep))
    assert ops.redact("mail ana@example.com card 4111 1111 1111 1111 sk-abcdefghijklmnopqrs") \
        == "mail [email] card [card] [key]"

def test_28_4_ignored_error():
    import ex28_4_ignored_error as ex
    run = {"stop_reason": "end_turn", "tool_calls": 3, "ms": 1000,
           "tools": [("fetch", 10, True), ("read", 10, False), ("read", 10, False)]}
    assert ex.classify(run) == "ignored_error"
    fixed = dict(run, tools=[("fetch", 10, True), ("fetch", 10, False)])
    assert ex.classify(fixed) == "ok"
    loop = dict(run, tools=[("fetch", 10, True)] * 3)
    assert ex.classify(loop) == "tool_loop"
    assert "ignored_error" in ex.FAILURES

def test_28_5_burn_alert():
    import ex28_5_burn as ex
    rows, alerts = ex.main(incident=(14, 16))
    assert alerts == [15]

# ================================================================ 29: cost engineering
def test_29_estimate_and_capacity():
    import ch29_costs as c
    plain = c.estimate(6, 6000, 100, 800, 300)
    cached = c.estimate(6, 6000, 100, 800, 300, cache=True)
    assert plain["input_tokens"] == 53_100 and cached["dollars"] < plain["dollars"]
    assert c.concurrency_needed(10, 8) == 80
    assert round(c.rate_limited_capacity(4000, 2_000_000, 6, 60_000)) == 33

def test_29_4_budgets(model, ws):
    import ex29_4_budgets as ex
    ex.DAILY.spent.clear()
    model.reset(default=lambda kw: [tool("run_query", {"sql": "SELECT 1"})])
    answer, stats = ex.ask("ana", "Keep querying forever", per_request=0.0035)
    assert answer.startswith("Stopped early: request budget")
    assert stats["steps"] == 9                   # 9 x $0.0004 per scripted call
    model.reset(default=lambda kw: [text("42")])
    for _ in range(400):                         # $0.0004 a run: 250 fit in $0.10
        answer, _ = ex.ask("ben", "How many?")
        if answer.startswith("Sorry"):
            break
    assert "ben has used today's budget" in answer
    assert ex.ask("chen", "How many?")[0] == "42"
    ex.DAILY.spent.clear()

def test_29_5_cost_cut(model, ws):
    import ex29_5_cost_cut as ex
    model.reset(default=_analyst(lambda q: SQL["cancelled"] if "cancel" in q.lower()
                                 else None))
    before, after = ex.main(trials=1)
    assert before["runs"] == after["runs"]
    small_calls = [c for c in model.calls if c["model"] == "claude-haiku-4-5"]
    assert small_calls and any("cache_control" in t for c in model.calls
                               for t in c.get("tools", []))
