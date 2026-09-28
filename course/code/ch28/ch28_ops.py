"""Chapter 28: AgentOps in production. Builds on ch28_agentops.py (summaries, failure
classes, the fleet report) with the tools you use every day once an agent is live:

  * log_event          structured logs that join with traces on trace_id
  * latency_breakdown  where one run's time went: model, tools, everything else
  * timeline           a text picture of one run's trajectory (an ASCII Gantt chart)
  * TAXONOMY           the 12 classes of agent failure, each with how to detect,
                       fix and evaluate it, and the chapter that covers it
  * classify_detailed  which of the 12 classes a run shows, from traces and evals
  * AGENT_SLOS         the objectives a production agent should have
  * measure_slos       each objective measured, with its error budget
  * dashboard          one static HTML page: headline numbers, SLOs, failures, tools

Runs offline on a built-in sample of runs, or on the spans ch28_otel.py wrote:

    ./course.sh python ch28_ops.py              # the built-in sample
    ./course.sh python ch28_ops.py spans.jsonl  # your own traces"""
import html
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

import ch28_agentops as ops

# ------------------------------------------------------------ 1. structured logs
EVENTS = ("run_start", "model_call", "tool_call", "run_end")

def log_event(out, event: str, trace_id: str, run_id: str = "", **fields) -> dict:
    """One JSON line per event. The trace_id is what joins a log line to its trace,
    so 'show me the logs for this slow span' is a filter, not a search."""
    if event not in EVENTS:
        raise ValueError(f"unknown event {event!r}")
    record = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
              "trace_id": trace_id, "run_id": run_id, "event": event}
    # text can hold personal data: redact it before it leaves the process
    record.update({k: ops.redact(v) if isinstance(v, str) else v
                   for k, v in fields.items()})
    line = json.dumps(record)
    if isinstance(out, list):
        out.append(line)
    else:
        out.write(line + "\n")
    return record

def error_type(result: str) -> str | None:
    """A span's error.type (an OpenTelemetry attribute) from a tool's result. Add
    span.set_attribute("error.type", ...) in traced_tool to record it."""
    if not str(result).startswith("ERROR"):
        return None
    if "not authorized" in result:
        return "not_authorized"                    # Chapter 26's identity checks
    if "security guard" in result:
        return "guard_blocked"                     # Chapter 25's guards
    return "tool_error"

# ------------------------------------------------------------ 2. where did the time go?
def _tool_name(span: dict) -> str:
    return span["attributes"].get("gen_ai.tool.name") or span["name"].split()[-1]

def latency_breakdown(spans: list[dict]) -> dict:
    """Model time, tool time and 'other': prompt building, parsing, retries, network,
    everything between the spans. A large 'other' is orchestration overhead."""
    root = None
    total = 0
    model_ms = 0.0
    tools = defaultdict(float)

    # SINGLE PASS through all spans
    for s in spans:
        if s["name"] == "invoke_agent":
            root = s
            total = s["ms"]
        elif s["name"].startswith("chat "):
            model_ms += s["ms"]
        elif s["name"].startswith("execute_tool "):
            tools[_tool_name(s)] += s["ms"]

    # Fallback if no root span
    if total == 0:
        total = sum(s["ms"] for s in spans)

    tool_ms = sum(tools.values())
    other = total - model_ms - tool_ms       # negative only if tools ran in parallel
    share = {k: round(v / total, 3) if total else 0.0
             for k, v in (("model", model_ms), ("tool", tool_ms), ("other", other))}
    return {"total_ms": total, "model_ms": model_ms, "tool_ms": tool_ms,
            "tools": dict(tools), "other_ms": round(other, 1), "share": share}

# ------------------------------------------------------------ 3. the trajectory as text
def _depths(spans: list[dict]) -> list[int]:
    """Compute depths with memoization to avoid redundant parent chain walks."""
    parent = {s["span_id"]: s.get("parent_id") for s in spans}
    depth_cache = {}  # Memoization cache

    def get_depth(span_id, visited=None):
        """Recursive depth computation with cycle detection."""
        if visited is None:
            visited = set()
        if span_id in depth_cache:
            return depth_cache[span_id]
        if span_id in visited or span_id not in parent:
            return 0
        visited.add(span_id)
        p = parent.get(span_id)
        d = 0 if not p else 1 + get_depth(p, visited)
        depth_cache[span_id] = min(d, 10)  # Cap at 10 to guard against bad data
        return depth_cache[span_id]

    return [get_depth(s["span_id"]) for s in spans]

