"""Chapter 21.10: coordination economics. Offline: hand-made stats and the simulator."""
import pytest


@pytest.fixture
def co(ws):
    import ch21_coordination as co
    return co


def run(ok=True, **kw):
    return {"ok": ok, "steps": 3, "input_tokens": 1000, "output_tokens": 100,
            "latency_s": 4.0, "cost": 0.004, **kw}


def test_normalize_accepts_run_agent_and_benchmark_shapes(co):
    a = co.normalize({"steps": 2, "input_tokens": 10, "output_tokens": 5, "ok": True,
                      "latency_s": 1.5, "cost": 0.01})
    b = co.normalize({"steps": 2, "tokens_in": 10, "tokens_out": 5, "ok": True,
                      "ms": 1500, "cost": 0.01})
    assert a == b and a["calls"] == 2 and a["messages"] == 0
    priced = co.normalize({"steps": 1, "input_tokens": 1_000_000, "output_tokens": 0,
                           "model": "claude-haiku-4-5"})
    assert priced["cost"] == pytest.approx(1.00) and priced["ok"] is False


def test_report_measures_each_overhead_term(co):
    single = [run() for _ in range(10)]
    team = [run(steps=8, input_tokens=2500, latency_s=6.0, cost=0.009, lead_calls=2,
                messages=6, duplicated_tokens=400, retries=1,
                worker_latency_s=[1.0, 2.0, 3.0]) for _ in range(10)]
    o = co.coordination_report(single, team)["overhead"]
    assert o["extra_calls"] == 5 and o["lead_calls"] == 2 and o["messages"] == 6
    assert o["extra_input_tokens"] == 1500 and o["duplicated_tokens"] == 400
    assert o["sync_wait_s"] == pytest.approx(1.0)        # slowest 3.0 minus mean 2.0
    assert o["extra_retries"] == 1 and o["extra_latency_s"] == pytest.approx(2.0)
    assert o["extra_cost_per_task"] == pytest.approx(0.005)
    assert o["cost_ratio"] == pytest.approx(2.25)


def test_decide_requires_a_measurable_gain_worth_its_cost(co):
    single = [run(ok=i < 60) for i in range(100)]           # 60%
    team = [run(ok=i < 90, cost=0.014) for i in range(100)]  # 90%, +$0.01 per task
    r = co.coordination_report(single, team)
    worth = co.decide(r, value_per_success=0.10)             # 0.30 x $0.10 = $0.03 > $0.01
    assert worth["verdict"] == "team" and worth["break_even_value"] == pytest.approx(0.01 / 0.3)
    assert co.decide(r, value_per_success=0.02)["verdict"] == "single agent"
    small = co.coordination_report([run(ok=i < 28) for i in range(30)],
                                   [run(ok=i < 29, cost=0.008) for i in range(30)])
    d = co.decide(small, value_per_success=100.0)            # huge value, but no evidence
    assert d["verdict"] == "single agent" and "overlap" in d["reason"]


def test_decide_a_requirement_only_one_design_meets(co):
    single = [run(latency_s=20.0) for _ in range(20)]
    team = [run(latency_s=12.0, cost=0.02) for _ in range(20)]
    r = co.coordination_report(single, team)
    assert co.decide(r, 0.0, latency_slo_s=15)["verdict"] == "team"
    assert co.decide(r, 0.0, latency_slo_s=25)["verdict"] == "single agent"  # both meet it
    assert co.decide(co.coordination_report(team, single), 1.0,
                     latency_slo_s=15)["verdict"] == "single agent"


def test_failure_propagation(co):
    f = co.failure_propagation(0.9, 3)
    assert f["p_task"] == pytest.approx(0.729)
    assert f["share_of_parts"] == pytest.approx((0.9 + 0.81 + 0.729) / 3)
    contained = co.failure_propagation(0.9, 3, parallel=True, lead_steps=2)
    assert contained["p_task"] == pytest.approx(0.81 * 0.729)
    assert contained["share_of_parts"] == pytest.approx(0.81 * 0.9)
    crash = co.failure_propagation(0.9, 3, parallel=True, contained=False, retries=5)
    assert crash["p_step"] == 0.9 and crash["share_of_parts"] == pytest.approx(0.729)
    retried = co.failure_propagation(0.9, 3, parallel=True, retries=1)
    assert retried["p_step"] == pytest.approx(0.99)


def test_simulated_runs_match_section_29_8(co):
    single, team = co.simulated_runs(False)
    r = co.coordination_report(single, team)
    assert r["single"]["tasks"] == 100 and r["single"]["success"] == r["team"]["success"] == 0.97
    assert r["overhead"]["lead_calls"] == 2 and r["overhead"]["messages"] == 2
    assert r["overhead"]["extra_calls"] == pytest.approx(2.0)
    assert co.decide(r, 0.05)["verdict"] == "single agent"
    single, team = co.simulated_runs(True)
    o = co.coordination_report(single, team)["overhead"]
    assert o["duplicated_tokens"] > 0 and o["sync_wait_s"] > 0 and o["cost_ratio"] > 2


def test_illustrative_fallback_has_the_same_shape(co):
    single, team = co.illustrative_runs(True)
    r = co.coordination_report(single, team)
    assert r["single"]["tasks"] == 30 and r["single"]["success"] == pytest.approx(28 / 30)


def test_exercise_21_7(ws):
    import ex21_7_team_economics as ex
    rows = ex.sweep(tool_ms=(1000, 2000, 3000))
    assert ex.crossover(rows) == 2000
    assert ex.crossover(rows, "parallel_p95") is None
    assert all(r["extra_cost"] > 0 for r in rows)
    assert ex.max_workers() == 5 and ex.max_workers(retries=1) == 180
