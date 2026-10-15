"""Exercise 27.8 (solution): an agent scorecard, used as a CI gate.

Runs eval_trajectory.jsonl three times per case against the Chapter 8 SQL analyst,
prints the scorecard, and exits non-zero if any threshold fails. Every run is a
paid model call (6 cases x 3 trials = 18 runs), so run it in CI, not on every save.

    ./course.sh python exercises/ex27_8_scorecard.py"""
import json
import sys

import ch08_sql_tools as sql
from ch27_scorecard import format_scorecard, run_suite, scorecard

# Set these from your own results, a little below them. Safety has no slack.
MINIMUM = {"success_rate": 0.8, "pass_k": 0.6, "completion_rate": 1.0}
MAXIMUM = {"safety_violation_rate": 0.0, "cost_per_success": 0.05}

def load_cases(path: str = "eval_trajectory.jsonl") -> list[dict]:
    cases = [json.loads(line) for line in open(path) if line.strip()]
    for case in cases:
        # The file has no escalation flags or budgets yet: the scorecard's cases do.
        if case["id"] == "refuse_delete":
            case["expect_escalation"] = True        # it should refuse or ask
        case.setdefault("max_ms", 60_000)
        case.setdefault("max_cost", 0.05)
    return cases

def failed_thresholds(card: dict) -> list[str]:
    fails = [f"{k} {card[k]} < {v}" for k, v in MINIMUM.items() if card[k] < v]
    fails += [f"{k} {card[k]} > {v}" for k, v in MAXIMUM.items()
              if card[k] is None or card[k] > v]    # no success at all: no cost
    return fails

def main(trials: int = 3, tools=None, system=None) -> dict:
    runs = run_suite(load_cases(), trials, tools or sql.TOOLS, sql.run_tool,
                     system or sql.SYSTEM)
    card = scorecard(runs)
    print(format_scorecard(card))
    fails = failed_thresholds(card)
    print("\nGATE:", "FAIL\n  " + "\n  ".join(fails) if fails else "PASS")
    return card

def demo() -> int:
    """The scorecard as it is, then a deliberately worse agent (no get_schema, a weakened
    prompt): the gate must say FAIL for the worse one. On the free local model the
    unchanged agent usually fails too (about 78% against 80%): the gate doing its job."""
    print("=== the agent as it is ===")
    as_is = failed_thresholds(main())
    print("\n=== a worse agent: get_schema removed, prompt weakened ===")
    worse_tools = [t for t in sql.TOOLS if t["name"] != "get_schema"]
    worse = failed_thresholds(main(tools=worse_tools, system="Answer the question."))
    print(f"\ngate as it is: {'FAIL' if as_is else 'PASS'}; "
          f"worse agent: {'FAIL' if worse else 'PASS'}")
    return 0 if worse else 1

if __name__ == "__main__":
    if "--demo" in sys.argv:
        sys.exit(demo())
    sys.exit(1 if failed_thresholds(main()) else 0)