def _starts(spans: list[dict]) -> list[float]:
    """Start times relative to the run. ch28_otel.py records durations only, so
    without start_ms we lay each span's children end to end, in the order they
    finished: the agent loop runs one step at a time."""
    if all("start_ms" in s for s in spans):
        t0 = min(s["start_ms"] for s in spans)
        return [s["start_ms"] - t0 for s in spans]
    starts = [0.0] * len(spans)
    cursor, depths = {}, _depths(spans)            # cursor: parent -> next free time
    for i in sorted(range(len(spans)), key=lambda i: depths[i]):
        s = spans[i]
        p = s.get("parent_id")
        if p in cursor:
            starts[i] = cursor[p]
            cursor[p] += s["ms"]
        cursor.setdefault(s["span_id"], starts[i])
    return starts

def _label(span: dict) -> str:
    if span["name"].startswith("execute_tool "):
        return _tool_name(span)
    return span["name"].split()[0].replace("invoke_agent", "agent")

def timeline(spans: list[dict], width: int = 60) -> str:
    """One row per span in start order: name (indented by nesting), ms, and a bar on
    a shared time axis. '#' model call, '=' tool call, 'x' failed tool, '-' agent."""
    width = min(width, 88 - 27)                    # 27 columns of label + ms + frame
    starts, depths = _starts(spans), _depths(spans)
    total = max((t + s["ms"] for t, s in zip(starts, spans)), default=0) or 1
    head = f"{total:,.0f} ms"
    rows = [f"{'span':<18}{'ms':>6} |0{head:>{width - 1}}|"]
    for i in sorted(range(len(spans)), key=lambda i: (starts[i], depths[i])):
        s = spans[i]
        err = bool(s["attributes"].get("error"))
        fill = {"execute_tool": "x" if err else "=", "chat": "#"}.get(
            s["name"].split()[0], "-")
        left = min(width - 1, round(starts[i] / total * width))
        right = max(left + 1, round((starts[i] + s["ms"]) / total * width))
        bar = " " * left + fill * (min(right, width) - left)
        name = ("  " * depths[i] + _label(s))[:15] + (" !" if err else "")
        rows.append(f"{name:<18}{s['ms']:>6.0f} |{bar:<{width}}|")
    return "\n".join(rows)

# ------------------------------------------------------------ 4. the failure taxonomy
TAXONOMY = {                   # class: (detect, mitigate, evaluate, chapters, traces?)
 "wrong_tool": ("eval: expected tool not called", "better tool names, descriptions",
                "routing eval", "3, 27", False),
 "wrong_args": ("eval: tool called with wrong args", "schemas, enums, examples",
                "argument checks", "3, 27", False),
 "tool_failure": ("tool span error flag", "retries, fallbacks, clear errors",
                  "fault injection", "7, 19", True),
 "misread_result": ("right tools, no errors, wrong answer", "structured results",
                    "answer vs data check", "8, 27", False),
 "hallucination": ("answer numbers in no tool result", "cite sources, verify",
                   "groundedness check", "6, 18, 27", False),
 "context_overflow": ("stop: context window exceeded", "trim, summarize, retrieve",
                      "long-input cases", "16", True),
 "injection": ("guard blocked a tool result", "quarantine untrusted text",
               "red-team suite", "14, 25", True),
 "planning_failure": ("trajectory eval: bad plan", "plan, then check the plan",
                      "trajectory eval", "20", False),
 "infinite_loop": ("same call repeated / step limit", "loop detector, step cap",
                   "step-limit test", "4, 28", True),
 "memory_poisoning": ("memory audit only", "provenance, write policy",
                      "poisoning tests", "17, 25", False),
 "auth_failure": ("tool error.type not_authorized", "scoped tokens, checks",
                  "permission tests", "26", True),
 "runaway": ("cost, time or steps over budget", "budgets, cheaper models",
             "budget assertions", "29", True),
}
# The False entries above can't be seen in traces alone. They need an eval (what
# SHOULD have happened) or, for memory poisoning, an audit of the memory store.

