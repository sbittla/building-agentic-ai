"""Chapter 29: performance engineering for agents. A latency model and a cost model
you can compute from a trace, and an experiment that sweeps concurrency to find the
knee: the point where more requests in flight stop buying throughput and start
buying queueing.

  * latency_model   total = model + tool + retrieval + orchestration
                            + queueing + serialization
  * cost_per_task   model + tool + retrieval + infrastructure + retry + human review
  * experiment      run an agent at several concurrency levels and measure each
  * simulated_agent an offline agent with a rate-limited model and a prompt cache
  * real_agent      the Chapter 8 SQL analyst, timed the same way (exercise 29.6)

    ./course.sh python ch29_perf.py        an offline sweep: 1, 2, 4, 8, 16 in flight"""
import itertools
import json
import random
import statistics
import threading
import time
from contextlib import contextmanager

from ch20_router import PRICES
from ch29_costs import CACHE_READ, CACHE_WRITE
from ch29_loadtest import pct

# ------------------------------------------------------------ 1. the latency model
RETRIEVAL_WORDS = ("search", "query", "retrieve", "lookup", "fetch")
# Encoding the request, decoding the reply and copying history, per step, OUTSIDE the
# model and tool spans. Measure yours with measure_serialization(); a few ms is usual.
SERIALIZE_MS = 2.0

def is_retrieval(tool_name: str) -> bool:
    """Tools that fetch data (search, SQL query, vector lookup) are retrieval: they
    scale with the data, not with the model, so they get their own term."""
    return any(w in tool_name.lower() for w in RETRIEVAL_WORDS)

def _from_spans(spans: list[dict]) -> dict:
    """Components from one trace's spans (Chapter 28's format). Assumes the model,
    tool and queue spans are children of invoke_agent and run one after another."""
    c = {"model_ms": 0.0, "tool_ms": 0.0, "retrieval_ms": 0.0, "queue_ms": 0.0,
         "steps": 0}
    for s in spans:
        name = s["name"]
        if name == "invoke_agent":
            c["total_ms"] = s["ms"]
        elif name.startswith("chat "):
            c["model_ms"] += s["ms"]
            c["steps"] += 1
        elif name.startswith("execute_tool "):
            tool = s["attributes"].get("gen_ai.tool.name", name.split(" ", 1)[1])
            c["retrieval_ms" if is_retrieval(tool) else "tool_ms"] += s["ms"]
        elif name.startswith("queue"):             # e.g. a gateway's wait_for_slot
            c["queue_ms"] += s["ms"]
        elif name.startswith("serialize"):
            c["serialize_ms"] = c.get("serialize_ms", 0.0) + s["ms"]
    c.setdefault("total_ms", sum(s["ms"] for s in spans))
    return c

def latency_model(spans_or_components, serialize_ms_per_step: float = SERIALIZE_MS):
    """Where one run's time went, in ms. Every term is measured except two:
    serialization (traced if there are serialize spans, else steps x a measured
    constant) and orchestration, the remainder: your own loop, guards, logging and
    anything nobody traced. A negative remainder means spans overlapped (parallel
    tool calls): the sequential model doesn't hold, so read the trace instead.
    Model spans timed at the client already include network transfer."""
    c = (_from_spans(spans_or_components) if isinstance(spans_or_components, list)
         else spans_or_components)
    total = c.get("total_ms", c.get("ms", 0.0))
    parts = {"model": c.get("model_ms", 0.0), "tool": c.get("tool_ms", 0.0),
             "retrieval": c.get("retrieval_ms", 0.0),
             "queueing": c.get("queue_ms", 0.0),
             "serialization": c.get("serialize_ms",
                                    serialize_ms_per_step * c.get("steps", 0))}
    parts = {k: round(v, 1) for k, v in parts.items()}
    parts["orchestration"] = round(total - sum(parts.values()), 1)
    return {**parts, "total": round(total, 1)}

SHORT = {"model": "model", "tool": "tool", "retrieval": "retr",
         "orchestration": "orch", "queueing": "queue", "serialization": "serial"}

def format_latency(lm: dict) -> str:
    """One line: the terms in ms, then the total they add up to."""
    return (" + ".join(f"{s} {lm[k]:,.0f}" for k, s in SHORT.items())
            + f" = {lm['total']:,.0f} ms")

def measure_serialization(messages: list, repeat: int = 20) -> float:
    """ms to encode and decode a conversation once, as a stand-in for per-step
    serialization when it isn't traced. Run it on a real conversation."""
    t0 = time.perf_counter()
    for _ in range(repeat):
        json.loads(json.dumps(messages, default=str))
    return (time.perf_counter() - t0) * 1000 / repeat

