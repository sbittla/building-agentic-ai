"""Chapter 27: an evaluation suite you run after every change.

Run:  python ch27_eval.py [cases.jsonl] [trials]      e.g.  python ch27_eval.py eval_sql.jsonl 3

Models are not deterministic, so ONE run per case proves little. Each case runs
`trials` times, and the report gives the pass rate with a 95% confidence interval,
pass^k (passed EVERY trial: what users rely on) and the flaky cases."""
import hashlib
import json
import math
import re
import sqlite3
import statistics
import sys
import time
from ch04_agent import run_agent

DB_PATH = "shop.db"

# ---------------------------------------------------------------- checking one answer
def _query(sql):
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()

def db_fingerprint() -> str:
    """A hash of every row of every table: if it changes, something was written."""
    h = hashlib.sha256()
    for (table,) in _query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        for row in _query(f"SELECT * FROM {table} ORDER BY rowid"):
            h.update(repr(row).encode())
    return h.hexdigest()

def _numbers(text):
    return [float(n.replace(",", "")) for n in re.findall(r"-?\d[\d,]*\.?\d*", text)]

def contains_value(answer: str, value) -> bool:
    """Does the answer state this value? Numbers may be written as 19,238 or 19238.0
    or rounded; text is matched case-insensitively."""
    if isinstance(value, (int, float)):
        # Small counts must be exact (399 is not 400); big amounts may be rounded (0.5%).
        tolerance = 0.51 if abs(value) < 1000 else abs(value) * 0.005
        return any(abs(n - value) <= tolerance for n in _numbers(answer))
    return str(value).lower() in answer.lower()

def check(case: dict, answer: str, messages: list, db_before: str | None = None) -> list[str]:
    """Return a list of failed checks (empty list = pass)."""
    failures = []
    used = [b.name for m in messages if m["role"] == "assistant"
            for b in m["content"] if getattr(b, "type", "") == "tool_use"]
    if "answer_sql" in case:              # the truth comes from the data, not from the case file
        rows = _query(case["answer_sql"])
        expected = rows[0][0] if rows else None
        if expected is None or not contains_value(answer, expected):
            failures.append(f"answer doesn't state the correct value {expected!r}")
    for text in case.get("must_contain", []):
        if text.lower() not in answer.lower():
            failures.append(f"missing '{text}'")
    for pattern in case.get("must_match", []):
        if not re.search(pattern, answer, re.I | re.M):
            failures.append(f"no match for /{pattern}/")
    for pattern in case.get("must_not_match", []):
        if re.search(pattern, answer, re.I | re.M):
            failures.append(f"matches forbidden /{pattern}/")
    for text in case.get("must_not_contain", []):
        if text.lower() in answer.lower():
            failures.append(f"contains forbidden '{text}'")
    for tool in case.get("must_use_tools", []):
        if tool not in used:
            failures.append(f"did not use {tool}")
    for tool in case.get("must_not_use_tools", []):
        if tool in used:
            failures.append(f"used {tool} but shouldn't have")
    if "max_tool_calls" in case and len(used) > case["max_tool_calls"]:
        failures.append(f"{len(used)} tool calls > {case['max_tool_calls']}")
    if case.get("db_unchanged") and db_before is not None and db_fingerprint() != db_before:
        failures.append("the database CHANGED")      # judge by state, not by what it said
    return failures

# ---------------------------------------------------------------- statistics
def wilson(passes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% confidence interval for a pass rate. With 20 runs and 17 passes the rate is 85%,
    but the truth could be anywhere from about 64% to 95%."""
    if n == 0:
        return 0.0, 0.0
    p = passes / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)

def summarize(rows) -> dict:
    by_case = {}
    for r in rows:
        by_case.setdefault(r["id"], []).append(r["pass"])
    passes, n = sum(r["pass"] for r in rows), len(rows)
    lo, hi = wilson(passes, n)
    return {"cases": len(by_case), "runs": n, "pass_rate": passes / n if n else 0.0,
            "ci95": (lo, hi),
            "pass_all_trials": sum(all(v) for v in by_case.values()) / len(by_case),   # pass^k
            "pass_any_trial": sum(any(v) for v in by_case.values()) / len(by_case),    # pass@k
            "flaky": sorted(c for c, v in by_case.items() if any(v) and not all(v)),
            "median_s": statistics.median(r["seconds"] for r in rows),
            "mean_tokens": statistics.mean(r["tokens"] for r in rows)}

# ---------------------------------------------------------------- running the suite
def run_suite(cases, tools, run_tool, system, trace_path="traces.jsonl", trials=1):
    rows = []
    with open(trace_path, "a") as trace:
        for case in cases:
            for trial in range(1, trials + 1):
                before = db_fingerprint() if case.get("db_unchanged") else None
                t0 = time.perf_counter()
                answer, messages, stats = run_agent(case["question"], tools, run_tool,
                                                    system=system, verbose=False)
                seconds = time.perf_counter() - t0
                failures = check(case, answer, messages, before)
                used = [b.name for m in messages if m["role"] == "assistant"
                        for b in m["content"] if getattr(b, "type", "") == "tool_use"]
                rows.append({"id": case["id"], "trial": trial, "pass": not failures,
                             "seconds": seconds,
                             "tokens": stats["input_tokens"] + stats["output_tokens"],
                             "tool_calls": stats["tool_calls"], "tools_used": used,
                             "failures": failures})
                trace.write(json.dumps({**rows[-1], "question": case["question"],
                                        "answer": answer}) + "\n")
                print(f"{'PASS' if not failures else 'FAIL'} {case['id']:<20} #{trial} "
                      f"{seconds:5.1f}s {rows[-1]['tokens']:>6} tok  {'; '.join(failures)}")
    s = summarize(rows)
    lo, hi = s["ci95"]
    print(f"\n{s['cases']} cases x {trials} trials: pass rate {s['pass_rate']:.0%} "
          f"(95% CI {lo:.0%}-{hi:.0%}) | passed every trial: {s['pass_all_trials']:.0%} | "
          f"median {s['median_s']:.1f}s | mean tokens {s['mean_tokens']:.0f}")
    if s["flaky"]:
        print("Flaky (passed some trials, failed others):", ", ".join(s["flaky"]))
    return rows

if __name__ == "__main__":
    import ch08_sql_tools as sql
    path = sys.argv[1] if len(sys.argv) > 1 else "eval_sql.jsonl"
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    cases = [json.loads(line) for line in open(path) if line.strip()]
    run_suite(cases, sql.TOOLS, sql.run_tool, sql.SYSTEM, trials=trials)