# ------------------------------------------------------------ 5. classify in detail
BUDGET = {"cost": 0.25, "ms": 40_000, "steps": 15}  # per run, well above the SLOs
CONTEXT_LIMIT = 200_000                             # tokens the model can read

def ungrounded_numbers(answer: str, sources: list[str]) -> list[str]:
    """Numbers in the answer that appear in no tool result. Numbers under 10 are
    skipped: counts like '3 orders' are often derived, not copied."""
    # Extract numbers from answer ONCE
    answer_nums = _numbers(answer)

    # Extract numbers from all sources
    seen = {n for text in sources for n in _numbers(text)}

    # Filter: only return numbers in answer that don't appear in any source
    return [n for n in answer_nums if n not in seen and float(n) >= 10]

def _numbers(text: str) -> list[str]:
    """'48,210.' -> '48210': the same number written with or without commas."""
    return [n.replace(",", "")
            for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]

def repeated_calls(spans: list[dict], run: dict, times: int = 3) -> bool:
    """The same call (tool + argument hash) `times` times. Without hashes, fall back
    to the same tool failing `times` times in a row, as ops.classify does."""
    hashes = Counter((_tool_name(s), s["attributes"]["tool.args_hash"]) for s in spans
                     if "tool.args_hash" in s["attributes"])
    if hashes:
        return max(hashes.values()) >= times
    streak, last = 0, None
    for name, _, err in run["tools"]:
        streak = streak + 1 if err and name == last else int(err)
        last = name
        if streak >= times:
            return True
    return False

def classify_detailed(run: dict, spans: list[dict] | None = None,
                      eval_result: dict | None = None, budget: dict = BUDGET) -> list:
    """Every taxonomy class this run shows (a run can have several). `run` is a
    summarize() record; eval_result may hold passed, right_tool, right_args,
    answer, tool_results, plan_ok, memory_ok, injection."""
    spans, ev = spans or [], eval_result or {}
    kinds = [s["attributes"].get("error.type") for s in spans
             if s["name"].startswith("execute_tool ")]
    special = ("not_authorized", "guard_blocked")
    plain_errors = sum(err for _, _, err in run["tools"]) - sum(k in special
                                                                 for k in kinds)
    fake = ungrounded_numbers(ev.get("answer", ""), ev.get("tool_results", []))
    max_in = max((s["attributes"].get("gen_ai.usage.input_tokens", 0) for s in spans),
                 default=0)
    found = {
        "wrong_tool": ev.get("right_tool") is False,
        "wrong_args": ev.get("right_args") is False,
        "tool_failure": plain_errors > 0,
        "hallucination": bool(fake) or ev.get("grounded") is False,
        "context_overflow": run["stop_reason"] == "model_context_window_exceeded"
                            or max_in > 0.9 * CONTEXT_LIMIT,
        "injection": "guard_blocked" in kinds or bool(ev.get("injection")),
        "planning_failure": ev.get("plan_ok") is False,
        "infinite_loop": run["stop_reason"] == "tool_use"      # hit max_iterations
                         or repeated_calls(spans, run),
        "memory_poisoning": ev.get("memory_ok") is False,       # needs a memory audit
        "auth_failure": "not_authorized" in kinds,
        "runaway": run["cost"] > budget["cost"] or run["ms"] > budget["ms"]
                   or run["model_calls"] > budget["steps"],
    }
    # the data was there, nothing failed, the right tools ran: the model misread it
    found["misread_result"] = (ev.get("passed") is False and run["tool_calls"] > 0
                               and not any(found.values()))
    return [c for c in TAXONOMY if found[c]]

