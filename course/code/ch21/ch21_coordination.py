"""Chapter 21: does the team pay for itself? Coordination economics for multi-agent
systems. A team of agents is not automatically better than one agent: it makes more
model calls, copies context into every worker, sends messages, waits for its slowest
worker, retries, and gives failures more places to start. This module measures that
overhead from per-run stats and turns it into a decision.

  * normalize          one run's stats in one shape (run_agent's keys, plus a few)
  * coordination_report  a single agent and a team, side by side, and the overhead terms
  * decide             is the team worth it? success gain x value vs extra cost,
                       or a latency/quality requirement only the team meets
  * failure_propagation  how per-step reliability compounds over n steps

    ./course.sh python ch21_coordination.py

The demo measures a single agent and a lead with workers on the simulator from
section 29.8 (offline, free, the same numbers on every machine). If the simulator or
its database isn't there, it falls back to illustrative numbers and says so."""
import math
import statistics

# ------------------------------------------------------------ 1. one run, one shape
def normalize(run: dict) -> dict:
    """One run's stats with run_agent's keys (steps, input_tokens, output_tokens), plus
    ok, latency_s and cost. Also accepts the benchmark's names (tokens_in, tokens_out,
    ms). Team-only keys default to zero: lead_calls, messages, duplicated_tokens,
    retries, failed_parts and worker_latency_s (one latency per worker)."""
    tin = run.get("input_tokens", run.get("tokens_in", 0))
    tout = run.get("output_tokens", run.get("tokens_out", 0))
    latency = run["latency_s"] if "latency_s" in run else run.get("ms", 0) / 1000
    if "cost" in run:
        dollars = run["cost"]
    else:                                     # price it like Chapter 20 does
        from ch20_router import cost
        dollars = cost({"input_tokens": tin, "output_tokens": tout,
                        **({"model": run["model"]} if "model" in run else {})})
    return {"ok": bool(run.get("ok", run.get("success", False))),
            "calls": run.get("steps", run.get("calls", 0)),
            "input_tokens": tin, "output_tokens": tout,
            "latency_s": latency, "cost": dollars,
            "lead_calls": run.get("lead_calls", 0),
            "messages": run.get("messages", 0),
            "duplicated_tokens": run.get("duplicated_tokens", 0),
            "retries": run.get("retries", 0),
            "failed_parts": run.get("failed_parts", 0),
            "worker_latency_s": list(run.get("worker_latency_s", []))}

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% confidence interval for a success rate (the measurement interlude)."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)

def p95(values: list[float]) -> float:
    values = sorted(values)
    return values[min(len(values) - 1, round(0.95 * (len(values) - 1)))] if values else 0.0

def summarize(runs: list[dict]) -> dict:
    """Means per task over many runs of one design."""
    runs = [normalize(r) for r in runs]
    n, ok = len(runs), sum(r["ok"] for r in runs)
    mean = lambda key: statistics.mean(r[key] for r in runs) if runs else 0.0
    waits = [max(r["worker_latency_s"]) - statistics.mean(r["worker_latency_s"])
             for r in runs if len(r["worker_latency_s"]) > 1]
    spent = sum(r["cost"] for r in runs)
    return {"tasks": n, "success": ok / n if n else 0.0, "success_ci": wilson(ok, n),
            "calls": mean("calls"), "lead_calls": mean("lead_calls"),
            "input_tokens": mean("input_tokens"), "output_tokens": mean("output_tokens"),
            "duplicated_tokens": mean("duplicated_tokens"), "messages": mean("messages"),
            "retries": mean("retries"),
            "sync_wait_s": statistics.mean(waits) if waits else 0.0,
            "runs_with_failed_part": sum(r["failed_parts"] > 0 for r in runs) / n if n else 0.0,
            "latency_s": mean("latency_s"),
            "p95_s": p95([r["latency_s"] for r in runs]),
            "cost_per_task": spent / n if n else 0.0,
            "cost_per_success": spent / ok if ok else None}

