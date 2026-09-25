"""Capstone 3 data: a synthetic incident. At 14:05 a deploy of checkout-service adds a
synchronous call; p95 latency and errors jump. Logs, metrics, git history, runbooks."""
import json
import random
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path("incident")
START = datetime(2026, 9, 22, 13, 0)
DEPLOY = datetime(2026, 9, 22, 14, 5)

def build():
    rnd = random.Random(3)
    (ROOT / "logs").mkdir(parents=True, exist_ok=True)
    (ROOT / "runbooks").mkdir(exist_ok=True)
    # metrics: one row per minute per service
    rows = ["minute,service,p95_ms,error_rate"]
    for m in range(120):
        t = START + timedelta(minutes=m)
        for svc in ("checkout-service", "search-service"):
            bad = svc == "checkout-service" and t >= DEPLOY
            p95 = (rnd.gauss(820, 60) if bad else rnd.gauss(310, 25)) if svc.startswith("checkout") \
                else rnd.gauss(180, 15)
            err = (rnd.uniform(0.04, 0.07) if bad else rnd.uniform(0.001, 0.004))
            rows.append(f"{t:%Y-%m-%dT%H:%M},{svc},{p95:.0f},{err:.4f}")
    (ROOT / "metrics.csv").write_text("\n".join(rows) + "\n")
    # logs
    for svc in ("checkout-service", "search-service"):
        lines = []
        for s in range(0, 7200, 20):
            t = START + timedelta(seconds=s)
            bad = svc == "checkout-service" and t >= DEPLOY and rnd.random() < 0.3
            msg = ("ERROR fraud-check timeout after 800ms (FraudClient.check_sync)" if bad
                   else "INFO request ok")
            lines.append(json.dumps({"ts": f"{t:%Y-%m-%dT%H:%M:%S}", "service": svc, "msg": msg}))
        (ROOT / "logs" / f"{svc}.jsonl").write_text("\n".join(lines) + "\n")
    (ROOT / "runbooks" / "checkout-latency.md").write_text(
        "# Checkout latency high\n1. Check recent deploys of checkout-service.\n"
        "2. Look for timeouts to downstream services (fraud, payments).\n"
        "3. If a deploy correlates, roll back with `deployctl rollback checkout-service`.\n")
    (ROOT / "runbooks" / "search-errors.md").write_text("# Search errors\n1. Check the index cluster health.\n")
    # git history with the bad deploy
    repo = ROOT / "repo"
    repo.mkdir(exist_ok=True)
    g = lambda *a, when=None: subprocess.run(["git", *a], cwd=repo, capture_output=True, check=True,
                                            env={"GIT_AUTHOR_DATE": when or "", "GIT_COMMITTER_DATE": when or "",
                                                 "PATH": "/usr/bin:/bin", "HOME": "/tmp",
                                                 "GIT_AUTHOR_NAME": "dev", "GIT_AUTHOR_EMAIL": "d@x",
                                                 "GIT_COMMITTER_NAME": "dev", "GIT_COMMITTER_EMAIL": "d@x"})
    if not (repo / ".git").exists():
        g("init", "-q")
        (repo / "checkout.py").write_text("def pay(order):\n    fraud.check_async(order)\n")
        g("add", "-A"); g("commit", "-qm", "checkout: initial", when="2026-09-20T10:00:00")
        (repo / "search.py").write_text("def search(q):\n    return index.query(q)\n")
        g("add", "-A"); g("commit", "-qm", "search: tune ranking", when="2026-09-22T11:30:00")
        (repo / "checkout.py").write_text("def pay(order):\n    fraud.check_sync(order, timeout=0.8)\n")
        g("add", "-A"); g("commit", "-qm", "checkout: make fraud check synchronous (deploy 14:05)",
                          when="2026-09-22T14:04:00")
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo, capture_output=True,
                         text=True).stdout.strip()
    return sha

if __name__ == "__main__":
    print("bad deploy commit:", build())
