"""Exercise 7.7 (Complex): 3-city trip, 5 runs with cache on and 5 with cache off."""
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
        t0 = time.perf_counter()
        run_agent(QUESTION, w.TOOLS, w.run_tool, system=w.SYSTEM, verbose=False)
        rows.append({"seconds": time.perf_counter() - t0,
                     "http_calls": base.stats["http_calls"] - before["http_calls"],
                     "cache_hits": base.stats["cache_hits"] - before["cache_hits"]})
    return rows

def main(runs=5):
    base._cache.clear()
    table = {"cache on": run(True, runs), "cache off": run(False, runs)}
    print("| mode | mean s | HTTP calls/run | cache hits/run |")
    for mode, rows in table.items():
        print(f"| {mode} | {statistics.mean(r['seconds'] for r in rows):.2f} | "
              f"{statistics.mean(r['http_calls'] for r in rows):.1f} | "
              f"{statistics.mean(r['cache_hits'] for r in rows):.1f} |")
    print("Time goes to model calls plus one HTTP round-trip per geocode/forecast; with the "
          "cache on, repeat runs skip the HTTP part entirely.")
    return table

if __name__ == "__main__":
    main()
