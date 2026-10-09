"""Chapter 31: the forward-deployed field kit. Offline: the brief drafting uses the
scripted model; everything else is deterministic."""
from dataclasses import replace

import pytest
from fakemodel import MODEL, thinking, tool


@pytest.fixture
def f(ws):
    import ch31_field as m
    return m


def test_vague_brief_names_every_gap(f):
    problems = " | ".join(f.check_brief(f.VAGUE_BRIEF))
    for gap in ("isn't measurable", "no baseline", "no target", "no customer owner",
                "no non-goals"):
        assert gap in problems
    assert f.check_brief(f.BRIEF) == []


def test_brief_target_must_improve_and_baseline_needs_a_method(f):
    worse = replace(f.BRIEF, metric=f.Metric("minutes per file", "minutes", 18, 20, "time study"))
    assert any("no better" in p for p in f.check_brief(worse))
    unmeasured = replace(f.BRIEF, metric=f.Metric("minutes per file", "minutes", 18, 9))
    assert any("no method" in p for p in f.check_brief(unmeasured))
    up = replace(f.BRIEF, metric=f.Metric("files per day", "files", 20, 30, "logs",
                                          higher_is_better=True))
    assert f.check_brief(up) == []


def test_slices_rank_and_reject_with_reasons(f):
    ok, rejected = f.rank_slices(f.SLICES, f.ENV.blocked())
    assert ok[0].name == "Summarize a claim file for the adjuster"
    assert round(f.score(ok[0]), 1) == 106.7
    why = {s.name: w for s, w in rejected}
    assert "core_system_write" in why["Approve small claims automatically"][0]
    assert "email_customers" in why["Draft the letter to the customer"][0]
    assert "isn't ready" in why["Flag missing documents at intake"][0]


def test_write_access_unblocks_core_writes(f):
    env = replace(f.ENV, write_access=True)
    assert "core_system_write" not in env.blocked() and "email_customers" in env.blocked()


def test_draft_design_breaks_every_rule_and_fixed_design_none(f):
    rules = {v.rule for v in f.check_design(f.DRAFT_DESIGN, f.ENV)}
    assert rules == {"sign-in", "model hosting", "egress", "personal data in logs",
                     "retention", "residency", "write access", "audit"}
    assert f.check_design(f.FIXED_DESIGN, f.ENV) == []


def test_pilot_gate_hold_promote_stop(f):
    g2 = f.pilot_gate(f.WEEK_2)
    assert g2["decision"] == "hold" and "only 40 runs" in g2["reasons"][0]
    g6 = f.pilot_gate(f.WEEK_6)
    assert g6["decision"] == "promote" and g6["interval"][0] >= 0.85
    assert round(g6["gain"], 2) == 0.42
    leak = replace(f.WEEK_6, critical=1)
    assert f.pilot_gate(leak)["decision"] == "stop"
    poor = replace(f.WEEK_6, successes=100)                     # 62%: even hi < 85%
    assert f.pilot_gate(poor)["decision"] == "stop"
    slow = replace(f.WEEK_6, p95_s=12.0, metric_now=16.0)
    g = f.pilot_gate(slow)
    assert g["decision"] == "hold" and len(g["reasons"]) == 2
    assert f.next_stage("pilot", "promote") == "general release"
    assert f.next_stage("pilot", "hold") == "pilot"
    assert f.next_stage("general release", "promote") == "general release"


def test_handoff_and_productize(f):
    gaps = f.handoff_gaps(f.HANDOFF_PACK)
    assert [g.split(":")[0] for g in gaps] == ["escalation", "training"]
    assert f.handoff_gaps({k: "x" for k in f.HANDOFF}) == []
    rows = f.productize(f.FIELD_FIXES)
    assert rows[0]["capability"] == "ocr for scanned pdfs" and rows[0]["customers"] == 3
    assert rows[0]["verdict"].startswith("build")
    assert all(r["verdict"].startswith("keep") for r in rows[1:])


def test_draft_brief_is_a_forced_tool_call_and_code_still_checks(f, model):
    model.reset([[thinking(), tool("record_brief", {
        "users": "claims adjusters", "job": "read claim files", "output": "a summary",
        "metric_name": "minutes to summarize a claim file", "unit": "minutes",
        "baseline": None, "target": None, "measured_how": "",
        "customer_owner": "Anna Weber", "constraints": ["data stays in the EU"],
        "non_goals": ["emailing customers"], "risks": [],
        "open_questions": ["How long does a file take today, measured?"]})]])
    brief, questions = f.draft_brief(f.NOTES, "Lakeside Insurance")
    call = model.calls[0]
    assert call["tool_choice"] == {"type": "tool", "name": "record_brief"}
    assert "<notes>" in call["messages"][0]["content"]
    problems = f.check_brief(brief)
    assert any("no baseline" in p for p in problems) and any("no target" in p for p in problems)
    assert questions == ["How long does a file take today, measured?"]


def test_exercise_solutions(ws, model):
    import ex31_2_your_brief as e2, ex31_3_prompt_rule as e3, ex31_4_runs_needed as e4
    assert e2.check_brief(e2.BRIEF) == [] and len(e2.check_brief(e2.VAGUE)) >= 4
    import ch31_field as f
    others = [c for c in f.FIXED_DESIGN if c.name != "agent service"]
    assert {v.rule for v in e3.check_all(others + [e3.AGENT], f.ENV)} == {"personal data to the model"}
    assert "diagnosis" in e3.check_all(others + [e3.REDACTED], f.ENV)[0].detail
    assert e3.check_all(others + [e3.IN_VPC], f.ENV) == []
    n = e4.runs_needed(37, 40)
    assert n and e4.wilson(round(37 / 40 * n), n)[0] >= 0.85
    assert e4.wilson(round(37 / 40 * (n - 1)), n - 1)[0] < 0.85
    assert e4.runs_needed(42, 50) is None