# ------------------------------------------------------------ 2. the overhead report
def coordination_report(single_runs: list[dict], team_runs: list[dict]) -> dict:
    """The same tasks, run by one agent and by a team. Returns both summaries and the
    overhead terms: what the team spends that the single agent doesn't."""
    s, t = summarize(single_runs), summarize(team_runs)
    return {"single": s, "team": t, "overhead": {
        "extra_calls": t["calls"] - s["calls"],
        "lead_calls": t["lead_calls"],                 # planning and synthesis
        "extra_input_tokens": t["input_tokens"] - s["input_tokens"],
        "duplicated_tokens": t["duplicated_tokens"],   # the same context, in every worker
        "messages": t["messages"],                     # briefs out, results back
        "sync_wait_s": t["sync_wait_s"],               # waiting for the slowest worker
        "extra_retries": t["retries"] - s["retries"],
        "extra_latency_s": t["latency_s"] - s["latency_s"],
        "extra_p95_s": t["p95_s"] - s["p95_s"],
        "runs_with_failed_part": t["runs_with_failed_part"],
        "success_gain": t["success"] - s["success"],
        "extra_cost_per_task": t["cost_per_task"] - s["cost_per_task"],
        "cost_ratio": t["cost_per_task"] / s["cost_per_task"] if s["cost_per_task"] else None}}

# ------------------------------------------------------------ 3. the decision
def _meets(d: dict, min_success, latency_slo_s) -> bool:
    return ((min_success is None or d["success"] >= min_success)
            and (latency_slo_s is None or d["p95_s"] <= latency_slo_s))

def decide(report: dict, value_per_success: float, *, min_success: float | None = None,
           latency_slo_s: float | None = None) -> dict:
    """Does the capability the team adds exceed what coordination costs? The team wins
    only if (a) it meets a requirement (success rate, p95 latency) the single agent
    misses, or (b) its success gain, valued per task, exceeds its extra cost per task
    AND the gain is measurable (the confidence intervals don't overlap)."""
    s, t, o = report["single"], report["team"], report["overhead"]
    team_ok, single_ok = _meets(t, min_success, latency_slo_s), _meets(s, min_success,
                                                                      latency_slo_s)
    gain, extra = o["success_gain"], o["extra_cost_per_task"]
    out = {"gain_value_per_task": gain * value_per_success, "extra_cost_per_task": extra,
           "break_even_value": extra / gain if gain > 0 else None}
    if team_ok and not single_ok:
        return {**out, "verdict": "team",
                "reason": "the team meets a requirement the single agent misses"}
    if single_ok and not team_ok:
        return {**out, "verdict": "single agent",
                "reason": "the single agent meets the requirements and the team doesn't"}
    measurable = t["success_ci"][0] > s["success_ci"][1]
    if gain > 0 and not measurable:
        return {**out, "verdict": "single agent",
                "reason": "no measurable success gain (the intervals overlap); "
                          "add tasks before you decide"}
    if gain * value_per_success > extra:
        return {**out, "verdict": "team",
                "reason": "the success gain is worth more than the extra cost"}
    return {**out, "verdict": "single agent",
            "reason": "the extra cost is more than the success gain is worth"}

# ------------------------------------------------------------ 4. failure propagation
def failure_propagation(p_step: float, n: int, *, parallel: bool = False,
                        contained: bool = True, retries: int = 0,
                        lead_steps: int = 0) -> dict:
    """How reliability compounds. n worker steps, each right with probability p_step,
    plus lead_steps (planning, synthesis) that must all be right.

    p_task: every part right. That is p^n whatever the topology: more steps, more
            ways to fail.
    share_of_parts: the expected share of parts you still get right. Sequentially, a
            failure spoils every step after it. In parallel with containment, each
            part stands alone; without containment, one crash takes down the team.
    Retries apply only to contained failures: you can't retry a failure you can't see."""
    p = 1 - (1 - p_step) ** (1 + (retries if contained else 0))
    lead = p_step ** lead_steps
    if not parallel:
        share = statistics.mean(p ** k for k in range(1, n + 1))
    elif contained:
        share = p
    else:
        share = p ** n
    return {"p_step": p, "p_task": lead * p ** n, "share_of_parts": lead * share}

