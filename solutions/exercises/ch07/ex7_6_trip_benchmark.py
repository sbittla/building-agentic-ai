"""Exercise 7.6 (Complex): 3-city trip, 5 runs with cache on and 5 with cache off."""
import statistics
import time
import sol_ch07_weather_tools as w
import ch07_weather_tools as base
from ch04_agent import run_agent

QUESTION = ("I'm travelling Seattle (2 days), then Austin (3 days), then Pune (2 days). "
            "What should I pack? Check each city's forecast.")

def run(cache_on: bool, runs: int = 5):
    rows = []
    for _ in range(runs):
        if not cache_on:
            base._cache.clear()
        base.CACHE_SECONDS = 600 if cache_on else 0
        before = dict(base.stats)
        tool_time = [0.0]
        def timed_tool(name, args):
            t = time.perf_counter()
            try:
                return w.run_tool(name, args)
            finally:
                tool_time[0] += time.perf_counter() - t
        t0 = time.perf_counter()
        run_agent(QUESTION, w.TOOLS, timed_tool, system=w.SYSTEM, verbose=False)
        rows.append({"seconds": time.perf_counter() - t0, "tool_seconds": tool_time[0],
                     "http_calls": base.stats["http_calls"] - before["http_calls"],
                     "cache_hits": base.stats["cache_hits"] - before["cache_hits"]})
    return rows

def main(runs=5):
    base._cache.clear()
    table = {"cache on": run(True, runs), "cache off": run(False, runs)}
    print("| mode | mean s | model s | tool (HTTP) s | HTTP calls/run | cache hits/run |")
    means = {}
    for mode, rows in table.items():
        total = statistics.mean(r["seconds"] for r in rows)
        tools = statistics.mean(r["tool_seconds"] for r in rows)
        means[mode] = tools
        print(f"| {mode} | {total:.2f} | {total - tools:.2f} | {tools:.2f} | "
              f"{statistics.mean(r['http_calls'] for r in rows):.1f} | "
              f"{statistics.mean(r['cache_hits'] for r in rows):.1f} |")
    print(f"Most of the time is model calls; the tools' HTTP round-trips are the rest. The cache "
          f"cuts tool time from {means['cache off']:.2f}s to {means['cache on']:.2f}s per run "
          "(repeat runs skip the HTTP part); differences in total time beyond that are the "
          "model's run-to-run variation.")
    return table

if __name__ == "__main__":
    main()