# ------------------------------------------------------------ 6. SLOs for agents
AGENT_SLOS = [  # name, target, direction, measured from (the key in traces or evals)
 {"name": "Task success", "target": 0.95, "op": ">=", "key": "passed",
  "source": "evals + judge (Ch 27)"},
 {"name": "p95 latency (ms)", "target": 8000, "op": "<", "key": "ms",
  "source": "traces"},
 {"name": "Cost per task ($)", "target": 0.05, "op": "<", "key": "cost",
  "source": "traces"},
 {"name": "Tool selection accuracy", "target": 0.98, "op": ">=", "key": "right_tool",
  "source": "eval suite (Ch 27)"},
 {"name": "Unsafe action rate", "target": 0.0001, "op": "<", "key": "unsafe",
  "source": "human review (Ch 25)"},
 {"name": "Escalation accuracy", "target": 0.95, "op": ">=", "key": "escalation_ok",
  "source": "human review (Ch 19)"},
 {"name": "Retrieval recall", "target": 0.90, "op": ">=", "key": "recall",
  "source": "eval suite (Ch 18)"},
]

def _error_budget(slo: dict, labels: list) -> float | None:
    """The share of the window's allowed failures still unspent (negative: overspent).
    Only for rate SLOs, where each run either counts against the target or not."""
    if not labels or not all(isinstance(v, bool) for v in labels):
        return None
    # a False fails a success SLO (">="); a True fails a rate-of-harm SLO ("<")
    bad = labels.count(False) if slo["op"] == ">=" else labels.count(True)
    allowed = (1 - slo["target"] if slo["op"] == ">=" else slo["target"]) * len(labels)
    return round(1 - bad / allowed, 2)

def measure_slos(runs: list[dict], evals: dict, slos: list = AGENT_SLOS) -> list:
    """Each SLO with its measured value. No data means None: never a guess."""
    results = []
    for slo in slos:
        if slo["key"] == "ms":
            value = ops._pct([r["ms"] for r in runs], 0.95) if runs else None
            labels = []
        elif slo["key"] == "cost":
            value = sum(r["cost"] for r in runs) / len(runs) if runs else None
            labels = []
        else:
            labels = [e[slo["key"]] for e in evals.values()
                      if e.get(slo["key"]) is not None]
            value = sum(labels) / len(labels) if labels else None
        met = None if value is None else (value >= slo["target"] if slo["op"] == ">="
                                          else value < slo["target"])
        results.append({"name": slo["name"], "target": slo["target"], "op": slo["op"],
                        "value": value, "met": met, "n": len(labels) or len(runs),
                        "budget_left": _error_budget(slo, labels),
                        "source": slo["source"]})
    return results

def _fmt(name: str, value) -> str:
    if value is None:
        return "n/a"
    if "ms" in name:
        return f"{value:,.0f}"
    if "$" in name:
        return f"{value:.3f}"
    return f"{value:.2%}" if value < 0.01 else f"{value:.0%}"

def _budget(r: dict) -> str:
    return "" if r["budget_left"] is None else f"{r['budget_left']:.0%}"

def slo_table(results: list[dict]) -> str:
    rows = [f"{'SLO':<24}{'target':>10}{'value':>9}  {'status':<8}{'budget':>7}"
            f"  measured from"]
    for r in results:
        status = {True: "met", False: "MISSED", None: "no data"}[r["met"]]
        rows.append(f"{r['name']:<24}{r['op'] + ' ' + _fmt(r['name'], r['target']):>10}"
                    f"{_fmt(r['name'], r['value']):>9}  {status:<8}{_budget(r):>7}  "
                    f"{r['source']}")
    return "\n".join(rows)

# ------------------------------------------------------------ 7. a static dashboard
CSS = """body{font:15px/1.4 system-ui,sans-serif;color:#111;background:#fff;
max-width:860px;margin:24px auto;padding:0 16px}h1{font-size:22px}h2{font-size:17px;
margin-top:28px;border-bottom:1px solid #999}.tiles{display:flex;gap:12px;
flex-wrap:wrap}.tile{border:1px solid #666;padding:10px 16px;min-width:150px}
.tile b{display:block;font-size:26px}table{border-collapse:collapse;width:100%}
td,th{text-align:left;padding:4px 8px;border-bottom:1px solid #ccc}
td.n,th.n{text-align:right}.missed{font-weight:bold}svg text{font-size:13px}"""

