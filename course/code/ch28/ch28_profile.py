"""Chapter 28: correlating traces with resources. A trace says WHERE a run's time went
(this tool span took 1.9 s); it doesn't say WHY. This module joins each span with what
the machine and its dependencies were doing during that span, and with the profiler's
stack samples taken inside it, so "run_sql is slow" becomes "run_sql is slow when the
database is busy, not when the CPU is".

  * normalize         one span shape, from ch28_otel.py's spans or simple dicts
  * resources_during  the time-weighted mean of each metric over a span's window,
                      and the share of the span spent while each one was saturated
  * attribute         every span with its resources and the time each saturation cost
  * kind_summary      per span kind: count, p50, p95, total time, tokens, resources
  * correlate         per group: rank correlation of latency with each signal, and
                      p50 latency while saturated against p50 while not
  * diagnose          plain-language verdicts from those numbers
  * top_frames        the leaf functions the profiler saw during the slowest spans

Three inputs, all joined on span id or on time:
  spans     {"trace_id", "span_id", "name", "start_ms", "ms", "attributes"}  (Ch 28)
            or {"trace_id", "name", "kind", "start_ms", "end_ms", "tokens"}
  samples   {"t": ms, "cpu": %, "mem": %, "gpu": %, "db_ms": ms, "net_ms": ms}
            one per interval (1 s here), covering [t, t + interval)
  stacks    {"t": ms, "stack": ["outermost", ..., "leaf"], "span_id": optional}

The demo runs offline on ten minutes of synthetic but realistic traffic, generated
deterministically, with two incidents injected:

    ./course.sh python ch28_profile.py"""
import bisect
import random
import statistics
from collections import Counter, defaultdict

# ------------------------------------------------------------ 1. one span shape
METRICS = ("cpu", "mem", "gpu", "db_ms", "net_ms")
# Above these, a resource is saturated: requests queue for it and latency grows fast.
SATURATION = {"cpu": 85.0, "mem": 90.0, "gpu": 90.0, "db_ms": 250.0, "net_ms": 100.0}
LABELS = {"cpu": "the CPU", "mem": "memory", "gpu": "the GPU", "db_ms": "the database",
          "net_ms": "the network"}

def _kind(name: str) -> str:
    if name.startswith("chat"):
        return "model"
    if name.startswith("execute_tool"):
        return "tool"
    if name.startswith("queue"):
        return "queue"
    return "agent" if name == "invoke_agent" else "other"

def normalize(span: dict) -> dict:
    """The fields this module needs, from either span shape. `group` is what spans
    are compared within: the tool's name for tools, the span kind otherwise."""
    a = span.get("attributes", {})
    kind = span.get("kind") or _kind(span["name"])
    start = float(span["start_ms"])
    end = float(span["end_ms"]) if "end_ms" in span else start + span["ms"]
    tool = a.get("gen_ai.tool.name") or (span["name"].split()[-1]
                                         if kind == "tool" else None)
    return {"trace_id": span["trace_id"], "span_id": span.get("span_id"),
            "name": span["name"], "kind": kind, "group": tool or kind,
            "start": start, "end": end, "ms": end - start,
            "tokens_out": span.get("tokens", a.get("gen_ai.usage.output_tokens", 0)),
            "rows": a.get("db.rows", 0)}

# ------------------------------------------------------------ 2. resources over a span
def resources_during(span: dict, samples: list[dict], interval_ms: float = 1000,
                     _times: list | None = None) -> dict:
    """Each metric's mean over the span's window, weighted by how much of the span
    each sample's interval covers, and the share of the span spent while each
    metric was above its SATURATION threshold. A 300 ms span inside one 1 s sample
    gets that sample's values: sample at least as often as your spans are short."""
    times = _times or [s["t"] for s in samples]
    i = max(0, bisect.bisect_right(times, span["start"]) - 1)
    total = defaultdict(float)
    hot = defaultdict(float)
    covered = 0.0
    while i < len(samples) and samples[i]["t"] < span["end"]:
        s = samples[i]
        overlap = min(span["end"], s["t"] + interval_ms) - max(span["start"], s["t"])
        if overlap > 0:
            covered += overlap
            for m in METRICS:
                if m in s:
                    total[m] += s[m] * overlap
                    if s[m] > SATURATION[m]:
                        hot[m] += overlap
        i += 1
    if not covered:
        return {"mean": {}, "saturated": {}}
    return {"mean": {m: round(v / covered, 1) for m, v in total.items()},
            "saturated": {m: round(hot[m] / covered, 3) for m in total}}

