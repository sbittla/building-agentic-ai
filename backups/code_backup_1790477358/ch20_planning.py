"""Chapter 20: planning. The model writes a plan as data; code checks the plan before
anything runs; each step runs with the Chapter 4 loop, its own brief and only the tools
it's allowed; when a step fails, the rest of the plan is made again.

    ./course.sh python ch20_planning.py
    ./course.sh python ch20_planning.py "Which city brings in the most revenue?"
"""
import json
import sys
from graphlib import CycleError, TopologicalSorter

import ch08_sql_tools as sql
from ch04_agent import MODEL, get_client, run_agent

MAX_STEPS = 6              # a plan longer than this is sent back
MAX_REPLANS = 2

# ------------------------------------------------------------ 1. a plan is data
PLAN = {"type": "object", "additionalProperties": False, "required": ["steps"],
        "properties": {"steps": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["id", "do", "tools", "needs", "done_when"],
            "properties": {
                "id": {"type": "string"},                    # "s1", "s2", ...
                "do": {"type": "string"},                    # one concrete action
                "tools": {"type": "array", "items": {"type": "string"}},
                "needs": {"type": "array", "items": {"type": "string"}},  # step ids
                "done_when": {"type": "string"}}}}}}         # how to tell it worked

PLANNER = ("You plan work for an agent. Break the goal into at most {n} small steps. "
           "Each step does one thing, lists only the tools it needs (from: {tools}), "
           "lists the ids of earlier steps whose results it needs, and says how to "
           "tell it's done. The last step must produce the final answer to the goal. "
           "Plan only; don't answer the goal yet.")

def ask_json(system, prompt, schema, model=None, max_tokens=3000) -> dict:
    """One model call that must return JSON matching `schema` (structured outputs)."""
    reply = get_client().messages.create(
        model=model or MODEL, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": schema}})
    return json.loads("".join(b.text for b in reply.content if b.type == "text"))

def make_plan(goal: str, tools: list[dict], feedback: str = "", model=None) -> dict:
    names = ", ".join(t["name"] for t in tools)
    prompt = f"Goal: {goal}" + (f"\n\n{feedback}" if feedback else "")
    return ask_json(PLANNER.format(n=MAX_STEPS, tools=names), prompt, PLAN, model)

# ------------------------------------------------------------ 2. check before running
def check_plan(plan: dict, tools: list[dict], done: dict | None = None) -> list[str]:
    """Everything the model could get wrong that code can catch. Empty list = OK."""
    steps, known = plan["steps"], {t["name"] for t in tools}
    ids = [s["id"] for s in steps]
    earlier = set(done or {})                      # results from before a replan
    errors = []
    if not steps:
        errors.append("the plan has no steps")
    if len(steps) > MAX_STEPS:
        errors.append(f"{len(steps)} steps; the limit is {MAX_STEPS}")
    if len(set(ids)) != len(ids) or earlier & set(ids):
        errors.append("step ids must be unique")
    for s in steps:
        if unknown := set(s["tools"]) - known:
            errors.append(f"{s['id']} uses unknown tools {sorted(unknown)}")
        if missing := set(s["needs"]) - set(ids) - earlier:
            errors.append(f"{s['id']} needs steps that don't exist: {sorted(missing)}")
        if not s["done_when"].strip():
            errors.append(f"{s['id']} has no done_when")
    try:
        order(plan, done)
    except CycleError:
        errors.append("the steps depend on each other in a circle")
    return errors

def order(plan: dict, done: dict | None = None) -> list[str]:
    """Step ids in an order that respects `needs` (a topological sort)."""
    graph = {s["id"]: {n for n in s["needs"] if n not in (done or {})}
             for s in plan["steps"]}
    return list(TopologicalSorter(graph).static_order())

# ------------------------------------------------------------ 3. execute and replan
def run_step(step, results, tools, run_tool, model=None, verbose=False):
    """One step with its own brief: the step, how to tell it's done, and ONLY the
    results it depends on. Never the whole history (Chapter 16)."""
    allowed = [t for t in tools if t["name"] in step["tools"]]
    inputs = "\n".join(f"- {n}: {results[n][:1500]}" for n in step["needs"])
    brief = (f"Do this: {step['do']}\nYou're done when: {step['done_when']}\n"
             + (f"Results you can use:\n{inputs}\n" if inputs else "")
             + "Reply with the result only.")
    return run_agent(brief, allowed, run_tool, system=sql.SYSTEM, verbose=verbose,
                     max_iterations=6, model=model)

def execute(goal, tools, run_tool, route=None, verbose=False) -> dict:
    """Plan, check, run step by step, and replan the rest when a step fails.
    route(step) -> model name lets each step use a different model (section 20.7)."""
    results, log, feedback = {}, [], ""
    for attempt in range(MAX_REPLANS + 1):
        plan = make_plan(goal, tools, feedback)
        if errors := check_plan(plan, tools, results):
            log.append(("rejected plan", errors))
            feedback = ("Your previous plan was rejected: " + "; ".join(errors)
                        + _done_so_far(results))
            continue
        log.append(("plan", [s["id"] + ": " + s["do"] for s in plan["steps"]]))
        steps = {s["id"]: s for s in plan["steps"]}
        failed = None
        for sid in order(plan, results):
            step = steps[sid]
            model = route(step) if route else None
            answer, _, stats = run_step(step, results, tools, run_tool, model, verbose)
            log.append((sid, stats.get("model", MODEL), stats["stop_reason"]))
            if stats["stop_reason"] not in ("end_turn", "stop_sequence") \
                    or answer.startswith("ERROR"):
                failed = (sid, answer[:300])
                break
            results[sid] = answer
        if not failed:
            return {"answer": results[order(plan, {})[-1]], "results": results,
                    "log": log, "replans": attempt}
        feedback = (f"Step {failed[0]} failed: {failed[1]}. Plan ONLY the remaining "
                    f"work, with new step ids." + _done_so_far(results))
    return {"answer": "Couldn't complete the goal; see the log.", "results": results,
            "log": log, "replans": MAX_REPLANS}

def _done_so_far(results: dict) -> str:
    if not results:
        return ""
    done = "\n".join(f"- {k}: {v[:300]}" for k, v in results.items())
    return f"\n\nAlready done (use these ids in `needs`, don't redo them):\n{done}"

if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or ("Which city brings in the most revenue, and "
                                      "which product category sells best there?")
    out = execute(goal, sql.TOOLS, sql.run_tool, verbose=True)
    for entry in out["log"]:
        print(*entry)
    print("\nAnswer:", out["answer"])