def _bars(items: dict, fmt=str) -> str:
    """A horizontal bar list as inline SVG: label, bar, value. Gray prints fine."""
    if not items:
        return "<p>None.</p>"
    top = max(items.values()) or 1
    rows = []
    for i, (label, v) in enumerate(items.items()):
        y, w = i * 24, 380 * v / top
        rows.append(f'<text x="0" y="{y + 15}">{html.escape(str(label))}</text>'
                    f'<rect x="170" y="{y + 4}" width="{w:.0f}" height="14" '
                    f'fill="#555"><title>{label}: {fmt(v)}</title></rect>'
                    f'<text x="{176 + w:.0f}" y="{y + 15}">{fmt(v)}</text>')
    return (f'<svg width="640" height="{len(items) * 24}" role="img" '
            f'aria-label="bar chart">{"".join(rows)}</svg>')

STATUS = {True: "&#10003; met", False: "&#10007; MISSED", None: "no data"}

def dashboard(report: dict, slo_results: list[dict], path: str = "dashboard.html"):
    """One HTML file with no scripts or external files: it opens anywhere, can be
    attached to an incident ticket, and prints in grayscale."""
    cps = report["cost_per_success"]
    tiles = [("Success rate", f"{report['success_rate']:.0%}"),
             ("p95 latency", f"{report['p95_ms'] / 1000:.1f} s"),
             ("Cost / success", f"${cps:.3f}" if cps is not None else "n/a"),
             ("Runs", str(report["runs"]))]
    tiles = "".join(f'<div class="tile">{k}<b>{v}</b></div>' for k, v in tiles)
    slo_rows = "".join(
        f'<tr class="{"missed" if r["met"] is False else ""}">'
        f'<td>{html.escape(r["name"])}</td><td class="n">{r["op"]} '
        f'{_fmt(r["name"], r["target"])}</td>'
        f'<td class="n">{_fmt(r["name"], r["value"])}</td>'
        f'<td>{STATUS[r["met"]]}'
        f'</td><td class="n">{_budget(r)}</td><td>{html.escape(r["source"])}</td>'
        f'</tr>' for r in slo_results)
    tool_rows = "".join(
        f'<tr><td>{html.escape(str(name))}</td><td class="n">{t["calls"]}</td>'
        f'<td class="n">{t["p95_ms"]:,.0f}</td><td class="n">{t["error_rate"]:.0%}</td>'
        f'</tr>' for name, t in report["tools"].items())
    failures = report.get("taxonomy") or report["failures"]
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent dashboard</title><style>{CSS}</style></head><body>
<h1>Agent dashboard</h1><div class="tiles">{tiles}</div>
<h2>Service-level objectives</h2><table><tr><th>SLO</th><th class="n">Target</th>
<th class="n">Measured</th><th>Status</th><th class="n">Budget left</th>
<th>Source</th></tr>{slo_rows}</table>
<h2>Failure classes (runs)</h2>{_bars(failures)}
<h2>Tools</h2><table><tr><th>Tool</th><th class="n">Calls</th><th class="n">p95 ms</th>
<th class="n">Error rate</th></tr>{tool_rows}</table>
<h2>Tool p95 latency (ms)</h2>{_bars({n: t["p95_ms"] for n, t in
                                     report["tools"].items()}, lambda v: f"{v:,.0f}")}