# ------------------------------------------------------------ 5. measured runs (optional)
def simulated_runs(multi_part: bool, reps: int = 5, tool_ms: float = 250,
                   parallel_tools: bool = False) -> tuple:
    """One agent and a lead with workers on the same questions, on the simulator from
    section 29.8, with the same random numbers for both. parallel_tools lets the single
    agent run one turn's tool calls at the same time. Returns (single, team) lists of
    per-run stats in normalize()'s shape, including the team-only terms."""
    import ch29_benchmark as b
    single, multi = b.load_cases()
    for c in single + multi:
        b.QUESTIONS[c["question"]] = c["sqls"]
    for c in multi:                                    # how the simulated lead splits
        parts = [f"{c['question']} (part {i + 1}: {q})" for i, q in enumerate(c["sqls"])]
        b.SUBQUESTIONS[c["question"]] = parts
        for part, q in zip(parts, c["sqls"]):
            b.QUESTIONS[part] = [q]
    cases, key = (multi, "E2") if multi_part else (single, "E1")

    class Clock(b.VirtualTime):                        # records each worker's latency
        def parallel(self, fn, items):
            def timed(item):
                t0 = self.t
                out = fn(item)
                self.workers.append(self.t - t0)
                return out
            self.workers = []
            return super().parallel(timed, items)

    class Client(b.SimClient):                         # records who made each call
        def create(self, model, system="", messages=(), **kw):
            resp = super().create(model, system=system, messages=messages, **kw)
            lead = system.startswith((b.PLAN, b.SYNTH))
            self.log.append((lead, len(messages) == 1, resp.usage.input_tokens))
            return resp

    def run(case, design, seed):
        clock, made = Clock(), []
        def client_for(seed_key, backend):
            c = Client(seed_key, backend)
            c.log = []
            made.append(c)
            return c
        r = b.task(case, design, backend=clock, client_for=client_for, model=b.LARGE,
                   seed_key=seed, tool_ms=tool_ms, parallel=parallel_tools)
        log = made[0].log
        starts = [tin for lead, first, tin in log if not lead and first]
        workers = getattr(clock, "workers", [])
        return {**r, "lead_calls": sum(lead for lead, _, _ in log),
                "messages": 2 * len(workers),          # one brief out, one result back
                "duplicated_tokens": sum(starts) - starts[0] if design != "agent" else 0,
                "worker_latency_s": [ms / 1000 for ms in workers],
                "failed_parts": (r.get("answer") or "").count("unknown")}

    seeds = [(c, f"{key}:{c['id']}:{rep}") for rep in range(reps) for c in cases]
    return ([run(c, "agent", s) for c, s in seeds],
            [run(c, "multi-agent", s) for c, s in seeds])

ILLUSTRATIVE = {   # per-task means from the simulator, used only when it can't run
    False: (100, {"ok": 0.97, "steps": 3, "tokens_in": 1000, "tokens_out": 109, "ms": 3970,
                  "cost": 0.0031},
                 {"ok": 0.97, "steps": 5, "tokens_in": 1200, "tokens_out": 125, "ms": 6230,
                  "cost": 0.0041, "lead_calls": 2, "messages": 2}),
    True: (30, {"ok": 28 / 30, "steps": 3, "tokens_in": 1100, "tokens_out": 129, "ms": 4940,
                "cost": 0.0038},
               {"ok": 29 / 30, "steps": 8.5, "tokens_in": 2477, "tokens_out": 275, "ms": 6760,
                "cost": 0.0083, "lead_calls": 2, "messages": 4.3, "duplicated_tokens": 225}),
}

