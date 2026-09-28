"""Exercise 19.5 (solution): a cost budget per job. The agent action records what each
model call cost; a job that would go over its budget waits for a person."""
import json

import ch19_durable as d
from ch04_agent import run_agent

PRICES = {"input": 2.00, "output": 10.00}        # dollars per million tokens (Appendix E)
BUDGETS: dict[str, float] = {}                   # job id -> dollars
SPENT: dict[str, float] = {}

def cost(stats: dict) -> float:
    return (stats["input_tokens"] * PRICES["input"]
            + stats["output_tokens"] * PRICES["output"]) / 1e6

def budgeted_agent(args, key):
    job = key.split(":")[0]
    if SPENT.get(job, 0.0) >= BUDGETS.get(job, float("inf")):
        raise d.Permanent(f"job budget of ${BUDGETS[job]:.4f} used up "
                          f"(spent ${SPENT[job]:.4f})")
    answer, _, stats = run_agent(args["prompt"], [], lambda n, a: "ERROR: no tools",
                                 verbose=False, max_iterations=args.get("max_steps", 4))
    SPENT[job] = SPENT.get(job, 0.0) + cost(stats)
    if stats["stop_reason"] not in ("end_turn", "stop_sequence"):
        raise RuntimeError(f"agent step didn't finish: {answer[:200]}")
    return answer

d.ACTIONS["agent"]["run"] = budgeted_agent

def create_job(goal, steps, budget: float):
    job = d.create_job(goal, steps)
    BUDGETS[job] = budget
    return job

def main():
    steps = [{"action": "agent", "args": {"prompt": f"Write tagline {i} for a bakery."}}
             for i in range(3)]
    small = create_job("tiny budget", steps, budget=0.000001)
    normal = create_job("normal budget", steps, budget=1.00)
    results = {job: d.run_job(job) for job in (small, normal)}
    for job in (small, normal):
        print(d.report(job), f"\n  spent ${SPENT.get(job, 0):.5f}")
    return results, small, normal

if __name__ == "__main__":
    print(json.dumps(main()[0]))
