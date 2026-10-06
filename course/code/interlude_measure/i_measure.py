"""Interlude (measuring): one run is an anecdote. Run every case several times, report the
pass rate with a margin of error, and call a change an improvement only when the margins
say so. No model needed: the demo agents are simulated, with a success rate you choose.

Run:  python i_measure.py"""
import json
import math
import random


def wilson(passes: int, runs: int, z: float = 1.96) -> tuple[float, float]:
    """The 95% interval for a pass rate (the Wilson score interval). Unlike passes/runs
    plus or minus a guess, it stays honest for small numbers and for rates near 0 or 100%."""
    if runs == 0:
        return 0.0, 1.0
    p = passes / runs
    centre = (p + z * z / (2 * runs)) / (1 + z * z / runs)
    half = z * math.sqrt(p * (1 - p) / runs + z * z / (4 * runs * runs)) / (1 + z * z / runs)
    return max(0.0, centre - half), min(1.0, centre + half)


def load_cases(path: str) -> list[dict]:
    """A case file has one JSON object per line: {"id": ..., "question": ..., "expect": ...}."""
    with open(path, encoding="utf8") as f:
        return [json.loads(line) for line in f if line.strip()]


def contains_expected(answer, case) -> bool:
    """The simplest check: the expected text appears in the answer."""
    return str(case["expect"]).lower() in str(answer).lower()


def run_suite(agent, cases, trials: int = 3, check=contains_expected) -> dict:
    """Ask every case `trials` times. agent(question) -> answer; check(answer, case) -> bool."""
    results = [{"id": case["id"], "passed": bool(check(agent(case["question"]), case))}
               for case in cases for _ in range(trials)]
    passes = sum(r["passed"] for r in results)
    low, high = wilson(passes, len(results))
    passed = {r["id"] for r in results if r["passed"]}
    failed = {r["id"] for r in results if not r["passed"]}
    return {"passes": passes, "runs": len(results), "rate": passes / len(results),
            "low": low, "high": high, "flaky": sorted(passed & failed), "results": results}


def compare(old: dict, new: dict) -> str:
    """A cautious verdict: better or worse only when the two intervals don't overlap."""
    if new["low"] > old["high"]:
        return "better"
    if new["high"] < old["low"]:
        return "worse"
    return "can't tell yet: the intervals overlap, so run more trials or more cases"


def simulated_agent(success_rate: float, seed: int = 0):
    """A stand-in for an agent that answers each question correctly with a fixed probability."""
    rng = random.Random(seed)
    return lambda question: "correct" if rng.random() < success_rate else "wrong"


CASES = [{"id": f"q{i}", "question": f"question {i}", "expect": "correct"} for i in range(10)]


def report(label: str, r: dict) -> None:
    print(f"{label:<14} {r['passes']:>3}/{r['runs']:<4} = {r['rate']:4.0%}   "
          f"95% interval {r['low']:4.0%} to {r['high']:4.0%}")


if __name__ == "__main__":
    print("Version A really succeeds 70% of the time, version B 80%.\n")
    for trials in (1, 3, 30):
        a = run_suite(simulated_agent(0.70, seed=1), CASES, trials)
        b = run_suite(simulated_agent(0.80, seed=2), CASES, trials)
        print(f"{trials} trial(s) per case, {len(CASES)} cases")
        report("  version A", a)
        report("  version B", b)
        print("  B against A:", compare(a, b), "\n")