# ------------------------------------------------------------ 2. the cost model
def cost_per_task(*, input_tokens=0, output_tokens=0, cached_tokens=0,
                  cache_write_tokens=0, model="claude-sonnet-5", model_calls=1,
                  tool_calls=0, tool_price=0.0, retrieval_calls=0, retrieval_price=0.0,
                  retries=0, infra_per_hour=0.0, tasks_per_hour=None,
                  review_share=0.0, review_minutes=0.0,
                  reviewer_per_hour=0.0) -> dict:
    """Dollars for one task, by component.
    input_tokens counts ALL input, cached or not; cached_tokens were read from the
    cache (10% of the price) and cache_write_tokens written to it (125%).
    retries: model calls thrown away (timeouts), each costing an average call.
    infra: a server's $/hour spread over the tasks it finishes in that hour, so
    it falls as throughput rises. review: the share of tasks a person checks,
    times their minutes, times their hourly rate."""
    price_in, price_out = PRICES.get(model, (0.0, 0.0))
    fresh = input_tokens - cached_tokens - cache_write_tokens
    model_cost = (fresh * price_in + cached_tokens * price_in * CACHE_READ
                  + cache_write_tokens * price_in * CACHE_WRITE
                  + output_tokens * price_out) / 1e6
    c = {"model": model_cost,
         "tool": tool_calls * tool_price,
         "retrieval": retrieval_calls * retrieval_price,
         "infra": infra_per_hour / tasks_per_hour if tasks_per_hour else 0.0,
         "retry": retries * model_cost / max(model_calls, 1),
         "review": review_share * review_minutes / 60 * reviewer_per_hour}
    c = {k: round(v, 6) for k, v in c.items()}
    return {**c, "total": round(sum(c.values()), 6)}

# ------------------------------------------------------------ 3. the shared backend
class QueueTimeout(Exception):
    """Waited too long for a model slot: what a gateway turns into a 429."""

class Backend:
    """What the concurrent tasks of one experiment level share: the model's
    concurrency slots (a provider limit, or your gateway's), the simulator's prompt
    cache, and a clock scale so an offline sweep runs in seconds (0.01 = 100x fast).
    Every time is reported in unscaled ms, as if it had run at full length. Timer
    overshoot is scaled up too, so offline, orchestration reads a little high."""
    def __init__(self, slots: int | None = None, scale: float = 1.0):
        self.sem = threading.BoundedSemaphore(slots) if slots else None
        self.scale, self.cache, self.lock = scale, set(), threading.Lock()

    def ms_since(self, t0: float) -> float:
        return (time.perf_counter() - t0) * 1000 / self.scale

    def sleep(self, ms: float):
        time.sleep(ms * self.scale / 1000)

    @contextmanager
    def slot(self, timeout_ms: float | None = None):
        """Hold one model slot; yields the ms spent waiting for it (queueing)."""
        t0 = time.perf_counter()
        wait = None if timeout_ms is None else max(0.0, timeout_ms) * self.scale / 1000
        if self.sem and not self.sem.acquire(timeout=wait):
            raise QueueTimeout(f"no model slot within {timeout_ms:.0f} ms")
        try:
            yield self.ms_since(t0)
        finally:
            if self.sem:
                self.sem.release()

# ------------------------------------------------------------ 4. a simulated agent
SEED = 29
SIM = {"prefix": 3_000, "question": 60,          # tokens: system + tools, question
       "ttft_ms": 500, "ms_per_token": 10,       # time to first token, decode speed
       "cache_ttft_saving": 0.5,                 # a fully cached prompt halves TTFT
       "timeout_rate": 0.03, "timeout_ms": 4_000,
       "queue_deadline_ms": 10_000,              # give up waiting for slots after this
       "orchestration_ms": 15,                   # your own code, per step
       "tool_price": 0.0, "retrieval_price": 0.002,
       "review_share": 0.005, "review_minutes": 3, "reviewer_per_hour": 60}

def _cached_tokens(backend, task, step, prefix, last_prompt):
    """Prompt cache: a prefix hits once some earlier call has finished writing it.
    Step 0 can reuse the shared system prefix; later steps reuse the whole prompt
    of the task's previous call (history only grows, so it is a prefix)."""
    if step > 0 and (task, step - 1) in backend.cache:
        return last_prompt
    return prefix if "system" in backend.cache else 0