def illustrative_runs(multi_part: bool) -> tuple:
    """Stand-in runs with the means above, the successes spread over the tasks."""
    n, single, team = ILLUSTRATIVE[multi_part]
    runs = lambda mean: [{**mean, "ok": i < round(mean["ok"] * n)} for i in range(n)]
    return runs(single), runs(team)

# ------------------------------------------------------------ 6. demo
def show(title: str, report: dict, verdict: dict) -> None:
    s, t, o = report["single"], report["team"], report["overhead"]
    pct = lambda d: f"{d['success']:.0%} ({d['success_ci'][0]:.0%}-{d['success_ci'][1]:.0%})"
    print(f"\n== {title} ({s['tasks']} tasks each)")
    print(f"{'':<14}{'success (95% CI)':<20}{'calls':>6}{'tokens':>8}{'mean s':>8}"
          f"{'p95 s':>7}{'$/task':>9}")
    for name, d in (("one agent", s), ("lead+workers", t)):
        print(f"{name:<14}{pct(d):<20}{d['calls']:>6.1f}"
              f"{d['input_tokens'] + d['output_tokens']:>8,.0f}{d['latency_s']:>8.1f}"
              f"{d['p95_s']:>7.1f}{d['cost_per_task']:>9.4f}")
    print(f"overhead: +{o['extra_calls']:.1f} calls ({o['lead_calls']:.0f} by the lead), "
          f"+{o['extra_input_tokens']:,.0f} input tokens ({o['duplicated_tokens']:,.0f} "
          f"duplicated), {o['messages']:.1f} messages, {o['sync_wait_s']:.2f} s waiting "
          f"for the slowest worker, {o['extra_latency_s']:+.1f} s mean latency, "
          f"cost x{o['cost_ratio']:.1f}")
    be = verdict["break_even_value"]
    print(f"success gain {o['success_gain']:+.1%}, extra cost ${o['extra_cost_per_task']:.4f}"
          f"/task" + (f", break-even value ${be:.2f} per success" if be else ""))
    print(f"verdict: {verdict['verdict']}: {verdict['reason']}")

if __name__ == "__main__":
    VALUE = 0.05             # what one right answer is worth to you, in dollars (assumed)
    scenarios = [("one-part questions", False, {}),
                 ("multi-part questions", True, {}),
                 ("multi-part questions, 3 s tools, p95 SLO 16 s", True,
                  {"tool_ms": 3000, "slo": 16}),
                 ("the same, one agent with parallel tool calls", True,
                  {"tool_ms": 3000, "slo": 16, "parallel": True})]
    for title, multi, opts in scenarios:
        try:
            single, team = simulated_runs(multi, tool_ms=opts.get("tool_ms", 250),
                                          parallel_tools=opts.get("parallel", False))
        except Exception as exc:                       # no simulator or no shop.db
            if opts:
                continue
            print(f"(simulator unavailable: {type(exc).__name__}; illustrative numbers)")
            single, team = illustrative_runs(multi)
        report = coordination_report(single, team)
        show(title, report, decide(report, VALUE, latency_slo_s=opts.get("slo")))

    print("\n== failure propagation, 97% per step")
    print(f"{'design':<44}{'every part right':>17}{'share of parts':>15}")
    for name, kw in [("one agent, one step", dict(n=1)),
                     ("pipeline of 3 agents", dict(n=3)),
                     ("lead + 3 workers, a crash stops the team",
                      dict(n=3, parallel=True, contained=False, lead_steps=2)),
                     ("lead + 3 workers, failures contained",
                      dict(n=3, parallel=True, lead_steps=2)),
                     ("lead + 3 workers, contained, 1 retry each",
                      dict(n=3, parallel=True, lead_steps=2, retries=1))]:
        f = failure_propagation(0.97, **kw)
        print(f"{name:<44}{f['p_task']:>17.1%}{f['share_of_parts']:>15.1%}")
