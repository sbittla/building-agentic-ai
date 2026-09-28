"""Exercise 20.3 (solution): plans that check_plan must reject, and one it accepts.
No model is called: checking a plan is ordinary code."""
import ch08_sql_tools as sql
from ch20_planning import check_plan

def step(sid, tools=("run_query",), needs=(), done="a number is returned"):
    return {"id": sid, "do": f"step {sid}", "tools": list(tools), "needs": list(needs),
            "done_when": done}

BAD = {
    "too many steps": ({"steps": [step(f"s{i}") for i in range(1, 9)]}, "limit"),
    "unknown tool": ({"steps": [step("s1", tools=["send_email"])]}, "unknown tools"),
    "missing step": ({"steps": [step("s1", needs=["s0"])]}, "don't exist"),
    "cycle": ({"steps": [step("s1", needs=["s2"]), step("s2", needs=["s1"])]}, "circle"),
    "no done_when": ({"steps": [step("s1", done=" ")]}, "no done_when"),
}
GOOD = {"steps": [step("s1", tools=["get_schema"], done="the tables are listed"),
                  step("s2", needs=["s1"]), step("s3", tools=[], needs=["s1", "s2"])]}

def main():
    results = {}
    for name, (plan, expected) in BAD.items():
        errors = check_plan(plan, sql.TOOLS)
        results[name] = (bool(errors) and any(expected in e for e in errors), errors)
    results["good"] = (check_plan(GOOD, sql.TOOLS) == [], [])
    for name, (ok, errors) in results.items():
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {errors}")
    return results

if __name__ == "__main__":
    main()