def _model_call(r, backend, rng, prompt, cached, out, sim):
    """One model call through a slot. A timeout holds the slot for timeout_ms and
    is retried; a task that has queued past its deadline gives up."""
    while True:
        remaining = sim["queue_deadline_ms"] - r["queue_ms"]
        try:
            with backend.slot(remaining) as waited:
                r["queue_ms"] += waited
                timed_out = rng.random() < sim["timeout_rate"]
                ttft = rng.lognormvariate(0, 0.3) * sim["ttft_ms"]
                ttft *= 1 - sim["cache_ttft_saving"] * cached / prompt
                ms = (sim["timeout_ms"] if timed_out
                      else ttft + out * sim["ms_per_token"] * rng.uniform(0.8, 1.2))
                backend.sleep(ms)
        except QueueTimeout:
            r["queue_ms"] = sim["queue_deadline_ms"]
            raise
        r["model_ms"] += ms
        if not timed_out:
            return
        r["retries"] += 1

def _tool_call(r, backend, rng):
    """60% retrieval (a search: slower, data-sized), 40% a quick local tool.
    Tools don't need a model slot, so they never queue here."""
    retrieval = rng.random() < 0.6
    ms = rng.lognormvariate(0, 0.5) * (150 if retrieval else 40)
    backend.sleep(ms)
    r["retrieval_ms" if retrieval else "tool_ms"] += ms
    r["retrieval_calls" if retrieval else "tool_calls"] += 1
    return rng.randint(300, 900)                  # tokens the result adds to history

def simulated_agent(question: str, backend: Backend, task: int = 0,
                    seed: int = SEED, sim: dict = SIM) -> dict:
    """An offline agent: 2-4 model calls with a tool call between each. Task i draws
    the same random numbers at every concurrency level (common random numbers), so
    differences between levels come from concurrency, not luck."""
    rng = random.Random(seed * 1_000_003 + task)
    r = {"ok": True, "steps": 0, "tokens_in": 0, "tokens_out": 0, "cached": 0,
         "written": 0, "model_ms": 0.0, "tool_ms": 0.0, "retrieval_ms": 0.0,
         "queue_ms": 0.0, "retries": 0, "tool_calls": 0, "retrieval_calls": 0}
    calls, history, prompt = rng.randint(2, 4), sim["question"], 0
    try:
        for step in range(calls):
            backend.sleep(sim["orchestration_ms"] + SERIALIZE_MS)
            last_prompt, prompt = prompt, sim["prefix"] + history
            out = rng.randint(60, 240)
            cached = _cached_tokens(backend, task, step, sim["prefix"], last_prompt)
            _model_call(r, backend, rng, prompt, cached, out, sim)
            with backend.lock:                    # the call wrote its prefix
                backend.cache.update({"system", (task, step)})
            r["steps"] += 1
            r["tokens_in"] += prompt
            r["tokens_out"] += out
            r["cached"] += cached
            r["written"] += prompt - cached
            history += out
            if step < calls - 1:
                history += _tool_call(r, backend, rng)
    except QueueTimeout:
        r["ok"] = False
    r["cost"] = cost_per_task(
        input_tokens=r["tokens_in"], output_tokens=r["tokens_out"],
        cached_tokens=r["cached"], cache_write_tokens=r["written"],
        model_calls=r["steps"], tool_calls=r["tool_calls"],
        tool_price=sim["tool_price"], retrieval_calls=r["retrieval_calls"],
        retrieval_price=sim["retrieval_price"], retries=r["retries"],
        review_share=sim["review_share"], review_minutes=sim["review_minutes"],
        reviewer_per_hour=sim["reviewer_per_hour"])["total"]
    return r

