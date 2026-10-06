"""Chapter 25.11: the agent risk model, and exercise 25.7's launch gate. Offline."""
import pytest


@pytest.fixture
def risk(ws):
    import ch25_risk
    return ch25_risk


def profile(c=1, a=1, x=1, p=1, b=1):
    return dict(capability=c, autonomy=a, access=x, persistence=p, blast_radius=b)


def test_score_multiplies_the_five_factors(risk):
    assert risk.risk_score(profile()) == 1
    assert risk.risk_score(profile(3, 3, 3, 3, 3)) == 243
    assert risk.risk_score(profile(2, 2, 3, 3, 3)) == 108


@pytest.mark.parametrize("bad", [0, 4, None, "3", 2.5])
def test_factors_must_be_1_to_3(risk, bad):
    with pytest.raises(ValueError):
        risk.risk_score(profile(c=bad))
    with pytest.raises(ValueError):
        risk.risk_score({"capability": 1})                      # missing factors


def test_tier_bounds(risk):
    assert [risk.tier(s) for s in (1, 8, 9, 27, 28, 81, 82, 243)] == [1, 1, 2, 2, 3, 3, 4, 4]
    with pytest.raises(ValueError):
        risk.tier(244)


def test_cutting_any_one_factor_divides_the_score(risk):
    high = profile(3, 3, 3, 3, 3)
    for factor in risk.FACTORS:
        assert risk.risk_score({**high, factor: 1}) == 81       # whichever factor you cut


def test_controls_grow_with_the_tier(risk):
    low = risk.required_controls(profile())
    assert low == ["owner", "evals", "audit_log"]
    moderate = risk.required_controls(profile(2, 2, 2))         # 8 -> still tier 1
    assert moderate == low
    tier2 = risk.required_controls(profile(2, 2, 2, 2))         # 16
    assert set(low) < set(tier2) and "threat_model" in tier2 and "approval_gate" not in tier2
    critical = risk.required_controls(profile(3, 3, 3, 3, 3))
    assert {"red_team", "sandbox", "step_up", "review_weekly"} <= set(critical)
    assert "review_monthly" not in critical                     # weekly replaces monthly
    assert all(c in risk.CONTROLS for c in critical)


def test_a_factor_at_3_adds_its_controls_whatever_the_total(risk):
    spends = profile(x=3)                                       # score 3, tier 1
    assert risk.tier(risk.risk_score(spends)) == 1
    assert {"approval_gate", "scoped_tokens"} <= set(risk.required_controls(spends))
    assert "sandbox" in risk.required_controls(profile(c=3))
    assert "memory_gate" in risk.required_controls(profile(p=3))
    assert "red_team" in risk.required_controls(profile(b=3))


def test_gaps_lists_only_what_is_missing(risk):
    p = profile(x=3)
    assert risk.gaps(p, risk.required_controls(p)) == []
    assert risk.gaps(p, ["owner", "evals", "audit_log", "scoped_tokens"]) == ["approval_gate"]


def test_book_agents_score_as_the_chapter_says(risk):
    scores = {name: (risk.risk_score(p), risk.tier(risk.risk_score(p))) for name, p in risk.AGENTS.items()}
    assert list(scores.values()) == [(1, 1), (12, 2), (108, 4)]
    support = risk.AGENTS["support agent with refunds (case study)"]
    safer = {**support, "autonomy": 1}
    assert (risk.risk_score(safer), risk.tier(risk.risk_score(safer))) == (54, 3)
    assert len(risk.required_controls(support)) == 17 and len(risk.required_controls(safer)) == 14


def test_demo_runs_offline(risk, capsys):
    import runpy
    runpy.run_module("ch25_risk", run_name="__main__")
    out = capsys.readouterr().out
    assert "= 108  tier 4 (critical)" in out and "=  54  tier 3 (high)" in out


def test_exercise_launch_gate(ws, capsys):
    import ex25_7_launch as ex
    ok, missing = ex.can_launch(ex.CODING_AGENT, ex.IN_PLACE)
    assert not ok and "approval_gate" in missing and "kill_switch" in missing
    import ch25_risk
    ok, missing = ex.can_launch(ex.CODING_AGENT, ch25_risk.required_controls(ex.CODING_AGENT))
    assert ok and missing == []
    rows = {f: (s, t) for f, s, t in ex.cuts(ex.CODING_AGENT)}
    assert "persistence" not in rows                            # already at 1
    assert rows["autonomy"] == (18, 2) and rows["blast_radius"] == (27, 2)
    # Re-score on change: adding long-term memory reopens the gate.
    remembered = {**ex.CODING_AGENT, "persistence": 3}
    assert not ex.can_launch(remembered, ch25_risk.required_controls(ex.CODING_AGENT))[0]
    import runpy
    runpy.run_module("ex25_7_launch", run_name="__main__")
    assert "Launch allowed: False" in capsys.readouterr().out