</body></html>"""
    with open(path, "w") as f:
        f.write(page)
    return path

# ------------------------------------------------------------ 8. sample runs
def build_spans(trace_id: str, steps: list, stop_reason: str = "end_turn",
                model: str = "claude-sonnet-5", gap: float = 40) -> list[dict]:
    """Spans in ch28_otel.py's format, plus start_ms, for a scripted run. Steps are
    ("chat", ms, tokens_in, tokens_out) or ("tool", name, ms, attributes)."""
    spans, t = [], gap
    for i, step in enumerate(steps, 1):
        if step[0] == "chat":
            _, ms, tin, tout = step
            name, attrs = f"chat {model}", {"gen_ai.request.model": model,
                                            "gen_ai.usage.input_tokens": tin,
                                            "gen_ai.usage.output_tokens": tout}
        else:
            _, tool, ms, extra = step
            name, attrs = f"execute_tool {tool}", {"gen_ai.tool.name": tool,
                                                   "error": False, **extra}
        spans.append({"name": name, "trace_id": trace_id, "span_id": f"{i:016x}",
                      "parent_id": f"{0:016x}", "start_ms": t, "ms": ms,
                      "attributes": attrs})
        t += ms + gap                              # the loop's own work between steps
    spans.append({"name": "invoke_agent", "trace_id": trace_id,
                  "span_id": f"{0:016x}", "parent_id": None, "start_ms": 0, "ms": t,
                  "attributes": {"agent.stop_reason": stop_reason}})
    return spans                                   # the root last, as OTel exports it

ERR = {"error": True}

def sample() -> tuple[dict, dict]:
    """A few runs of a SQL agent (Chapter 8) and what the evals said about them."""
    spans = {
        "run-ok-1": build_spans("run-ok-1", [
            ("chat", 900, 2500, 120), ("tool", "get_schema", 120, {}),
            ("chat", 1100, 3200, 150), ("tool", "run_query", 480, {}),
            ("chat", 1300, 3600, 260)]),
        "run-ok-2": build_spans("run-ok-2", [
            ("chat", 800, 2400, 100), ("tool", "run_query", 350, {}),
            ("chat", 1200, 3000, 220)]),
        "run-loop": build_spans("run-loop", [("chat", 700, 2500, 90)] + [
            ("tool", "run_query", 300, {**ERR, "tool.args_hash": "a1f3"}),
            ("chat", 800, 3000, 90)] * 4, stop_reason="tool_use"),
        "run-denied": build_spans("run-denied", [
            ("chat", 900, 2500, 100),
            ("tool", "refund", 90, {**ERR, "error.type": "not_authorized"}),
            ("chat", 1000, 2900, 180)]),
        "run-made-up": build_spans("run-made-up", [
            ("chat", 900, 2500, 100), ("tool", "run_query", 400, {}),
            ("chat", 1400, 3100, 240)]),
    }
    evals = {
        "run-ok-1": {"passed": True, "right_tool": True, "unsafe": False,
                     "recall": 1.0},
        "run-ok-2": {"passed": True, "right_tool": True, "unsafe": False,
                     "escalation_ok": True},
        "run-loop": {"passed": False, "right_tool": True},
        "run-denied": {"passed": False, "right_tool": True, "unsafe": False,
                       "escalation_ok": True},
        "run-made-up": {"passed": False, "right_tool": True, "recall": 0.5,
                        "answer": "Revenue in March was $48,210 across 12 regions.",
                        "tool_results": ["[(41877.5,)]"]},
    }
    return spans, evals

# ------------------------------------------------------------ demo
if __name__ == "__main__":
    if len(sys.argv) > 1:
        by_trace, evals = ops.load_spans(sys.argv[1]), {}   # no evals: SLOs say n/a
    else:
        by_trace, evals = sample()
    runs = [ops.summarize(tid, s) for tid, s in by_trace.items()]
    first = next(iter(by_trace))
    print(f"TIMELINE of {first}\n{timeline(by_trace[first])}\n")
    b = latency_breakdown(by_trace[first])
    share = b["share"]
    print(f"LATENCY {b['total_ms']:,.0f} ms: model {share['model']:.0%}, tools "
          f"{share['tool']:.0%} {b['tools']}, other {share['other']:.0%}")
    log = []
    log_event(log, "run_start", first, "r1", question="Email ana@example.com sales")
    print("LOG  ", log[0], "\n\nFAILURE CLASSES")
    counts = Counter()
    for run in runs:
        found = classify_detailed(run, by_trace[run["trace_id"]],
                                  evals.get(run["trace_id"]))
        counts.update(found)
        print(f"  {run['trace_id']:<14} {', '.join(found) or 'ok'}")
    classes = [ops.classify(r, evals.get(r["trace_id"], {}).get("passed"))
               for r in runs]
    rep = ops.report(runs, classes)
    rep["taxonomy"] = dict(counts.most_common())
    slos = measure_slos(runs, evals)
    print(f"\nSLOs\n{slo_table(slos)}")
    print(f"\nwrote {dashboard(rep, slos, 'dashboard.html')}")
