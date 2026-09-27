"""Chapter 28: AgentOps. Turn traces into answers: what each run did and cost, which
runs failed and why, how the fleet is doing against its targets, and when to wake
someone up. Reads the spans that ch28_otel.py writes (spans.jsonl).

  * summarize  one record per run: steps, tokens, cost, latency, tool errors
  * classify   why a run failed, in a fixed set of classes you can count
  * report     success rate, p50/p95 latency, cost per successful run, worst tools
  * alerts     service-level objectives (SLOs) checked in code
  * redact     what must never reach a trace: secrets and personal data

    ./course.sh python ch28_agentops.py spans.jsonl"""
import json
import re
import statistics
import sys
from collections import defaultdict

from ch20_router import PRICES

# ------------------------------------------------------------ 1. redaction
REDACT = [(re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[email]"),
          (re.compile(r"\b\d(?:[ -]?\d){12,18}\b"), "[card]"),
          (re.compile(r"sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{30,}"), "[key]")]

def redact(text: str) -> str:
    """Apply before anything is written to a trace or a log."""
    for pattern, label in REDACT:
        text = pattern.sub(label, text)
    return text

# ------------------------------------------------------------ 2. one record per run
def load_spans(path: str) -> dict[str, list[dict]]:
    runs = defaultdict(list)
    for line in open(path):
        if line.strip():
            span = json.loads(line)
            runs[span["trace_id"]].append(span)
    return runs

def summarize(trace_id: str, spans: list[dict]) -> dict:
    root = next((s for s in spans if s["name"] == "invoke_agent"), None)
    chats = [s for s in spans if s["name"].startswith("chat ")]
    tools = [s for s in spans if s["name"].startswith("execute_tool ")]
    dollars = 0.0
    for c in chats:
        a = c["attributes"]
        price_in, price_out = PRICES.get(a.get("gen_ai.request.model"), (0.0, 0.0))
        dollars += (a.get("gen_ai.usage.input_tokens", 0) * price_in
                    + a.get("gen_ai.usage.output_tokens", 0) * price_out) / 1e6
    return {
        "trace_id": trace_id,
        "ms": root["ms"] if root else sum(s["ms"] for s in spans),
        "stop_reason": (root or {}).get("attributes", {}).get("agent.stop_reason"),
        "model_calls": len(chats), "tool_calls": len(tools),
        "tokens": sum(c["attributes"].get("gen_ai.usage.input_tokens", 0)
                      + c["attributes"].get("gen_ai.usage.output_tokens", 0)
                      for c in chats),
        "cost": round(dollars, 6),
        "tools": [(t["attributes"].get("gen_ai.tool.name"), t["ms"],
                   bool(t["attributes"].get("error"))) for t in tools],
    }

# ------------------------------------------------------------ 3. why did it fail?
FAILURES = ["ok", "wrong_answer", "refusal", "cut_off", "step_limit", "tool_loop",
            "tool_errors", "too_slow"]

def classify(run: dict, passed_eval: bool | None = None,
             slow_ms: float = 30_000) -> str:
    """One class per run, checked in a fixed order, so counts compare over time."""
    errors = [name for name, _, err in run["tools"] if err]
    streak, longest, last = 0, 0, None
    for name, _, err in run["tools"]:
        streak = streak + 1 if err and name == last else (1 if err else 0)
        last = name
        longest = max(longest, streak)
    if run["stop_reason"] == "refusal":
        return "refusal"
    if run["stop_reason"] in ("max_tokens", "model_context_window_exceeded"):
        return "cut_off"
    if run["stop_reason"] == "tool_use":              # the loop hit max_iterations
        return "step_limit"
    if longest >= 3:
        return "tool_loop"
    if passed_eval is False:
        return "wrong_answer"
    if len(errors) > run["tool_calls"] / 2:
        return "tool_errors"
    if run["ms"] > slow_ms:
        return "too_slow"
    return "ok"

# ------------------------------------------------------------ 4. the fleet report
def _pct(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, int(q * len(values)))] if values else 0.0

def report(runs: list[dict], classes: list[str]) -> dict:
    ok = [r for r, c in zip(runs, classes) if c == "ok"]
    by_tool = defaultdict(list)
    for r in runs:
        for name, ms, err in r["tools"]:
            by_tool[name].append((ms, err))
    return {
        "runs": len(runs),
        "success_rate": len(ok) / len(runs) if runs else 0.0,
        "p50_ms": _pct([r["ms"] for r in runs], 0.5),
        "p95_ms": _pct([r["ms"] for r in runs], 0.95),
        "cost_per_success": (sum(r["cost"] for r in runs) / len(ok)) if ok else None,
        "failures": {c: classes.count(c) for c in FAILURES
                     if c != "ok" and c in classes},
        "tools": {name: {"calls": len(v), "p95_ms": _pct([m for m, _ in v], 0.95),
                         "error_rate": round(sum(e for _, e in v) / len(v), 3)}
                  for name, v in sorted(by_tool.items())},
        "mean_steps": statistics.mean(r["model_calls"] for r in runs) if runs else 0,
    }

# ------------------------------------------------------------ 5. alerts
SLO = {"success_rate": 0.90, "p95_ms": 20_000, "cost_per_success": 0.05,
       "tool_error_rate": 0.10}

def alerts(rep: dict, slo: dict = SLO) -> list[str]:
    out = []
    if rep["success_rate"] < slo["success_rate"]:
        out.append(f"success rate {rep['success_rate']:.0%} below "
                   f"{slo['success_rate']:.0%}")
    if rep["p95_ms"] > slo["p95_ms"]:
        out.append(f"p95 latency {rep['p95_ms'] / 1000:.1f}s over "
                   f"{slo['p95_ms'] / 1000:.0f}s")
    if rep["cost_per_success"] and rep["cost_per_success"] > slo["cost_per_success"]:
        out.append(f"cost per success ${rep['cost_per_success']:.3f} over "
                   f"${slo['cost_per_success']:.2f}")
    for name, t in rep["tools"].items():
        if t["error_rate"] > slo["tool_error_rate"]:
            out.append(f"tool {name} fails {t['error_rate']:.0%} of calls")
    return out

if __name__ == "__main__":
    runs = [summarize(tid, spans) for tid, spans in
            load_spans(sys.argv[1] if len(sys.argv) > 1 else "spans.jsonl").items()]
    classes = [classify(r) for r in runs]
    rep = report(runs, classes)
    print(json.dumps(rep, indent=1))
    print("ALERTS:" if alerts(rep) else "No alerts.", *alerts(rep), sep="\n  ")
