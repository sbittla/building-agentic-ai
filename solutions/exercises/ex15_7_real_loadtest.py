"""Exercise 15.7 (Complex): load-test the chapter 13 MCP agent with real questions.

Start small:  ./course.sh python exercises/ex15_7_real_loadtest.py 5
Set a spending limit in your provider console before trying 50 users.
"""
import asyncio
import json
import statistics
import sys
import time
import ch13_mcp_agent as m13
import ch15_loadtest as lt

QUESTIONS = [json.loads(l)["question"] for l in open("eval_sql.jsonl") if l.strip()]

async def run(users=5, per_user=2, max_in_flight=10, cache_schema=False):
    config = {"servers": {"shopdb": {"command": "python", "args": ["ch13_sql_server.py"]}}}
    async with m13.MCPHub(config) as hub:
        schema = (await hub.call("shopdb__get_schema", {}))[0] if cache_schema else None
        system = "You are a data analyst for the shop database." + (
            f"\nSchema (already fetched, don't call get_schema):\n{schema}" if schema else "")
        latencies, errors, steps = [], [], []
        sem = asyncio.Semaphore(max_in_flight)
        async def one(q):
            t0 = time.perf_counter()                  # from arrival: includes queueing
            async with sem:
                try:
                    answer, msgs = await asyncio.wait_for(
                        m13.run_mcp_agent(hub, q, system=system), timeout=120)
                    steps.append(sum(1 for m in msgs if m["role"] == "assistant"))
                    latencies.append(time.perf_counter() - t0)
                except Exception as exc:
                    errors.append(type(exc).__name__)
        t0 = time.perf_counter()
        await asyncio.gather(*(one(QUESTIONS[(u + i) % len(QUESTIONS)])
                               for u in range(users) for i in range(per_user)))
        wall = time.perf_counter() - t0
    result = {"users": users, "requests": len(latencies) + len(errors), "errors": len(errors),
              "p50": lt.pct(latencies, 50), "p95": lt.pct(latencies, 95),
              "mean_steps": statistics.mean(steps) if steps else 0, "wall": wall,
              "cache_schema": cache_schema}
    print(json.dumps(result, indent=1))
    return result

def main(users=5):
    before = asyncio.run(run(users))
    after = asyncio.run(run(users, cache_schema=True))    # the fix: one fewer step per question
    print(f"\nmean steps {before['mean_steps']:.1f} -> {after['mean_steps']:.1f}, "
          f"p95 {before['p95']:.1f}s -> {after['p95']:.1f}s")
    return before, after

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
