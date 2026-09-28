"""Chapter 28 in production: logs, latency, timeline, taxonomy, SLOs, dashboard.
All offline: spans are scripted with ch28_ops.build_spans."""
import io
import json
from html.parser import HTMLParser

import pytest

import ch28_agentops as ops
import ch28_ops as o

def _run(tid, steps, stop="end_turn"):
    spans = o.build_spans(tid, steps, stop_reason=stop)
    return ops.summarize(tid, spans), spans

CHAT = ("chat", 1000, 2000, 100)

def test_log_event_redacts_and_joins_on_trace_id():
    lines, f = [], io.StringIO()
    o.log_event(lines, "tool_call", "t1", "r1", tool="run_query",
                args="ana@example.com")
    rec = o.log_event(f, "run_end", "t1", "r1", ms=1200)
    first = json.loads(lines[0])
    assert first["trace_id"] == "t1" and first["args"] == "[email]"
    assert json.loads(f.getvalue())["event"] == "run_end" == rec["event"]
    with pytest.raises(ValueError):
        o.log_event(lines, "coffee_break", "t1")

def test_latency_breakdown_sums():
    _, spans = _run("a", [CHAT, ("tool", "run_query", 300, {}),
                          ("tool", "get_schema", 100, {}), CHAT])
    b = o.latency_breakdown(spans)
    assert b["model_ms"] == 2000 and b["tool_ms"] == 400
    assert b["tools"] == {"run_query": 300, "get_schema": 100}
    assert b["model_ms"] + b["tool_ms"] + b["other_ms"] == pytest.approx(b["total_ms"])
    assert b["other_ms"] == 5 * 40                 # the gaps between steps
    assert sum(b["share"].values()) == pytest.approx(1.0, abs=0.01)

def test_timeline_width_and_order():
    _, spans = _run("a", [CHAT, ("tool", "run_query", 300, o.ERR), CHAT])
    text = o.timeline(spans, width=200)            # asked too wide: still fits
    rows = text.splitlines()
    assert all(len(r) <= 88 for r in rows)
    assert [r.split()[0] for r in rows[1:]] == ["agent", "chat", "run_query", "chat"]
    assert "!" in rows[3] and "x" in rows[3] and rows[2].startswith("  chat")
    # without start_ms (as ch28_otel.py writes them) the steps are laid end to end
    bare = [{k: v for k, v in s.items() if k != "start_ms"} for s in spans]
    rows = o.timeline(bare).splitlines()
    assert rows[2].index("#") < rows[3].index("x") < rows[4].index("#")

def test_classify_detailed_crafted_runs():
    loop = _run("loop", [CHAT] + [("tool", "run_query", 100,
                                   {**o.ERR, "tool.args_hash": "h"}), CHAT] * 3)
    assert "infinite_loop" in o.classify_detailed(*loop)
    assert "infinite_loop" in o.classify_detailed(*_run("cap", [CHAT], "tool_use"))
    made_up = o.classify_detailed(*_run("h", [CHAT, ("tool", "run_query", 100, {}),
                                              CHAT]),
                                  {"passed": False, "answer": "Sales were 48,210",
                                   "tool_results": ["[(41877.5,)]"]})
    assert made_up == ["hallucination"]
    grounded = o.classify_detailed(*_run("g", [CHAT, ("tool", "q", 100, {}), CHAT]),
                                   {"answer": "Sales were 41,877.5 in 3 regions",
                                    "tool_results": ["[(41877.5,)]"]})
    assert grounded == []
    denied = _run("d", [CHAT, ("tool", "refund", 50,
                               {**o.ERR, "error.type": "not_authorized"}), CHAT])
    assert o.classify_detailed(*denied) == ["auth_failure"]   # not a tool failure
    runaway = _run("r", [("chat", 3000, 50_000, 500)] * 20)
    assert o.classify_detailed(*runaway) == ["runaway"]
    ok = _run("ok", [CHAT, ("tool", "q", 100, {}), CHAT])
    assert o.classify_detailed(*ok, {"passed": True}) == []
    assert o.classify_detailed(*ok, {"passed": False}) == ["misread_result"]

def test_taxonomy_has_twelve_classes_with_chapters():
    assert len(o.TAXONOMY) == 12
    assert all(len(v) == 5 and v[3] for v in o.TAXONOMY.values())
    assert o.TAXONOMY["memory_poisoning"][4] is False       # not visible in traces

def test_measure_slos_none_when_unavailable():
    runs = [_run(f"r{i}", [CHAT])[0] for i in range(4)]
    res = {r["name"]: r for r in o.measure_slos(runs, {"r0": {"passed": True},
                                                        "r1": {"passed": False}})}
    assert len(res) == len(o.AGENT_SLOS) == 7
    success = res["Task success"]
    assert success["value"] == 0.5 and success["met"] is False and success["n"] == 2
    assert success["budget_left"] == pytest.approx(1 - 1 / (0.05 * 2), abs=0.01)
    assert res["p95 latency (ms)"]["met"] is True
    for name in ("Tool selection accuracy", "Unsafe action rate",
                 "Escalation accuracy", "Retrieval recall"):
        assert res[name]["value"] is None and res[name]["met"] is None
    assert all(r["value"] is None for r in o.measure_slos([], {}))

def test_dashboard_is_valid_html(ws):
    spans, evals = o.sample()
    runs = [ops.summarize(t, s) for t, s in spans.items()]
    rep = ops.report(runs, [ops.classify(r) for r in runs])
    path = o.dashboard(rep, o.measure_slos(runs, evals), str(ws / "dash.html"))
    page = open(path).read()
    stack = []                                     # every opened tag is closed

    class Tags(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag not in ("meta", "br"):
                stack.append(tag)

        def handle_endtag(self, tag):
            assert stack.pop() == tag

    Tags().feed(page)
    assert stack == [] and page.startswith("<!doctype html>")
    assert all(s["name"] in page for s in o.AGENT_SLOS)
    assert "<script" not in page and "http" not in page and "<svg" in page

def test_28_6_dashboard(ws):
    import ex28_6_dashboard as ex
    path = ex.main(out=str(ws / "ex28_6.html"))
    assert "Task success" in open(path).read()

def test_28_7_taxonomy():
    import ex28_7_taxonomy as ex
    counts = ex.main()
    assert len(counts) >= 6
    assert {"wrong_tool", "hallucination", "infinite_loop", "auth_failure",
            "injection", "runaway", "context_overflow"} <= set(counts)