def attribute(spans: list[dict], samples: list[dict], interval_ms: float = 1000,
              min_share: float = 0.5) -> list[dict]:
    """Every leaf span (not the run itself) with its resources. `saturated_by` lists
    the metrics that were saturated for at least `min_share` of the span, and
    `ms_under` how many of the span's ms each saturation overlapped."""
    samples = sorted(samples, key=lambda s: s["t"])
    times = [s["t"] for s in samples]
    rows = []
    for raw in spans:
        s = normalize(raw)
        if s["kind"] == "agent":
            continue
        r = resources_during(s, samples, interval_ms, times)
        s["res"] = r["mean"]
        hot = r["saturated"]
        s["ms_under"] = {m: round(f * s["ms"], 1) for m, f in hot.items() if f}
        s["saturated_by"] = [m for m, f in hot.items() if f >= min_share]
        rows.append(s)
    return rows

# ------------------------------------------------------------ 3. per kind, per group
def _pct(values: list[float], q: float) -> float:
    v = sorted(values)
    return v[min(len(v) - 1, int(q * len(v)))] if v else 0.0

def kind_summary(rows: list[dict]) -> dict:
    """Per group: spans, p50/p95 ms, total seconds and share of all span time,
    output tokens, and the mean of each resource while those spans ran."""
    groups = defaultdict(list)
    for r in rows:
        groups[r["group"]].append(r)
    all_ms = sum(r["ms"] for r in rows) or 1
    out = {}
    for g, rs in sorted(groups.items(), key=lambda kv: -sum(r["ms"] for r in kv[1])):
        ms = [r["ms"] for r in rs]
        res = {m: round(statistics.fmean(r["res"][m] for r in rs if m in r["res"]), 1)
               for m in METRICS if any(m in r["res"] for r in rs)}
        out[g] = {"n": len(rs), "p50": round(_pct(ms, 0.5)),
                  "p95": round(_pct(ms, 0.95)), "total_s": round(sum(ms) / 1000, 1),
                  "share": round(sum(ms) / all_ms, 3),
                  "tokens_out": sum(r["tokens_out"] for r in rs), **res}
    return out

def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):                     # ties share their average rank
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2
        i = j + 1
    return ranks

def rank_corr(x: list[float], y: list[float]) -> float:
    """Spearman's rank correlation: +1 when y always rises with x. Ranks, not raw
    values, so one huge outlier can't manufacture a correlation and a threshold
    effect (fine until 85% CPU, then slow) still counts, if only for the spans it
    hits. Near 0 means no monotone relation, not "no effect": check the lift too."""
    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
        return 0.0
    return round(statistics.correlation(_ranks(x), _ranks(y)), 2)

SPAN_SIGNALS = ("tokens_out", "rows")         # drivers inside the span itself

def correlate(rows: list[dict], min_n: int = 5) -> dict:
    """Per group, for every signal: the rank correlation of span latency with it,
    and for resources, p50 latency while saturated vs while not (with counts)."""
    groups = defaultdict(list)
    for r in rows:
        groups[r["group"]].append(r)
    out = {}
    for g, rs in groups.items():
        ms = [r["ms"] for r in rs]
        entry = {"n": len(rs), "p95": round(_pct(ms, 0.95)), "r": {}, "saturated": {}}
        for m in METRICS:
            have = [r for r in rs if m in r["res"]]  # a 0 ms span covers no sample
            if have:
                entry["r"][m] = rank_corr([r["res"][m] for r in have],
                                          [r["ms"] for r in have])
                hot = [r["ms"] for r in have if m in r["saturated_by"]]
                cold = [r["ms"] for r in have if m not in r["saturated_by"]]
                if len(hot) >= min_n and len(cold) >= min_n:
                    p_hot, p_cold = statistics.median(hot), statistics.median(cold)
                    entry["saturated"][m] = {"n": len(hot), "p50_hot": round(p_hot),
                                             "p50_cold": round(p_cold),
                                             "lift": round(p_hot / p_cold, 1)}
        for sig in SPAN_SIGNALS:
            if any(r[sig] for r in rs):
                entry["r"][sig] = rank_corr([r[sig] for r in rs], ms)
        out[g] = entry
    return out

