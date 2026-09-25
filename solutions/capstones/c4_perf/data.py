"""Capstone 4 data: three load-test runs (per-request CSV, like a Gatling/JMeter/k6
export). Run 3 has a planted regression on /api/search, plus thresholds."""
import json
import random
from pathlib import Path

ROOT = Path("perf")
ENDPOINTS = {"/api/login": 120, "/api/search": 240, "/api/checkout": 380, "/api/profile": 90}

def build():
    rnd = random.Random(5)
    (ROOT / "runs").mkdir(parents=True, exist_ok=True)
    for run, build_id in (("run-101", "b101"), ("run-102", "b102"), ("run-103", "b103")):
        rows = ["timestamp_ms,endpoint,latency_ms,status"]
        t = 0
        for i in range(6000):
            ep = rnd.choice(list(ENDPOINTS))
            base = ENDPOINTS[ep]
            slow = run == "run-103" and ep == "/api/search"
            lat = rnd.lognormvariate(0, 0.35) * base * (1.9 if slow else 1.0)
            status = 500 if (slow and rnd.random() < 0.03) or rnd.random() < 0.002 else 200
            t += rnd.randint(40, 60)
            rows.append(f"{t},{ep},{lat:.1f},{status}")
        (ROOT / "runs" / f"{run}.csv").write_text("\n".join(rows) + "\n")
        (ROOT / "runs" / f"{run}.json").write_text(json.dumps(
            {"run": run, "build": build_id, "users": 200, "duration_s": 300}))
    (ROOT / "thresholds.json").write_text(json.dumps(
        {"p95_regression_pct": 20, "error_rate_max_pct": 1.0, "throughput_drop_pct": 10}, indent=1))
    (ROOT / "release_notes.md").write_text(
        "# b103\n- search: switched ranking to a new ML re-ranker (synchronous call)\n"
        "- profile: copy changes\n# b102\n- login: dependency bumps\n")

if __name__ == "__main__":
    build(); print("perf data in", ROOT)
