"""Exercise 25.7: a launch gate from the risk model.

Score the coding agent from exercise 25.1(a), which reads GitHub issues (untrusted text)
and pushes to the team's repository on its own. Refuse launch while any required control
is missing, then try cutting each factor to 1 and see which cuts lower the tier.
Offline: no model involved."""
from ch25_risk import CONTROLS, FACTORS, TIERS, gaps, required_controls, risk_score, tier

CODING_AGENT = dict(capability=3,    # runs tests and git: open-ended tools
                    autonomy=3,      # pushes without a person in the loop
                    access=3,        # writes to the repository, a system of record
                    persistence=1,   # each issue is a fresh run
                    blast_radius=2)  # the team's repository, not customers

IN_PLACE = ["owner", "evals", "audit_log", "threat_model", "budgets", "sandbox"]

def can_launch(profile: dict, controls_in_place) -> tuple[bool, list[str]]:
    """The gate: launch only when nothing is missing. Code decides, not a reviewer's mood."""
    missing = gaps(profile, controls_in_place)
    return not missing, missing

def cuts(profile: dict) -> list[tuple[str, int, int]]:
    """For each factor above 1: (factor, score with that factor at 1, tier then)."""
    rows = []
    for factor in FACTORS:
        if profile[factor] > 1:
            score = risk_score({**profile, factor: 1})
            rows.append((factor, score, tier(score)))
    return rows

if __name__ == "__main__":
    score = risk_score(CODING_AGENT)
    level = tier(score)
    print(f"Coding agent: {score}, tier {level} ({TIERS[level][0]}), "
          f"{len(required_controls(CODING_AGENT))} controls required")
    ok, missing = can_launch(CODING_AGENT, IN_PLACE)
    print(f"Launch allowed: {ok}")
    for control in missing:
        print(f"  missing {control:14} {CONTROLS[control]}")

    print("\nCut one factor to 1:")
    for factor, new_score, new_tier in cuts(CODING_AGENT):
        lower = " <- lower tier" if new_tier < level else ""
        print(f"  {factor:12} {score} -> {new_score:>3}, tier {new_tier}{lower}")

    # The cut that keeps the agent useful: it opens a pull request and a person merges.
    # The required merge review, enforced by branch protection, is its approval gate.
    reviewed = {**CODING_AGENT, "autonomy": 1}
    ok, missing = can_launch(reviewed, IN_PLACE + ["approval_gate"])
    print(f"\nWith a person merging every pull request: {risk_score(reviewed)}, "
          f"tier {tier(risk_score(reviewed))}; still missing: {', '.join(missing) or 'nothing'}")