# ------------------------------------------------------------ 5. the experiment
def run_level(agent, questions, workers, n=None, seconds=None, model_slots=None,
              scale=1.0):
    """`workers` threads, each taking the next task as soon as its last one ends,
    until n tasks have started or `seconds` (unscaled) have passed."""
    backend, counter, results = Backend(model_slots, scale), itertools.count(), []
    start = time.perf_counter()

    def finished(i):
        return ((n is not None and i >= n)
                or (seconds is not None and backend.ms_since(start) > seconds * 1e3))

    def worker():
        while True:
            with backend.lock:                    # each task index is taken once
                i = next(counter)
            if finished(i):
                return
            t0 = time.perf_counter()
            try:
                r = agent(questions[i % len(questions)], backend, i)
            except Exception as exc:              # a crash is a failed task, not a stop
                r = {"ok": False, "error": type(exc).__name__}
            r["ms"] = backend.ms_since(t0)
            results.append(r)

    threads = [threading.Thread(target=worker) for _ in range(workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results, backend.ms_since(start) / 1000

def summarize_level(workers, results, wall_s, infra_per_hour=0.0) -> dict:
    """One row: what this concurrency level bought, and what it cost."""
    def mean(key):
        return statistics.mean(r.get(key, 0) for r in results) if results else 0.0
    lat = [r["ms"] / 1000 for r in results]
    ok = sum(r["ok"] for r in results)
    tokens_in = sum(r.get("tokens_in", 0) for r in results)
    throughput = len(results) / wall_s if wall_s else 0.0
    goodput = ok / wall_s if wall_s else 0.0      # tasks that succeeded, per second
    infra = infra_per_hour / (throughput * 3600) if throughput else 0.0
    cost = mean("cost") + infra                   # infra per task falls as tput rises
    return {"concurrency": workers, "tasks": len(results),
            "throughput": throughput, "goodput": goodput,
            "p50_s": pct(lat, 50), "p95_s": pct(lat, 95), "p99_s": pct(lat, 99),
            "tokens": mean("tokens_in") + mean("tokens_out"),
            "model_ms": mean("model_ms"), "tool_ms": mean("tool_ms"),
            "retrieval_ms": mean("retrieval_ms"), "queue_ms": mean("queue_ms"),
            "cache_hit": (sum(r.get("cached", 0) for r in results) / tokens_in
                          if tokens_in else 0.0),
            "steps": mean("steps"), "cost": cost,
            "cost_per_success": cost * len(results) / ok if ok else None,
            "success": ok / len(results) if results else 0.0,
            "results": results}

def experiment(agent, questions, concurrency_levels=(1, 2, 4, 8, 16), n=None,
               seconds=None, model_slots=None, scale=1.0, infra_per_hour=0.0):
    """Run agent(question, backend, task) -> result dict at each concurrency level,
    with a fresh Backend (slots and cache) per level. Returns one row per level.

    A fixed number of workers (closed loop), not open-loop arrivals: concurrency is
    the knob we turn, and Little's law (throughput = in flight / latency) makes the
    sweep the throughput curve whose knee we want. Queueing isn't hidden: the wait
    for a model slot happens inside each task and is measured. To ask what users
    feel at a given ARRIVAL rate, use ch29_loadtest.open_loop.

    n tasks per level (default: one per question), or run for `seconds`. Use n of
    10x the concurrency or more: the last tasks run with fewer workers busy."""
    if n is None and seconds is None:
        n = len(questions)
    rows = []
    for workers in concurrency_levels:
        results, wall_s = run_level(agent, questions, workers, n, seconds,
                                    model_slots, scale)
        rows.append(summarize_level(workers, results, wall_s, infra_per_hour))
    return rows

# ------------------------------------------------------------ 6. reading the results
COLUMNS = [("N", "concurrency", 3, "d"), ("tput", "throughput", 5, ".2f"),
           ("good", "goodput", 5, ".2f"), ("p50", "p50_s", 5, ".1f"),
           ("p95", "p95_s", 5, ".1f"), ("p99", "p99_s", 5, ".1f"),
           ("tok", "tokens", 6, ".0f"), ("model", "model_ms", 5, ".0f"),
           ("tool", "tool_ms", 5, ".0f"), ("retr", "retrieval_ms", 5, ".0f"),
           ("queue", "queue_ms", 5, ".0f"), ("cache", "cache_hit", 5, ".0%"),
           ("steps", "steps", 5, ".1f"), ("$/ok", "cost_per_success", 6, ".4f"),
           ("ok", "success", 4, ".0%")]

def format_experiment(rows: list[dict]) -> str:
    """A fixed-width table, one line per concurrency level."""
    def cell(row, key, width, fmt):
        value = row.get(key)
        return f"{'-' if value is None else format(value, fmt):>{width}}"
    lines = [" ".join(f"{h:>{w}}" for h, _, w, _ in COLUMNS)]
    lines += [" ".join(cell(r, k, w, f) for _, k, w, f in COLUMNS) for r in rows]
    lines.append("tput, good: tasks/s, all and successful; p50/p95/p99 in s; "
                 "model to queue: ms/task")
    return "\n".join(lines)

def knee(rows: list[dict], share: float = 0.9) -> dict:
    """The lowest concurrency that reaches `share` of the best goodput. Beyond it,
    more requests in flight buy latency, not throughput. Goodput, not throughput:
    tasks that give up early finish fast and flatter the raw rate."""
    best = max(r["goodput"] for r in rows)
    return next(r for r in rows if r["goodput"] >= share * best)

def interpret(rows: list[dict]) -> str:
    k, last = knee(rows), rows[-1]
    return (f"Knee at {k['concurrency']} in flight: {k['goodput']:.2f} good tasks/s, "
            f"p95 {k['p95_s']:.1f} s; at {last['concurrency']}: "
            f"{last['goodput']:.2f}/s, p95 {last['p95_s']:.1f} s, "
            f"{last['success']:.0%} ok.")

# ------------------------------------------------------------ 7. a real agent, timed
_task = threading.local()                          # the current task's record

class _TimedMessages:
    def __init__(self, messages):
        self._messages = messages

    def __getattr__(self, name):                   # stream, count_tokens, ...
        return getattr(self._messages, name)

    def create(self, **kw):
        rec = getattr(_task, "rec", None)
        if rec is None:                            # not inside an experiment
            return self._messages.create(**kw)
        with rec["backend"].slot() as waited:
            t0 = time.perf_counter()
            response = self._messages.create(**kw)
        rec["model_ms"] += (time.perf_counter() - t0) * 1000
        rec["queue_ms"] += waited
        usage = response.usage
        rec["cached"] += getattr(usage, "cache_read_input_tokens", 0) or 0
        rec["written"] += getattr(usage, "cache_creation_input_tokens", 0) or 0
        return response

class TimedClient:
    """Wraps the model client once, for all threads. Each call waits for a slot on
    the current task's backend and adds its time and cache tokens to that task.
    Outside an experiment it just passes calls through."""
    def __init__(self, client):
        self.client = client
        self.messages = _TimedMessages(client.messages)

def _timed_tools(run_tool, rec):
    def run(name, args):
        t0 = time.perf_counter()
        try:
            return run_tool(name, args)
        finally:
            key = "retrieval" if is_retrieval(name) else "tool"
            rec[f"{key}_ms"] += (time.perf_counter() - t0) * 1000
            rec[f"{key}_calls"] += 1
    return run

def real_agent(question: str, backend: Backend | None = None, task: int = 0) -> dict:
    """The Chapter 8 SQL analyst through run_agent, with model and tool time split
    out, so experiment() can sweep a real model (exercise 29.6). Costs money."""
    import ch04_agent
    import ch08_sql_tools as sql
    if not isinstance(ch04_agent.get_client(), TimedClient):
        ch04_agent._client = TimedClient(ch04_agent.get_client())
    rec = {"backend": backend or Backend(), "model_ms": 0.0, "queue_ms": 0.0,
           "tool_ms": 0.0, "retrieval_ms": 0.0, "tool_calls": 0,
           "retrieval_calls": 0, "cached": 0, "written": 0}
    _task.rec = rec
    try:
        answer, _, stats = ch04_agent.run_agent(
            question, sql.TOOLS, _timed_tools(sql.run_tool, rec), system=sql.SYSTEM,
            verbose=False)
    finally:
        _task.rec = None
    del rec["backend"]
    # usage.input_tokens counts only uncached input; the cache reads and writes
    # are reported separately, so add them back for the total
    tokens_in = stats["input_tokens"] + rec["cached"] + rec["written"]
    rec.update(ok=stats["stop_reason"] in ("end_turn", "stop_sequence"),
               steps=stats["steps"], tokens_in=tokens_in,
               tokens_out=stats["output_tokens"], retries=0, answer=answer)
    rec["cost"] = cost_per_task(
        input_tokens=tokens_in, output_tokens=stats["output_tokens"],
        cached_tokens=rec["cached"], cache_write_tokens=rec["written"],
        model=stats.get("model", ch04_agent.MODEL), model_calls=stats["steps"])["total"]
    return rec

if __name__ == "__main__":
    questions = [f"question {i}" for i in range(8)]
    rows = experiment(simulated_agent, questions, (1, 2, 4, 8, 16), n=48,
                      model_slots=4, scale=0.01, infra_per_hour=2.0)
    print("Simulated agent, 4 model slots, 48 tasks per level, run 100x faster "
          "than real time\n")
    print(format_experiment(rows))
    at8 = sorted(rows[3]["results"], key=lambda r: r["ms"])
    median = at8[len(at8) // 2]                   # a typical task past the knee
    print("\nMedian task at concurrency 8, in ms:\n ",
          format_latency(latency_model({**median, "total_ms": median["ms"]})))
    print(interpret(rows))
