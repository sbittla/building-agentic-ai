"""Chapter 20: model routing. Send each task to the cheapest model that can do it well:
by rules, by asking a small model, or by trying the small model first and escalating
when a check fails (a cascade). Measure cost per SUCCESSFUL task, not per call.

    ./course.sh python ch20_router.py        compare always-large, always-small, cascade
"""
import os
import re

import ch08_sql_tools as sql
from ch04_agent import MODEL, run_agent
from ch20_planning import ask_json

SMALL = os.environ.get("SMALL_MODEL", "claude-haiku-4-5")
LARGE = MODEL
PRICES = {"claude-haiku-4-5": (1.00, 5.00),    # dollars per million input and output
          "claude-sonnet-5": (2.00, 10.00)}    # tokens (Appendix E); prices change

def cost(stats: dict) -> float:
    model = stats.get("model", LARGE)
    price_in, price_out = PRICES.get(model, (0.0, 0.0))        # the local model: free
    return (stats["input_tokens"] * price_in + stats["output_tokens"] * price_out) / 1e6

# ------------------------------------------------------------ 1. rules
HARD_WORDS = ("why", "compare", "explain", "trend", "plan", "design", "trade-off")

def by_rules(task: str, tools: list | None = None) -> str:
    """Cheap and predictable: long tasks, many tools or 'reasoning' words go large."""
    hard = (len(task) > 400 or len(tools or []) > 3
            or any(w in task.lower() for w in HARD_WORDS))
    return LARGE if hard else SMALL

# ------------------------------------------------------------ 2. ask a small model
LEVEL = {"type": "object", "additionalProperties": False, "required": ["level", "why"],
         "properties": {"level": {"type": "string", "enum": ["easy", "hard"]},
                        "why": {"type": "string"}}}

def by_model(task: str) -> str:
    """A small model rates the task. Costs one small call, catches what rules miss."""
    verdict = ask_json("Rate how hard this task is for an AI assistant with SQL "
                       "tools. 'easy': one lookup or count. 'hard': several queries, "
                       "judgement or explanation.", task, LEVEL, model=SMALL,
                       max_tokens=2000)
    return LARGE if verdict["level"] == "hard" else SMALL

# ------------------------------------------------------------ 3. a cascade
def cascade(task, tools, run_tool, check, system=sql.SYSTEM, verbose=False):
    """Try the small model; accept its answer only if `check(answer)` passes in code;
    otherwise escalate to the large model. Returns (answer, trail of attempts)."""
    trail = []
    for model in (SMALL, LARGE):
        answer, _, stats = run_agent(task, tools, run_tool, system=system,
                                     verbose=verbose, model=model)
        ok = stats["stop_reason"] in ("end_turn", "stop_sequence") and check(answer)
        trail.append({"model": model, "ok": ok, "cost": cost(stats),
                      "tokens": stats["input_tokens"] + stats["output_tokens"]})
        if ok:
            break
    return answer, trail

# ------------------------------------------------------------ 4. measure it
def report(runs: list[dict]) -> dict:
    """runs: [{"cost": dollars, "ok": bool}]. Cost per successful task is the number
    to compare: a cheap model that fails half the time isn't cheap."""
    wins = sum(r["ok"] for r in runs)
    total = sum(r["cost"] for r in runs)
    return {"tasks": len(runs), "successes": wins, "total_cost": round(total, 5),
            "cost_per_success": round(total / wins, 5) if wins else None}

def has_number(answer: str) -> bool:
    """A deliberately cheap check. Chapter 27 shows real ones (gold answers)."""
    return bool(re.search(r"\d", answer))

TASKS = ["How many customers are there?",
         "How many orders were cancelled?",
         "Which product has the highest price?",
         "Compare revenue in the first and second half of the year and explain the "
         "difference by product category."]

if __name__ == "__main__":
    for name, route in [("always large", lambda t: LARGE), ("always small",
                        lambda t: SMALL), ("rules", by_rules)]:
        runs = []
        for task in TASKS:
            answer, _, stats = run_agent(task, sql.TOOLS, sql.run_tool,
                                         system=sql.SYSTEM, verbose=False,
                                         model=route(task))
            runs.append({"cost": cost(stats), "ok": has_number(answer)})
        print(f"{name:<13}", report(runs))
    runs = []
    for task in TASKS:
        _, trail = cascade(task, sql.TOOLS, sql.run_tool, has_number)
        runs.append({"cost": sum(t["cost"] for t in trail), "ok": trail[-1]["ok"]})
        steps = [t["model"] + (" ok" if t["ok"] else " failed check") for t in trail]
        print("  cascade:", " -> ".join(steps))
    print(f"{'cascade':<13}", report(runs))
