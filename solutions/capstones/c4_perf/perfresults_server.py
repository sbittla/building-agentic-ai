"""Capstone 4: load-test results. ALL statistics are computed here in Python,
so the model never does the arithmetic."""
import csv, json, logging, math, sys
from pathlib import Path
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
ROOT = Path("perf")
mcp = MCPServer("perfresults")

def _pct(sorted_vals, p):
    k = (len(sorted_vals) - 1) * p / 100
    lo, hi = math.floor(k), math.ceil(k)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)

def latencies(run_id: str) -> dict:
    """endpoint -> list of latencies (ms) for one run."""
    out = {}
    with open(ROOT / "runs" / f"{run_id}.csv") as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r["endpoint"], []).append(float(r["latency_ms"]))
    return out

def p95_change_ci(before: list, after: list, n_boot: int = 400, seed: int = 0):
    """Bootstrap 95% interval for the % change in p95. One run's p95 is noisy: resample
    each run's requests many times and see how much the change could move by chance."""
    import random
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_boot):
        a = sorted(rng.choices(before, k=len(before)))
        b = sorted(rng.choices(after, k=len(after)))
        pa, pb = _pct(a, 95), _pct(b, 95)
        diffs.append(100 * (pb - pa) / pa)
    diffs.sort()
    return round(_pct(diffs, 2.5), 1), round(_pct(diffs, 97.5), 1)

def stats(run_id: str) -> dict:
    f = ROOT / "runs" / f"{run_id}.csv"
    if not f.exists():
        raise ToolError(f"No run {run_id}. Use list_runs.")
    by_ep, first, last = {}, None, None
    with open(f) as fh:
        for r in csv.DictReader(fh):
            t = int(r["timestamp_ms"]); first = t if first is None else first; last = t
            by_ep.setdefault(r["endpoint"], []).append((float(r["latency_ms"]), r["status"] != "200"))
    seconds = (last - first) / 1000
    out = {}
    for ep, rows in sorted(by_ep.items()):
        lat = sorted(l for l, _ in rows)
        out[ep] = {"requests": len(rows), "p50_ms": round(_pct(lat, 50), 1),
                   "p95_ms": round(_pct(lat, 95), 1), "p99_ms": round(_pct(lat, 99), 1),
                   "throughput_rps": round(len(rows) / seconds, 2),
                   "error_rate_pct": round(100 * sum(e for _, e in rows) / len(rows), 2)}
    return out

@mcp.tool()
def list_runs() -> str:
    """Available runs with their build ids."""
    return "\n".join(p.read_text() for p in sorted((ROOT / "runs").glob("*.json")))

@mcp.tool()
def load_run(run_id: str) -> str:
    """Per-endpoint p50/p95/p99 latency, throughput and error rate for one run."""
    return json.dumps(stats(run_id), indent=1)

@mcp.tool()
def compare_runs(baseline: str, candidate: str) -> str:
    """Compare two runs against the thresholds; lists regressions with the numbers.
    A p95 regression counts only if it passes the threshold AND its 95% interval is
    entirely above zero, so run-to-run noise isn't reported as a regression."""
    th = json.loads((ROOT / "thresholds.json").read_text())
    a, b = stats(baseline), stats(candidate)
    la, lb = latencies(baseline), latencies(candidate)
    findings = []
    for ep in sorted(set(a) & set(b)):
        dp95 = 100 * (b[ep]["p95_ms"] - a[ep]["p95_ms"]) / a[ep]["p95_ms"]
        dtp = 100 * (b[ep]["throughput_rps"] - a[ep]["throughput_rps"]) / a[ep]["throughput_rps"]
        row = {"endpoint": ep, "p95_before": a[ep]["p95_ms"], "p95_after": b[ep]["p95_ms"],
               "p95_change_pct": round(dp95, 1), "error_rate_after_pct": b[ep]["error_rate_pct"],
               "throughput_change_pct": round(dtp, 1), "regressions": []}
        lo, hi = p95_change_ci(la[ep], lb[ep])
        row["p95_change_ci95_pct"] = [lo, hi]
        if dp95 > th["p95_regression_pct"] and lo > 0:
            row["regressions"].append("p95")
        elif dp95 > th["p95_regression_pct"]:
            row["note"] = "p95 rose past the threshold, but within run-to-run noise: rerun to confirm"
        if b[ep]["error_rate_pct"] > th["error_rate_max_pct"]:
            row["regressions"].append("errors")
        if -dtp > th["throughput_drop_pct"]:
            row["regressions"].append("throughput")
        findings.append(row)
    return json.dumps({"baseline": baseline, "candidate": candidate, "thresholds": th,
                       "endpoints": findings}, indent=1)

@mcp.tool()
def release_notes() -> str:
    """What changed in each build."""
    return (ROOT / "release_notes.md").read_text()

@mcp.resource("perf://thresholds")
def thresholds() -> str:
    """Regression thresholds."""
    return (ROOT / "thresholds.json").read_text()

@mcp.tool()
def start_test(scenario: str, users: int, duration_s: int) -> str:
    """Start a new load test (a stub in this capstone). Requires human approval."""
    return f"Queued {scenario} with {users} users for {duration_s}s (stub: no real traffic)."

if __name__ == "__main__":
    mcp.run(transport="stdio")
