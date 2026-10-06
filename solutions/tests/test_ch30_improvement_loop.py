"""Chapter 30.14: the agent improvement loop, and exercise 30.12. Offline: fake agents."""
import json
import subprocess
import sys

import pytest


@pytest.fixture
def loop(ws):
    import ch30_improvement_loop as m
    saved = m.shadow
    yield m
    m.shadow = saved


@pytest.fixture
def world(loop):
    v14, v15, v16 = loop.releases()
    production = [loop.serve(v14, r) for r in loop.traffic(200, seed=1)]
    return v14, v15, v16, production


def turn(loop, current, candidate, production, suite=None, gates=None):
    return loop.improvement_turn(current, candidate, production, suite or loop.SUITE,
                                 loop.traffic(100, seed=2), loop.traffic(400, seed=3),
                                 gates or loop.GATES)


def test_mining_classifies_with_the_taxonomy(loop, world):
    *_, production = world
    failures = loop.mine_failures(production)
    assert failures and all(not r["eval"]["passed"] for r in production
                            if r["trace_id"] in {f["trace_id"] for f in failures})
    classes = {c for f in failures for c in f["classes"]}
    assert {"infinite_loop", "tool_failure", "hallucination", "misread_result"} <= classes
    assert sum(not r["eval"]["passed"] for r in production) == len(failures)


def test_cases_are_deduplicated_labeled_and_skip_the_suite(loop, world):
    *_, production = world
    failures = loop.mine_failures(production)
    cases, skipped = loop.to_cases(failures, loop.SUITE)
    assert len(cases) == 3 and skipped["duplicate"] == len(failures) - 3
    keys = {loop.normalize(c["question"]) for c in cases}
    assert "how many orders were cancelled" in keys                 # variants merged
    assert all(c["failure_classes"] and c["source"] and c["expect"] for c in cases)
    assert all(c["id"].startswith(c["failure_classes"][-1]) for c in cases)
    again, skipped = loop.to_cases(failures, loop.SUITE + cases)
    assert again == [] and skipped["duplicate"] == len(failures)


def test_unlabeled_failures_wait_for_review(loop):
    f = [{"trace_id": "t", "question": "q?", "classes": ["misread_result"],
          "expect": None, "needs_label": True}]
    assert loop.to_cases(f, []) == ([], {"duplicate": 0, "needs_label": 1})


def test_normalize_and_stable_routing(loop):
    assert loop.normalize(" How many  orders were CANCELLED ?") == \
        "how many orders were cancelled"
    picks = [loop.routed_to_candidate(f"req-{i}", 0.10) for i in range(2000)]
    assert picks == [loop.routed_to_candidate(f"req-{i}", 0.10) for i in range(2000)]
    assert 0.07 < sum(picks) / len(picks) < 0.13


def test_good_candidate_is_promoted_with_evidence(loop, world):
    v14, v15, _, production = world
    t = turn(loop, v14, v15, production)
    assert t["decision"] == "promote" and t["stopped_at"] is None
    assert [s["stage"] for s in t["stages"]] == ["offline", "shadow", "canary"]
    off, sh, can = t["stages"]
    assert off["baseline"]["rate"] == pytest.approx(0.7) and off["candidate"]["rate"] == 1
    assert off["fixed"] == 1 and off["broken"] == [] and not off["gate"]["block"]
    assert sh["worse"] == 0 and sh["better"] > 0
    assert sh["shown"] == [v14(r["question"]) for r in loop.traffic(100, seed=2)]
    assert can["candidate"]["runs"] >= loop.GATES["canary_min_runs"]
    assert can["candidate"]["burn"] == 0 and can["control"]["burn"] > 1
    assert len(t["suite"]) == len(loop.SUITE) + 3
    rec = loop.evidence(t)
    json.dumps(rec)                                                  # JSON-ready
    assert rec["decision"] == "promote" and set(rec["stages"]) == {"offline", "shadow",
                                                                   "canary"}


def test_slow_candidate_rolls_back_at_canary(loop, world):
    v14, _, v16, production = world
    t = turn(loop, v14, v16, production)
    assert t["decision"] == "rollback" and t["stopped_at"] == "canary"
    assert any("p95" in r for r in t["reasons"])


def test_candidate_that_breaks_an_old_case_is_rejected_offline(loop, world):
    v14, *_, production = world
    bad = loop.FakeAgent("support-agent 1.5-bad", wrong={
        "How many customers do we have?": "We have 30 customers."})
    t = turn(loop, v14, bad, production)
    assert t["decision"] == "reject" and t["stopped_at"] == "offline"
    off = t["stages"][0]
    assert off["broken"] == ["how-many-customers-do"]
    assert len(t["stages"]) == 1                     # never reached shadow or users
    assert len(t["suite"]) == len(loop.SUITE) + 3    # the mined cases are kept anyway


def test_a_fixed_failure_cannot_come_back(loop, world):
    v14, v15, _, production = world
    first = turn(loop, v14, v15, production)
    relapse = loop.FakeAgent("support-agent 1.7", wrong={
        "What was revenue in March?": "Revenue in March was $48,210."})
    t = loop.offline_eval(v15, relapse, first["suite"], [])
    assert not t["passed"] and t["broken"] == [
        c["id"] for c in first["new_cases"] if c["failure_classes"] == ["hallucination"]]


def test_shadow_rejects_a_worse_candidate_without_showing_it(loop):
    v14, v15, _ = loop.releases()
    reqs = loop.traffic(100, seed=2)
    s = loop.shadow(v15, v14, reqs)
    assert not s["passed"] and s["worse"] > 0
    assert s["shown"] == [v15(r["question"]) for r in reqs]


def test_canary_holds_when_too_few_runs(loop):
    v14, v15, _ = loop.releases()
    c = loop.canary(v14, v15, loop.traffic(50, seed=3))
    assert not c["passed"] and c["hold"] and c["reasons"] == ["too few runs to tell"]


def test_demo_runs(loop, ws):
    out = subprocess.run([sys.executable, "ch30_improvement_loop.py"], cwd=ws,
                         capture_output=True, text=True, check=True).stdout
    assert "decision  PROMOTE" in out and "decision  ROLLBACK" in out
    assert len(json.load(open(ws / "release_decisions.json"))) == 2


# ------------------------------------------------------------ exercise 30.12
def test_ex30_12_slow_candidate_rejected_in_shadow(loop):
    import ex30_12_shadow_slos as ex
    _, v15, v16 = loop.releases()
    good, slow = ex.run([v15, v16])
    assert good["decision"] == "promote"
    assert slow["decision"] == "reject" and slow["stopped_at"] == "shadow"
    assert any("p95" in r for r in slow["reasons"])
    assert loop.shadow is ex.PLAIN_SHADOW                          # restored


def test_ex30_12_rejects_a_costlier_candidate(loop):
    import ex30_12_shadow_slos as ex
    cheap = loop.FakeAgent("cheap", model="claude-haiku-4-5")
    pricey = loop.FakeAgent("pricey", model="claude-sonnet-5")
    s = ex.shadow_with_slos(cheap, pricey, loop.traffic(60, seed=4))
    assert not s["passed"] and s["cost_rise"] > ex.MAX_COST_RISE
    assert any("more per task" in r for r in s["reasons"])
