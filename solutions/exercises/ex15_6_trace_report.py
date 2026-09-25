"""Exercise 15.6 (Medium): a report over the last 50 runs in traces.jsonl."""
import collections
import json
import statistics
import sys

def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))]

def report(path="traces.jsonl", last=50):
    runs = [json.loads(l) for l in open(path) if l.strip()][-last:]
    secs = [r["seconds"] for r in runs]
    tools = collections.Counter()
    for r in runs:
        tools.update(r.get("tools_used", []))
    print(f"runs: {len(runs)}   pass rate: {sum(r['pass'] for r in runs) / len(runs):.0%}")
    print(f"latency p50 {pct(secs, 50):.1f}s  p95 {pct(secs, 95):.1f}s   "
          f"mean tokens {statistics.mean(r['tokens'] for r in runs):,.0f}   "
          f"mean tool calls {statistics.mean(r['tool_calls'] for r in runs):.1f}")
    if tools:
        print("most-used tools:", ", ".join(f"{t} ({n})" for t, n in tools.most_common(5)))
    print("slowest questions:")
    for r in sorted(runs, key=lambda r: -r["seconds"])[:5]:
        print(f"  {r['seconds']:5.1f}s  {r['tokens']:>6} tok  {r['question'][:60]}")
    fails = collections.Counter(f for r in runs for f in r["failures"])
    if fails:
        print("most common failures:", fails.most_common(3))
    return runs

if __name__ == "__main__":
    report(*(sys.argv[1:2] or []))
