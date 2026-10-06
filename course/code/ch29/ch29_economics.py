"""Chapter 29: agent economics. Turn the cost per task you measured into a business
case: what the agent costs a month, what it saves against the people who do the work
today, how long it takes to pay back what it cost to build, and which assumption the
answer depends on most.

  * Assumptions     every number the case rests on, in one place, each one labeled
  * metrics         cost per task, per successful task, per user per month, human
                    minutes saved, automation, escalation and failure cost
  * business_case   monthly costs, savings, net and payback months
  * sensitivity     vary each assumption +/-20% and rank its effect on payback

Every default is an ASSUMPTION for the case study's support agent, except the model
cost per turn, which is the simulator's measured cost per task (section 29.8, E3).
Replace them with your own measurements and your finance team's figures.

    ./course.sh python ch29_economics.py        the support agent's business case"""
import textwrap
from dataclasses import dataclass, fields, replace

from ch20_router import PRICES

# ------------------------------------------------------------ 1. the assumptions
@dataclass(frozen=True)
class Assumptions:
    """One month of the support agent. Rates are shares of ALL conversations."""
    conversations_per_month: float = 18_000   # 600 a day (the case study)
    users_per_month: float = 12_000           # distinct customers who contact support
    turns_per_conversation: float = 3         # agent turns (questions) per conversation
    model_cost_per_turn: float = 0.0031       # $ per task, simulator E3, Sonnet, base
    tool_cost_per_conversation: float = 0.001  # paid APIs and retrieval queries
    infra_per_month: float = 400              # service, gateway, traces, vector store
    upkeep_per_month: float = 4_000           # people: evals, prompts, on-call share
    automation_rate: float = 0.68             # closed by the agent, no person involved
    failure_rate: float = 0.03                # closed by the agent, but wrongly
    human_minutes: float = 6                  # a person handling a whole conversation
    escalated_minutes: float = 6              # a takeover: no faster than from scratch
    review_share: float = 0.05                # automated conversations a person checks
    review_minutes: float = 2
    loaded_cost_per_hour: float = 40          # pay, benefits, tools and overhead
    failure_cost: float = 25                  # a wrong refund, a missed handoff, a fix
    human_failure_rate: float = 0.02          # people get some wrong too
    build_cost: float = 150_000               # one-time: engineering, evals, security

    def __post_init__(self):
        if not 0 <= self.failure_rate <= self.automation_rate <= 1:
            raise ValueError("need 0 <= failure_rate <= automation_rate <= 1")

# ------------------------------------------------------------ 2. the metrics
def token_cost(input_tokens: int, output_tokens: int,
               model: str = "claude-sonnet-5") -> float:
    """Dollars for the tokens of one call or run, at PRICES (Chapter 20)."""
    price_in, price_out = PRICES[model]
    return (input_tokens * price_in + output_tokens * price_out) / 1e6

def escalation_rate(a: Assumptions) -> float:
    """Every conversation the agent doesn't close goes to a person."""
    return 1 - a.automation_rate

def success_rate(a: Assumptions) -> float:
    """Conversations the agent closed AND got right."""
    return a.automation_rate - a.failure_rate

def running_cost_per_month(a: Assumptions) -> dict:
    """What running the agent costs: tokens, tools, infrastructure, and the people
    who keep it working (upkeep: evaluation, prompt changes, on-call)."""
    n = a.conversations_per_month
    return {"tokens": n * a.turns_per_conversation * a.model_cost_per_turn,
            "tools": n * a.tool_cost_per_conversation,
            "infra": a.infra_per_month, "upkeep": a.upkeep_per_month}

def cost_per_task(a: Assumptions) -> float:
    """Running cost per conversation, the fixed costs spread over the volume."""
    return sum(running_cost_per_month(a).values()) / a.conversations_per_month

def cost_per_successful_task(a: Assumptions) -> float:
    """Running cost per conversation the agent closed correctly: the failed and the
    escalated ones were paid for too, and buy no automation."""
    successes = a.conversations_per_month * success_rate(a)
    return (sum(running_cost_per_month(a).values()) / successes if successes > 0
            else float("inf"))

def cost_per_user_per_month(a: Assumptions) -> float:
    """Running cost per customer served: the number to compare with a seat price."""
    return sum(running_cost_per_month(a).values()) / a.users_per_month

def human_minutes_saved(a: Assumptions) -> float:
    """Minutes a month people no longer spend: the baseline minus the takeovers and
    the reviews. Failures cost money, counted in failure_cost, not here."""
    n = a.conversations_per_month
    baseline = n * a.human_minutes
    still_human = (n * escalation_rate(a) * a.escalated_minutes
                   + n * a.automation_rate * a.review_share * a.review_minutes)
    return baseline - still_human

def failure_cost_per_month(a: Assumptions, rate: float | None = None) -> float:
    """What wrong outcomes cost: far more per case than the model call that made it."""
    rate = a.failure_rate if rate is None else rate
    return a.conversations_per_month * rate * a.failure_cost

def payback_months(build_cost: float, net_per_month: float) -> float:
    """Months to earn back the build. Never, if the agent doesn't save money."""
    return build_cost / net_per_month if net_per_month > 0 else float("inf")

