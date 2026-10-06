"""Exercise 29.8: does the cheaper model pay off for the business?

The simulator's E3 (section 29.8) measured Claude Haiku 4.5 at $0.0016 per task and
Claude Sonnet 5 at $0.0031, with success rates of 93% and 98%. Put both into the
support agent's business case and find how many extra failures wipe out the token
saving. Free: pure arithmetic on the assumptions."""
from dataclasses import replace

from ch29_economics import Assumptions, business_case

SONNET = Assumptions()                                   # $0.0031 per turn, 3% failures
HAIKU_PER_TURN = 0.0016                                  # simulator E3, $ per task


def haiku(failure_rate: float) -> Assumptions:
    return replace(SONNET, model_cost_per_turn=HAIKU_PER_TURN, failure_rate=failure_rate)


def equal_net_failure_rate() -> float:
    """The Haiku failure rate at which its net saving equals Sonnet's. The net is
    linear in the failure rate, so two points give the line exactly."""
    target = business_case(SONNET)["net"]
    lo, hi = SONNET.failure_rate, SONNET.failure_rate + 0.01
    n_lo, n_hi = business_case(haiku(lo))["net"], business_case(haiku(hi))["net"]
    return lo + (target - n_lo) * (hi - lo) / (n_hi - n_lo)


def rows():
    out = [("Sonnet 5, 3% failures", business_case(SONNET))]
    for f in (0.03, 0.04, 0.05, 0.06):
        out.append((f"Haiku 4.5, {f:.0%} failures", business_case(haiku(f))))
    return out


if __name__ == "__main__":
    print(f"{'Configuration':<26}{'tokens $/mo':>12}{'net $/mo':>10}{'payback':>9}")
    for name, c in rows():
        print(f"{name:<26}{c['running']['tokens']:>12,.0f}{c['net']:>10,.0f}"
              f"{c['payback_months']:>8.1f}m")
    f = equal_net_failure_rate()
    saved = (business_case(haiku(SONNET.failure_rate))["running"]["tokens"]
             - business_case(SONNET)["running"]["tokens"])
    print(f"\nHaiku saves ${-saved:,.0f} a month in tokens. Its net equals Sonnet's at a "
          f"failure rate of {f:.2%}: {(f - SONNET.failure_rate) * 100:.2f} points above "
          "Sonnet's 3%.\nAny model that fails noticeably more often costs the business "
          "more, however cheap its tokens: choose by cost per SUCCESS and failure cost.")
