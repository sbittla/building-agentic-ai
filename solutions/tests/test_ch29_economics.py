"""Chapter 29.9: agent economics. Offline: pure arithmetic."""
import math
from dataclasses import replace

import pytest


@pytest.fixture
def econ(ws):
    import ch29_economics as e
    return e


def test_token_cost_uses_the_router_prices(econ):
    from ch20_router import PRICES
    price_in, price_out = PRICES["claude-sonnet-5"]
    assert econ.token_cost(1_000_000, 0) == pytest.approx(price_in)
    assert econ.token_cost(0, 1_000_000) == pytest.approx(price_out)


def test_rates_and_per_unit_costs(econ):
    a = econ.Assumptions()
    assert econ.escalation_rate(a) == pytest.approx(0.32)
    assert econ.success_rate(a) == pytest.approx(0.65)
    running = sum(econ.running_cost_per_month(a).values())
    assert econ.cost_per_task(a) == pytest.approx(running / 18_000)
    assert econ.cost_per_successful_task(a) == pytest.approx(running / (18_000 * 0.65))
    assert econ.cost_per_successful_task(a) > econ.cost_per_task(a)
    assert econ.cost_per_user_per_month(a) == pytest.approx(running / 12_000)


def test_business_case_numbers_in_the_book(econ):
    c = econ.business_case()
    assert round(c["running"]["tokens"]) == 167
    assert round(c["people"]["escalations"]) == 23_040
    assert round(c["failures"]) == 13_500
    assert round(c["with_agent"]) == 41_941 and round(c["baseline"]) == 81_000
    assert round(c["net"]) == 39_059
    assert c["payback_months"] == pytest.approx(150_000 / c["net"])
    assert round(c["payback_months"], 1) == 3.8
    assert round(c["hours_saved"]) == 1_204


def test_baseline_is_people_not_zero(econ):
    a = econ.Assumptions()
    c = econ.business_case(a)
    assert c["baseline"] == pytest.approx(18_000 * 6 * 40 / 60 + 18_000 * 0.02 * 25)
    worse = econ.business_case(replace(a, human_failure_rate=0.0))
    assert worse["net"] == pytest.approx(c["net"] - 9_000)


def test_no_saving_means_no_payback(econ):
    a = replace(econ.Assumptions(), automation_rate=0.05, failure_rate=0.05)
    c = econ.business_case(a)
    assert c["net"] < 0 and math.isinf(c["payback_months"])
    assert math.isinf(econ.cost_per_successful_task(a))


def test_invalid_rates_are_refused(econ):
    with pytest.raises(ValueError):
        econ.Assumptions(automation_rate=0.02, failure_rate=0.03)


def test_break_even_points(econ):
    a = econ.Assumptions()
    auto = econ.break_even(a, "automation_rate", a.failure_rate, 1.0)
    fail = econ.break_even(a, "failure_rate", 0.0, a.automation_rate)
    assert round(auto, 2) == 0.13 and round(fail, 3) == 0.117
    assert abs(econ.business_case(replace(a, failure_rate=fail))["net"]) < 1
    assert econ.break_even(a, "infra_per_month", 0, 1_000) is None   # never breaks even


def test_sensitivity_ranks_the_baseline_first_and_tokens_last(econ):
    rows = econ.sensitivity()
    names = [r["assumption"] for r in rows]
    assert names[0] == "human_minutes"
    assert names.index("automation_rate") < names.index("failure_rate")
    assert names.index("model_cost_per_turn") > names.index("upkeep_per_month")
    assert all(rows[i]["swing"] >= rows[i + 1]["swing"] for i in range(len(rows) - 1))
    top = rows[0]
    assert round(top["low"], 1) == 6.1 and round(top["high"], 1) == 2.8
    users = next(r for r in rows if r["assumption"] == "users_per_month")
    assert users["swing"] == 0


def test_exercise_cheap_model_only_pays_with_equal_failures(ws, capsys):
    import ex29_8_model_swap as ex
    f = ex.equal_net_failure_rate()
    assert 0.03 < f < 0.031
    from ch29_economics import business_case
    assert business_case(ex.haiku(f))["net"] == pytest.approx(
        business_case(ex.SONNET)["net"], abs=0.01)
    nets = [c["net"] for _, c in ex.rows()]
    assert nets[1] > nets[0] > nets[2] > nets[3] > nets[4]
