"""Exercise 20.6 (solution): a checked plan becomes a Chapter 19 durable job. Each plan
step is a "plan_step" action whose brief gets earlier results through "$n" references,
and each step's model is chosen by the rules router."""
import ch08_sql_tools as sql
import ch19_durable as d
from ch04_agent import run_agent
from ch20_planning import check_plan, make_plan, order
from ch20_router import by_rules

@d.action("plan_step")
def plan_step(args, key):
    inputs = "\n".join(f"- {k}: {v[:1500]}" for k, v in args["inputs"].items())
    brief = (f"Do this: {args['do']}\nYou're done when: {args['done_when']}\n"
             + (f"Results you can use:\n{inputs}\n" if inputs else "")
             + "Reply with the result only.")
    tools = [t for t in sql.TOOLS if t["name"] in args["tools"]]
    answer, _, stats = run_agent(brief, tools, sql.run_tool, system=sql.SYSTEM,
                                 verbose=False, model=args["model"], max_iterations=6)
    if stats["stop_reason"] not in ("end_turn", "stop_sequence"):
        raise RuntimeError(f"step didn't finish: {answer[:200]}")
    return answer

def plan_to_job(goal: str, plan: dict) -> str:
    ids = order(plan)
    position = {sid: i for i, sid in enumerate(ids, 1)}       # plan id -> job step
    steps = []
    for sid in ids:
        s = next(x for x in plan["steps"] if x["id"] == sid)
        steps.append({"action": "plan_step", "args": {
            "do": s["do"], "done_when": s["done_when"], "tools": s["tools"],
            "inputs": {n: f"${position[n]}" for n in s["needs"]},
            "model": by_rules(s["do"], s["tools"])}})
    return d.create_job(goal, steps)

def main(goal="Which city brings in the most revenue?", crash_after=1):
    plan = make_plan(goal, sql.TOOLS)
    if errors := check_plan(plan, sql.TOOLS):
        raise SystemExit(f"plan rejected: {errors}")
    job = d.claim("w1", plan_to_job(goal, plan))
    try:
        d.run_job(job, crash_after=crash_after)
    except d.Crash:
        with d._db() as con:
            con.execute("UPDATE jobs SET lease_until=0 WHERE id=?", (job,))
        d.claim("w2", job)
    status = d.run_job(job, worker="w2")
    print(d.report(job))
    return job, status

if __name__ == "__main__":
    main()
