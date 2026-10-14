"""Exercise 29.5 (solution): cost per successful task before and after two levers:
routing easy cases to the small model, and caching the stable prefix."""
import json
from pathlib import Path

import ch08_sql_tools as sql
from ch20_router import SMALL, by_rules
from ch27_eval import wilson
from ch27_trajectory import grade

CASES = Path("eval_trajectory.jsonl")

def cached_tools():
    """Prompt caching: mark the end of the stable tool list as cacheable."""
    tools = [dict(t) for t in sql.TOOLS]
    tools[-1]["cache_control"] = {"type": "ephemeral"}
    return tools

def run(cases, route=None, cache=False):
    tools = cached_tools() if cache else sql.TOOLS
    rows = [grade(c, tools, sql.run_tool, sql.SYSTEM,
                  model=route(c["question"]) if route else None) for c in cases]
    wins = sum(r["pass"] for r in rows)
    spent = sum(r["cost"] for r in rows)
    return {"pass_rate": wins / len(rows), "ci95": wilson(wins, len(rows)),
            "cost_per_success": spent / wins if wins else None, "runs": len(rows)}

def main(trials: int = 2):
    cases = [json.loads(l) for l in CASES.read_text().splitlines() if l.strip()] * trials
    before = run(cases)
    after = run(cases, route=by_rules, cache=True)
    print("before:", before, "\nafter: ", after)
    for label, r in (("before", before), ("after", after)):
        lo, hi = r["ci95"]
        cps = r["cost_per_success"]
        print(f"{label:<7} pass rate {r['pass_rate']:.0%} (95% CI {lo:.0%}-{hi:.0%}), "
              f"cost per success {'n/a' if cps is None else f'${cps:.4f}'}")
    overlap = after["ci95"][1] >= before["ci95"][0] and before["ci95"][1] >= after["ci95"][0]
    if not before["cost_per_success"] and not after["cost_per_success"]:
        print("Recommendation: can't decide on cost here: this model is free (the local "
              "model), so cost per success is $0 either way. Run on Claude to price the levers.")
    elif after["cost_per_success"] < before["cost_per_success"] and (
            after["pass_rate"] >= before["pass_rate"] or overlap):
        print("Recommendation: ship it: cheaper per success, and the pass rate didn't drop "
              "by more than the intervals can tell apart.")
    else:
        print("Recommendation: don't ship yet: the saving costs too much quality.")
    return before, after

if __name__ == "__main__":
    main()
