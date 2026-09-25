"""Capstone 3: logs, metrics and runbooks for incident triage (read-only)."""
import csv, json, logging, re, statistics, sys
from pathlib import Path
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
ROOT = Path("incident")
mcp = MCPServer("observability")

@mcp.tool()
def search_logs(service: str, start: str, end: str, pattern: str = "ERROR", limit: int = 20) -> str:
    """Log lines for a service between start and end (YYYY-MM-DDTHH:MM) matching a regex.
    Returns a count and up to `limit` example lines."""
    f = ROOT / "logs" / f"{service}.jsonl"
    if not f.exists():
        raise ToolError(f"No logs for {service}. Known: {[p.stem for p in (ROOT / 'logs').glob('*.jsonl')]}")
    rx = re.compile(pattern, re.I)
    hits = [json.loads(l) for l in f.read_text().splitlines()]
    hits = [h for h in hits if start <= h["ts"][:16] <= end and rx.search(h["msg"])]
    return f"{len(hits)} matching lines\n" + "\n".join(f"{h['ts']} {h['msg']}" for h in hits[:limit])

def _series(service, metric):
    with open(ROOT / "metrics.csv") as f:
        return [(r["minute"], float(r[metric])) for r in csv.DictReader(f) if r["service"] == service]

@mcp.tool()
def compare_to_baseline(service: str, metric: str, baseline_start: str, baseline_end: str,
                        window_start: str, window_end: str) -> str:
    """Mean of a metric (p95_ms or error_rate) in a window vs a baseline window, with the
    first minute where it crossed 2x the baseline. All statistics are computed here."""
    if metric not in ("p95_ms", "error_rate"):
        raise ToolError("metric must be p95_ms or error_rate")
    s = _series(service, metric)
    base = [v for t, v in s if baseline_start <= t <= baseline_end]
    win = [(t, v) for t, v in s if window_start <= t <= window_end]
    if not base or not win:
        raise ToolError("No data in one of the windows.")
    b = statistics.mean(base)
    first = next((t for t, v in win if v > 2 * b), None)
    w = statistics.mean(v for _, v in win)
    return json.dumps({"service": service, "metric": metric, "baseline_mean": round(b, 4),
                       "window_mean": round(w, 4), "ratio": round(w / b, 2),
                       "first_minute_over_2x": first})

@mcp.tool()
def search_runbooks(query: str) -> str:
    """Find runbooks whose text matches words in the query."""
    words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 3]
    hits = [p.name for p in (ROOT / "runbooks").glob("*.md")
            if any(w in p.read_text().lower() for w in words)]
    return "\n".join(hits) or "No runbooks match."

@mcp.tool()
def read_runbook(name: str) -> str:
    """Read one runbook by file name."""
    p = ROOT / "runbooks" / Path(name).name
    if not p.exists():
        raise ToolError("No such runbook.")
    return p.read_text()

if __name__ == "__main__":
    mcp.run(transport="stdio")
