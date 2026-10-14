"""Exercises 11.4 and 11.5, run end to end with sol_ch11_research_team.

    python run11_team.py delegation   11.4: the plan as structured objects, and how many
                                      model calls each subtask used (quick vs deep)
    python run11_team.py critic       11.5: plant an unsupported claim, show the critic
                                      catching it and the revised answer without it
"""
import asyncio
import json
import sys

import ch11_research_team as base
import sol_ch11_research_team as sol

QUESTION = ("Compare agentic search and RAG for our internal docs: cost, freshness, "
            "exact error codes.")
PLANTED = "RAG is always free to run, because embedding models cost nothing to call."

steps = []                                  # (objective, effort, model calls used)

def count_steps():
    original = base.run_subagent
    async def counted(task, max_iterations=6):
        before = base.usage["calls"]
        out = await original(task, max_iterations=max_iterations)
        effort = "quick" if max_iterations == sol.EFFORT_STEPS["quick"] else "deep"
        steps.append((task.splitlines()[0].removeprefix("Objective: "), effort,
                      base.usage["calls"] - before))
        return out
    base.run_subagent = counted

def delegation():
    count_steps()
    r = asyncio.run(sol.research(QUESTION, parallel=False, critic=False))
    print("PLAN (structured):")
    print(json.dumps(r["subtasks"], indent=1))
    print("\nmodel calls per subtask:")
    for objective, effort, calls in steps:
        print(f"  {effort:<5} {calls} calls  {objective[:70]}")
    quick = [c for _, e, c in steps if e == "quick"]
    deep = [c for _, e, c in steps if e == "deep"]
    if quick and deep:
        print(f"quick subtasks: at most {max(quick)} calls; deep: up to {max(deep)} "
              f"(caps {sol.EFFORT_STEPS['quick']} and {sol.EFFORT_STEPS['deep']})")
    print(f"\n{r['answer']}")

def critic():
    r = asyncio.run(sol.research(QUESTION, plant=PLANTED))
    print(f"planted claim: {PLANTED}")
    print(f"critic flagged: {json.dumps(r['unsupported'], indent=1)}")
    caught = any("free" in c.lower() or "cost nothing" in c.lower() for c in r["unsupported"])
    gone = "cost nothing" not in r["answer"].lower()
    print(f"critic caught the planted claim: {caught}")
    print(f"revised answer still has it: {not gone}")
    print(f"\nREVISED ANSWER:\n{r['answer']}")

if __name__ == "__main__":
    {"delegation": delegation, "critic": critic}[sys.argv[1] if len(sys.argv) > 1 else "critic"]()