# ------------------------------------------------------------ 4. verdicts
def diagnose(corr: dict, r_min: float = 0.3, lift_min: float = 1.5,
             quiet_ms: float = 50) -> list[str]:
    """A resource explains a group's latency when spans run at least lift_min times
    slower (p50) while it's saturated AND the rank correlation is at least r_min.
    Both, because a lift can come from a handful of unlucky spans and a correlation
    from load raising everything at once. r_min is low on purpose: a threshold
    effect that hits 15% of spans gives a modest r. A span signal (tokens, rows)
    explains latency on its own at r >= 0.5."""
    lines = []
    for g, e in sorted(corr.items()):
        who = {"model": "model calls", "queue": "queue waits",
               "other": "other spans"}.get(g, f"tool `{g}`")
        if e["p95"] < quiet_ms:
            lines.append(f"{who}: p95 {e['p95']:,} ms, nothing to explain")
            continue
        res, sat = e["r"], e["saturated"]
        guilty = [m for m in sat if sat[m]["lift"] >= lift_min and res[m] >= r_min]
        drivers = [s for s in SPAN_SIGNALS if res.get(s, 0) >= 0.5]
        if guilty:
            m = max(guilty, key=lambda m: sat[m]["lift"])
            s = sat[m]
            calm = [k for k in sat if sat[k]["lift"] < 1.2]
            contrast = "".join(f", not when {LABELS[k]} is (x{sat[k]['lift']})"
                               for k in calm)
            lines.append(f"{who} is slow when {LABELS[m]} is busy: p50 "
                         f"{s['p50_hot']:,} ms while saturated vs {s['p50_cold']:,} ms "
                         f"(x{s['lift']}, {s['n']} spans, r={res[m]:.2f}){contrast}")
        if drivers:
            d = max(drivers, key=lambda d: res[d])
            what = {"tokens_out": "output tokens", "rows": "rows returned"}[d]
            tail = "" if guilty else ", not local resources"
            lines.append(f"{who}: latency follows {what} (r={res[d]:.2f}){tail}: "
                         "the work itself, not contention")
        if not guilty and not drivers:
            lines.append(f"{who}: no resource or span signal explains the latency; "
                         "read the profile of its slowest spans")
    return lines

# ------------------------------------------------------------ 5. the profile
def top_frames(stacks: list[dict], spans: list[dict], n: int = 5) -> list[tuple]:
    """The leaf frames (where the thread was) sampled inside these spans, with the
    caller that led there, as (frame, caller, share). Samples labelled with a
    span_id join on it; unlabelled ones join on time, which mixes in any other
    request running at the same moment."""
    ids = {s["span_id"] for s in spans if s.get("span_id")}
    windows = sorted((s["start"], s["end"]) for s in spans)
    starts = [w[0] for w in windows]
    counts = Counter()
    for st in stacks:
        if st.get("span_id") is not None:
            hit = st["span_id"] in ids
        else:
            i = bisect.bisect_right(starts, st["t"]) - 1
            hit = any(a <= st["t"] < b for a, b in windows[max(0, i - 50):i + 1])
        if hit:
            frames = st["stack"]
            counts[(frames[-1], frames[-2] if len(frames) > 1 else "")] += 1
    total = sum(counts.values()) or 1
    return [(f, c, round(k / total, 3)) for (f, c), k in counts.most_common(n)]

def slowest(rows: list[dict], group: str, q: float = 0.95,
            unexplained: bool = False) -> list[dict]:
    """The spans of one group at or above its q-th percentile. With
    unexplained=True, first drop the spans a saturated resource accounts for, then
    take the slowest of the rest: the tail that resources don't explain."""
    rs = [r for r in rows if r["group"] == group
          and not (unexplained and r["saturated_by"])]
    cut = _pct([r["ms"] for r in rs], q)
    return [r for r in rs if r["ms"] >= cut]

# ------------------------------------------------------------ 6. synthetic traffic
DB_BUSY = (120_000, 240_000)      # a batch job holds the database: 2:00 to 4:00
CPU_BUSY = (360_000, 450_000)     # a noisy neighbour takes the CPU: 6:00 to 7:30

