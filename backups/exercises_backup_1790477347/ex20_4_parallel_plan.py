"""Exercise 20.4 (solution): run every step whose dependencies are finished at the same
time. TopologicalSorter hands out "ready" steps; threads run them; done() unlocks more."""
import concurrent.futures as cf
import time
from graphlib import TopologicalSorter

from ch20_planning import run_step

def run_plan_parallel(plan, tools, run_tool, workers: int = 4) -> tuple[dict, list]:
    steps = {s["id"]: s for s in plan["steps"]}
    sorter = TopologicalSorter({s["id"]: set(s["needs"]) for s in plan["steps"]})
    sorter.prepare()
    results, rounds = {}, []
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        while sorter.is_active():
            ready = list(sorter.get_ready())
            rounds.append(ready)                            # what ran together
            futures = {pool.submit(run_step, steps[s], dict(results), tools, run_tool): s
                       for s in ready}
            for fut in cf.as_completed(futures):
                sid = futures[fut]
                results[sid] = fut.result()[0]
                sorter.done(sid)
    return results, rounds

def run_plan_sequential(plan, tools, run_tool) -> dict:
    results = {}
    for sid in TopologicalSorter({s["id"]: set(s["needs"])
                                  for s in plan["steps"]}).static_order():
        step = next(s for s in plan["steps"] if s["id"] == sid)
        results[sid] = run_step(step, results, tools, run_tool)[0]
    return results

def timed(fn, *args):
    t0 = time.perf_counter()
    out = fn(*args)
    return out, time.perf_counter() - t0

PLAN = {"steps": [
    {"id": "s1", "do": "Count the customers.", "tools": ["run_query"], "needs": [],
     "done_when": "one number"},
    {"id": "s2", "do": "Count the orders.", "tools": ["run_query"], "needs": [],
     "done_when": "one number"},
    {"id": "s3", "do": "Say how many orders there are per customer.", "tools": [],
     "needs": ["s1", "s2"], "done_when": "a ratio"}]}

if __name__ == "__main__":
    import ch08_sql_tools as sql
    (_, rounds), t_par = timed(run_plan_parallel, PLAN, sql.TOOLS, sql.run_tool)
    _, t_seq = timed(run_plan_sequential, PLAN, sql.TOOLS, sql.run_tool)
    print(f"rounds: {rounds}\nparallel {t_par:.1f}s, sequential {t_seq:.1f}s")