# ------------------------------------------------------------ 3. the business case
def business_case(a: Assumptions = Assumptions()) -> dict:
    """Monthly costs with the agent and with people alone (the baseline, not zero),
    the net saving and the payback in months."""
    n, rate = a.conversations_per_month, a.loaded_cost_per_hour / 60
    running = running_cost_per_month(a)
    people = {"escalations": n * escalation_rate(a) * a.escalated_minutes * rate,
              "review": n * a.automation_rate * a.review_share * a.review_minutes * rate}
    with_agent = sum(running.values()) + sum(people.values()) + failure_cost_per_month(a)
    baseline = (n * a.human_minutes * rate
                + failure_cost_per_month(a, a.human_failure_rate))
    net = baseline - with_agent
    return {"running": running, "people": people,
            "failures": failure_cost_per_month(a),
            "with_agent": with_agent, "baseline": baseline, "net": net,
            "payback_months": payback_months(a.build_cost, net),
            "cost_per_task": cost_per_task(a),
            "cost_per_success": cost_per_successful_task(a),
            "cost_per_user_month": cost_per_user_per_month(a),
            "automation": a.automation_rate, "escalation": escalation_rate(a),
            "hours_saved": human_minutes_saved(a) / 60}

def break_even(a: Assumptions, field_name: str, lo: float, hi: float,
               steps: int = 60) -> float | None:
    """The value of one assumption at which the monthly net is zero (bisection), or
    None if the net has the same sign at both ends."""
    def net(x):
        return business_case(replace(a, **{field_name: x}))["net"]
    if (net(lo) > 0) == (net(hi) > 0):
        return None
    for _ in range(steps):
        mid = (lo + hi) / 2
        if (net(mid) > 0) == (net(lo) > 0):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

# ------------------------------------------------------------ 4. sensitivity
RATES = {"automation_rate", "failure_rate", "review_share", "human_failure_rate"}

def _scaled(a: Assumptions, name: str, k: float) -> Assumptions | None:
    value = getattr(a, name) * k
    if name in RATES:
        value = min(value, 1.0)
    try:
        return replace(a, **{name: value})
    except ValueError:                        # e.g. failures above automation
        return None

def sensitivity(a: Assumptions = Assumptions(), factor: float = 0.2) -> list[dict]:
    """Payback with each assumption lowered and raised by `factor`, the others held,
    ranked by how far it moves (a tornado chart in numbers). Infinite paybacks rank
    first: that assumption can make the case fail."""
    rows = []
    for f in fields(a):
        low, high = _scaled(a, f.name, 1 - factor), _scaled(a, f.name, 1 + factor)
        if low is None or high is None:
            continue
        p_low = business_case(low)["payback_months"]
        p_high = business_case(high)["payback_months"]
        rows.append({"assumption": f.name, "low": p_low, "high": p_high,
                     "swing": abs(p_high - p_low)})
    return sorted(rows, key=lambda r: -r["swing"])

def format_case(case: dict) -> str:
    """The business case as a short monthly statement."""
    m, p = case["running"], case["people"]
    months = case["payback_months"]
    lines = [
        "Per month                       with the agent    people only",
        f"  tokens                        {m['tokens']:>12,.0f}",
        f"  tools and retrieval           {m['tools']:>12,.0f}",
        f"  infrastructure                {m['infra']:>12,.0f}",
        f"  upkeep                        {m['upkeep']:>12,.0f}",
        f"  people: escalations           {p['escalations']:>12,.0f}",
        f"  people: review                {p['review']:>12,.0f}",
        f"  failures                      {case['failures']:>12,.0f}",
        f"  total                         {case['with_agent']:>12,.0f}"
        f"   {case['baseline']:>12,.0f}",
        f"Net saving ${case['net']:,.0f} a month; payback "
        + (f"{months:.1f} months" if months != float("inf") else "never"),
        f"Cost per task ${case['cost_per_task']:.3f}, per successful task "
        f"${case['cost_per_success']:.3f}, per user per month "
        f"${case['cost_per_user_month']:.3f}",
        f"Automation {case['automation']:.0%}, escalation {case['escalation']:.0%}, "
        f"{case['hours_saved']:,.0f} hours of people's time saved a month"]
    return "\n".join(lines)

if __name__ == "__main__":
    a = Assumptions()
    print("The support agent's business case (assumptions: see Assumptions)\n")
    print(format_case(business_case(a)))
    auto = break_even(a, "automation_rate", a.failure_rate, 1.0)
    fail = break_even(a, "failure_rate", 0.0, a.automation_rate)
    print(f"\nBreak-even: automation {auto:.0%} (failures at {a.failure_rate:.0%}), "
          f"or failures {fail:.1%} (automation at {a.automation_rate:.0%})")
    print("\nPayback in months with each assumption -20% / +20%, biggest swing first:")
    rows = sensitivity(a)
    for r in rows:
        if r["swing"] >= 0.1:
            print(f"  {r['assumption']:<26} {r['low']:>5.1f}  {r['high']:>5.1f}")
    small = ", ".join(r["assumption"] for r in rows if r["swing"] < 0.1)
    print(textwrap.fill(f"under 0.1 months: {small}", 84, initial_indent="  ",
                        subsequent_indent="    "))