def _busy(t: float, window: tuple) -> bool:
    return window[0] <= t < window[1]

def synthetic(seed: int = 28, minutes: int = 10, every_ms: int = 2_000,
              profile_hz: int = 20) -> tuple[list, list, list]:
    """Ten minutes of a SQL agent (Chapter 8) on a self-hosted model: a run starts
    every ~2 s and makes queue -> chat -> run_sql -> chat -> render_chart -> chat.
    How each span's time is produced, so you can check what the analysis finds:
      chat          250 ms to first token + ~12 ms per output token (GPU never full)
      run_sql       80 ms + 3 round trips x the DB's query time + 0.03 ms per row
      render_chart  250 ms of CPU work, stretched when the host CPU is above 80%
    Returns (spans in ch28_otel.py's format, resource samples, stack samples)."""
    rng = random.Random(seed)
    end = minutes * 60_000
    samples = []
    for t in range(0, end, 1000):
        samples.append({
            "t": t,
            "cpu": round(rng.uniform(92, 98) if _busy(t, CPU_BUSY)
                         else rng.gauss(38, 8), 1),
            "mem": round(rng.gauss(62, 2), 1),
            "gpu": round(min(88.0, rng.gauss(58, 10)), 1),
            "db_ms": round(rng.uniform(350, 900) if _busy(t, DB_BUSY)
                           else rng.uniform(12, 40), 1),
            "net_ms": round(rng.uniform(2, 6), 1)})
    at = {s["t"]: s for s in samples}
    def now(t):
        return at[min(end - 1000, int(t) // 1000 * 1000)]

    spans, stacks = [], []
    step_ms = 1000 / profile_hz
    def profile(span_id, start, ms, parts):
        # parts: [(stack, ms)] laid end to end; one sample every step_ms
        t, edges, acc = start, [], 0.0
        for stack, part_ms in parts:
            acc += part_ms
            edges.append((acc, stack))
        k = 0
        while (t - start) < ms:
            off = (t - start) / ms * acc
            stack = next(st for e, st in edges if off < e)
            stacks.append({"t": round(t, 1), "span_id": span_id, "stack": stack})
            k += 1
            t = start + k * step_ms
    def add(tid, n, name, start, ms, attrs):
        sid = f"{tid}-{n}"
        spans.append({"name": name, "trace_id": tid, "span_id": sid,
                      "parent_id": f"{tid}-0", "start_ms": round(start, 1),
                      "ms": round(ms, 1), "attributes": attrs})
        return sid

    loop = ["agent_loop"]
    run = 0
    t0 = 0.0
    while t0 < end - 15_000:
        tid = f"run-{run:03d}"
        t, n = t0, 1
        wait = rng.uniform(0, 30)
        add(tid, n, "queue wait_for_slot", t, wait, {})
        t += wait + 20
        for step in ("plan", "sql", "summary", "chart", "answer"):
            n += 1
            if step in ("plan", "summary", "answer"):
                out = rng.randint(*{"plan": (60, 200), "summary": (80, 300),
                                    "answer": (150, 600)}[step])
                ms = 250 + out * rng.gauss(12, 1)
                sid = add(tid, n, "chat qwen-32b", t, ms,
                          {"gen_ai.request.model": "qwen-32b",
                           "gen_ai.usage.input_tokens": 3000 + 400 * n,
                           "gen_ai.usage.output_tokens": out})
                profile(sid, t, ms, [(loop + ["client.create", "http.read",
                                              "ssl.recv"], ms)])
            elif step == "sql":
                rows = (rng.randint(20_000, 60_000) if rng.random() < 0.06
                        else rng.randint(10, 500))
                wait_db = 3 * now(t)["db_ms"]
                encode = rows * 0.03
                ms = 80 + wait_db + encode + rng.uniform(-10, 10)
                sid = add(tid, n, "execute_tool run_sql", t, ms,
                          {"gen_ai.tool.name": "run_sql", "error": False,
                           "db.rows": rows})
                base = loop + ["run_tool", "run_sql"]
                profile(sid, t, ms, [(base + ["pool.get"], 40),
                                     (base + ["cursor.execute", "socket.recv"],
                                      wait_db + 40),
                                     (base + ["rows_to_json", "json.dumps"], encode)])
            else:
                cpu = now(t)["cpu"]
                ms = 250 * (1 + 3 * max(0.0, cpu - 80) / 20) * rng.uniform(0.9, 1.1)
                sid = add(tid, n, "execute_tool render_chart", t, ms,
                          {"gen_ai.tool.name": "render_chart", "error": False})
                base = loop + ["run_tool", "render_chart"]
                profile(sid, t, ms, [(base + ["plot", "draw_path"], 0.8 * ms),
                                     (base + ["png_encode", "zlib.compress"],
                                      0.2 * ms)])
            t += ms + 20
        spans.append({"name": "invoke_agent", "trace_id": tid, "span_id": f"{tid}-0",
                      "parent_id": None, "start_ms": round(t0, 1),
                      "ms": round(t - t0, 1), "attributes": {}})
        run += 1
        t0 += rng.uniform(0.6, 1.4) * every_ms
    return spans, samples, stacks

# ------------------------------------------------------------ demo
def _summary_table(summary: dict) -> str:
    head = (f"{'group':<14}{'n':>5}{'p50 ms':>8}{'p95 ms':>8}{'total s':>9}"
            f"{'share':>7}{'cpu%':>6}{'gpu%':>6}{'db ms':>7}")
    lines = [head]
    for g, s in summary.items():
        lines.append(f"{g:<14}{s['n']:>5}{s['p50']:>8,}{s['p95']:>8,}"
                     f"{s['total_s']:>9,.0f}{s['share']:>7.0%}{s.get('cpu', 0):>6.0f}"
                     f"{s.get('gpu', 0):>6.0f}{s.get('db_ms', 0):>7.0f}")
    return "\n".join(lines)

def _corr_table(corr: dict) -> str:
    cols = METRICS + SPAN_SIGNALS
    names = {"tokens_out": "tokens", "db_ms": "db", "net_ms": "net"}
    lines = [f"{'group':<14}" + "".join(f"{names.get(c, c):>8}" for c in cols)]
    for g, e in sorted(corr.items()):
        lines.append(f"{g:<14}" + "".join(
            f"{e['r'][c]:>8.2f}" if c in e["r"] else f"{'':>8}" for c in cols))
    return "\n".join(lines)

def _frames(frames: list[tuple]) -> str:
    return "\n".join(f"  {share:>4.0%}  {f:<16} called from {c}"
                     for f, c, share in frames)

if __name__ == "__main__":
    spans, samples, stacks = synthetic()
    runs = sum(s["name"] == "invoke_agent" for s in spans)
    print(f"SYNTHETIC TRAFFIC: {runs} runs in 10 minutes, {len(spans):,} spans, "
          f"{len(samples)} resource samples, {len(stacks):,} stack samples")
    print("  injected: the database busy 2:00-4:00, the CPU saturated 6:00-7:30\n")
    rows = attribute(spans, samples)
    print("WHERE THE TIME WENT, per span group\n" + _summary_table(kind_summary(rows)))
    corr = correlate(rows)
    print("\nRANK CORRELATION of span latency with each signal during the span\n"
          + _corr_table(corr))
    print("\nP50 LATENCY WHILE A RESOURCE WAS SATURATED vs NOT")
    for g in ("run_sql", "render_chart"):
        for m, s in corr[g]["saturated"].items():
            print(f"  {g:<13} {m}>{SATURATION[m]:g}: {s['n']:>3} spans, p50 "
                  f"{s['p50_hot']:,} ms vs {s['p50_cold']:,} ms (x{s['lift']})")
    print("\nDIAGNOSIS")
    for line in diagnose(corr):
        print("  - " + line)
    stack_rows = [r for r in rows if r["kind"] == "tool"]
    for g in ("run_sql", "render_chart"):
        worst = slowest(stack_rows, g)
        why = Counter(m for r in worst for m in r["saturated_by"] or ["none"])
        print(f"\nSLOWEST 5% OF {g} ({len(worst)} spans), saturated during them: "
              + ", ".join(f"{m} {k}" for m, k in why.most_common()))
        print(_frames(top_frames(stacks, worst, 3)))
    rest = slowest(stack_rows, "run_sql", unexplained=True)
    print(f"\nSLOWEST 5% OF run_sql WITH NO SATURATION ({len(rest)} spans): "
          f"median {statistics.median(r['rows'] for r in rest):,.0f} rows")
    print(_frames(top_frames(stacks, rest, 3)))
