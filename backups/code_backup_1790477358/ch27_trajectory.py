"""Chapter 27: evaluating the trajectory, not just the answer. A right answer reached by
deleting rows, guessing, or calling the same failing tool ten times is not a success.
Every run gets three scores:

  * outcome   did it reach the goal? (the Chapter 27 checks on the answer and the data)
  * process   did it get there the right way? (tools, order, arguments, recovery, steps)
  * cost      what did it spend? (tokens and dollars, for cost per successful task)

Plus a regression gate for CI, and sampling for continuous evaluation in production.

    ./course.sh python ch27_trajectory.py            run eval_trajectory.jsonl once"""
import json
import math
import random
import re
import sys

from ch04_agent import run_agent
from ch20_router import cost
from ch27_eval import check as check_outcome, db_fingerprint, wilson

# ------------------------------------------------------------ 1. the trajectory
def trajectory(messages: list) -> list[dict]:
    """The steps the agent took: each tool call with its arguments and whether the
    result was an error. Built from the conversation, so any run can be graded."""
    results = {}
    for m in messages:
        if m["role"] == "user" and isinstance(m["content"], list):
            for b in m["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    results[b["tool_use_id"]] = b
    steps = []
    for m in messages:
        if m["role"] != "assistant":
            continue
        for b in m["content"]:
            if getattr(b, "type", "") == "tool_use":
                r = results.get(b.id, {})
                steps.append({"tool": b.name, "args": b.input,
                              "error": bool(r.get("is_error")),
                              "result": str(r.get("content", ""))[:200]})
    return steps

# ------------------------------------------------------------ 2. checking the process
def _in_order(names: list[str], expected: list[str]) -> bool:
    it = iter(names)
    return all(any(n == e for n in it) for e in expected)    # a subsequence

def check_process(case: dict, steps: list[dict]) -> list[str]:
    names, failures = [s["tool"] for s in steps], []
    if (seq := case.get("expect_sequence")) and not _in_order(names, seq):
        failures.append(f"tools not called in the order {seq} (got {names})")
    for tool in case.get("forbidden_tools", []):
        if tool in names:
            failures.append(f"called forbidden tool {tool}")
    for rule in case.get("arg_checks", []):
        calls = [s for s in steps if s["tool"] == rule["tool"]]
        values = [str(c["args"].get(rule["arg"], "")) for c in calls]
        if "must_match" in rule and not any(re.search(rule["must_match"], v, re.I)
                                            for v in values):
            failures.append(f"no {rule['tool']} call with {rule['arg']} "
                            f"matching /{rule['must_match']}/")
        if "must_not_match" in rule and any(re.search(rule["must_not_match"], v, re.I)
                                            for v in values):
            failures.append(f"a {rule['tool']} call matched /{rule['must_not_match']}/")
    if "max_steps" in case and len(steps) > case["max_steps"]:
        failures.append(f"{len(steps)} tool calls > {case['max_steps']}")
    seen_errors = set()
    for s in steps:                                        # the same mistake twice
        key = (s["tool"], json.dumps(s["args"], sort_keys=True))
        if s["error"] and key in seen_errors:
            failures.append(f"repeated a failing call to {s['tool']}")
            break
        if s["error"]:
            seen_errors.add(key)
    if case.get("must_recover") and steps and steps[-1]["error"]:
        failures.append("ended on an error without recovering")
    return failures

def tool_overlap(steps: list[dict], reference: list[str]) -> dict:
    """Precision and recall of the tools used against a reference trajectory."""
    used, ref = [s["tool"] for s in steps], list(reference)
    hits = sum(min(used.count(t), ref.count(t)) for t in set(ref))
    return {"precision": hits / len(used) if used else 1.0,
            "recall": hits / len(ref) if ref else 1.0}

# ------------------------------------------------------------ 3. one graded run
def grade(case, tools, run_tool, system, model=None) -> dict:
    before = db_fingerprint() if case.get("db_unchanged") else None
    answer, messages, stats = run_agent(case["question"], tools, run_tool,
                                        system=system, verbose=False, model=model)
    steps = trajectory(messages)
    outcome = check_outcome(case, answer, messages, before)
    process = check_process(case, steps)
    return {"id": case["id"], "outcome": not outcome, "process": not process,
            "pass": not outcome and not process, "failures": outcome + process,
            "steps": len(steps), "cost": cost(stats), "answer": answer,
            "trajectory": steps}

# ------------------------------------------------------------ 4. a regression gate
def gate(baseline: list[bool], candidate: list[bool], max_drop: float = 0.0) -> dict:
    """Block a change when the candidate is worse than the baseline by more than noise:
    a one-sided two-proportion test at about 95%. Small suites can't see small drops,
    which is why the gate also reports both confidence intervals."""
    n1, n2 = len(baseline), len(candidate)
    p1, p2 = sum(baseline) / n1, sum(candidate) / n2
    pooled = (sum(baseline) + sum(candidate)) / (n1 + n2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2)) or 1e-9
    z = (p1 - p2 - max_drop) / se
    return {"baseline": p1, "candidate": p2, "z": round(z, 2),
            "ci_baseline": wilson(sum(baseline), n1),
            "ci_candidate": wilson(sum(candidate), n2),
            "block": z > 1.645}

# ------------------------------------------------------------ 5. continuous evaluation
def sample_for_review(runs: list[dict], rate: float = 0.05, seed: int = 0) -> list:
    """Production runs to grade later: every failure the guards or the user flagged,
    plus a random share of the rest, so quality is measured on real traffic."""
    rng = random.Random(seed)
    return [r for r in runs if r.get("flagged") or rng.random() < rate]

def drift(daily_pass_rates: list[float], window: int = 7, drop: float = 0.1) -> bool:
    """Alert when the latest day is well below the recent average."""
    if len(daily_pass_rates) <= window:
        return False
    recent = daily_pass_rates[-window - 1:-1]
    return daily_pass_rates[-1] < sum(recent) / len(recent) - drop

if __name__ == "__main__":
    import ch08_sql_tools as sql
    path = sys.argv[1] if len(sys.argv) > 1 else "eval_trajectory.jsonl"
    cases = [json.loads(line) for line in open(path) if line.strip()]
    results = [grade(c, sql.TOOLS, sql.run_tool, sql.SYSTEM) for c in cases]
    for r in results:
        print(f"{r['id']:<22} outcome {'ok ' if r['outcome'] else 'BAD'} process "
              f"{'ok ' if r['process'] else 'BAD'} {r['steps']} steps "
              f"${r['cost']:.4f}  {'; '.join(r['failures'])}")
    wins = [r for r in results if r["pass"]]
    spent = sum(r["cost"] for r in results)
    print(f"\n{len(wins)}/{len(results)} passed both; cost per successful task "
          f"${spent / len(wins):.4f}" if wins else "\nNo run passed both.")
