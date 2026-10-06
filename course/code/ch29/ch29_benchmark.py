"""Chapter 29: a reproducible benchmark for architecture decisions.

Section 29.5's sweep asks how one agent behaves under load. This benchmark asks the
questions you face before that: which design, which execution strategy, which model,
how much context. Every run answers the same questions with known answers (the
Chapter 27 SQL cases), and success means the answer is RIGHT, checked against the
database, not merely that the agent stopped.

    ./course.sh python ch29_benchmark.py                   simulator: free, exactly reproducible
    ./course.sh python ch29_benchmark.py --backend claude  real latency and cost (--budget caps it)
    ./course.sh python ch29_benchmark.py --backend local   qwen3.5:9b through the kit's adapter
    ./course.sh python ch29_benchmark.py --quick           one repetition, fewer questions

Experiments
  E1 architecture   a fixed workflow, one agent, a lead with parallel workers
  E2 tool execution the agent's tool calls run one after another, or at the same time
  E3 model, context a small and a large model, with a short and a long system prompt
  E4 load           1 to 16 tasks in flight, a mix of easy and multi-part questions,
                    with and without transient tool failures

Each run writes benchmarks/<backend>-<time>/: config.json (everything needed to rerun
it), raw.jsonl (one line per task), summary.json and summary.md.

The simulator is a stand-in for a model: its latency, error rates and token counts are
the assumptions in SIM_MODELS, stated so you can change them. It reproduces the
MECHANICS exactly (the same seed gives the same numbers on any machine); only a real
model tells you how good your model is. Run both, and trust each for what it measures.
"""
import argparse
import hashlib
import json
import os
import platform
import random
import re
import statistics
import subprocess
import sys
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
import heapq
from types import SimpleNamespace as NS

import ch08_sql_tools as sql
from ch27_eval import _query, contains_value, db_fingerprint, wilson
from ch29_loadtest import pct
from ch29_perf import Backend, QueueTimeout, cost_per_task

SEED = 29
SMALL, LARGE = "claude-haiku-4-5", "claude-sonnet-5"

# ------------------------------------------------------------------ 1. the questions
CASES_FILE = Path(__file__).with_name("eval_sql.jsonl")
# Multi-part questions: several independent lookups, so tools can run in parallel.
MULTI = [
    ("multi-counts", "How many orders, customers and products are there?",
     ["SELECT COUNT(*) FROM orders", "SELECT COUNT(*) FROM customers", "SELECT COUNT(*) FROM products"]),
    ("multi-status", "How many orders are pending, and how many are cancelled?",
     ["SELECT COUNT(*) FROM orders WHERE status = 'pending'",
      "SELECT COUNT(*) FROM orders WHERE status = 'cancelled'"]),
    ("multi-products", "Which product is the most expensive, and which is the cheapest?",
     ["SELECT name FROM products ORDER BY price DESC LIMIT 1",
      "SELECT name FROM products ORDER BY price ASC LIMIT 1"]),
    ("multi-cities", "How many cities do customers live in, and how many customers are in Berlin?",
     ["SELECT COUNT(DISTINCT city) FROM customers", "SELECT COUNT(*) FROM customers WHERE city = 'Berlin'"]),
    ("multi-joined", "How many customers joined in 2024, and how many furniture products are there?",
     ["SELECT COUNT(*) FROM customers WHERE joined LIKE '2024-%'",
      "SELECT COUNT(*) FROM products WHERE category = 'furniture'"]),
    ("multi-orders", "How many orders were placed in December 2025, and how many are pending?",
     ["SELECT COUNT(*) FROM orders WHERE order_date LIKE '2025-12-%'",
      "SELECT COUNT(*) FROM orders WHERE status = 'pending'"]),
]


def load_cases():
    """The Chapter 27 cases that have a known answer, plus the multi-part ones.
    A case is {id, question, sqls}: the answer must state the result of every sql."""
    single = []
    for line in CASES_FILE.read_text().splitlines():
        c = json.loads(line)
        if c.get("answer_sql"):
            single.append({"id": c["id"], "question": c["question"], "sqls": [c["answer_sql"]]})
    multi = [{"id": i, "question": q, "sqls": s} for i, q, s in MULTI]
    return single, multi


def expected(case):
    return [(_query(s) or [[None]])[0][0] for s in case["sqls"]]


def correct(case, answer):
    return all(v is not None and contains_value(answer, v) for v in expected(case))


# ------------------------------------------------------------------ 2. the simulator
# Assumptions, not measurements: change them to match what you measure on your model.
SIM_MODELS = {
    SMALL: {"ttft_ms": 300, "ms_per_out_token": 5, "ms_per_1k_in": 25, "p_syntax": 0.10, "p_wrong": 0.10},
    LARGE: {"ttft_ms": 650, "ms_per_out_token": 12, "ms_per_1k_in": 45, "p_syntax": 0.04, "p_wrong": 0.03},
}
QUESTIONS = {}            # question text -> the SQL that answers it (the simulator's "knowledge")


def _tokens(*parts):
    return max(1, sum(len(json.dumps(p, default=str)) for p in parts) // 4)


def _block_text(content):
    if isinstance(content, str):
        return content
    return " ".join(getattr(b, "text", "") or (b.get("content", "") if isinstance(b, dict) else "")
                    for b in content)


class SimClient:
    """Speaks just enough of the Messages API for this benchmark. Every call draws from
    its own random generator, keyed by the task, the question, the kind of call and how
    many such calls came before: threads can run in any order and the numbers don't change."""
    def __init__(self, seed_key, backend):
        self.seed_key, self.backend, self.messages = seed_key, backend, self
        self.lock, self.counts, self.parts = threading.Lock(), {}, {}

    def _rng(self, *key):
        with self.lock:
            n = self.counts[key] = self.counts.get(key, -1) + 1
        return random.Random(f"{SEED}:{self.seed_key}:{key}:{n}")

    @staticmethod
    def _sql(good, profile, rng):
        r = rng.random()
        if r < profile["p_syntax"]:
            return "SELEC" + good[6:]                         # the database will say why
        if r < profile["p_syntax"] + profile["p_wrong"]:       # plausible and wrong
            return ("SELECT COUNT(*) FROM order_items" if "COUNT" in good.upper()
                    else "SELECT name FROM products ORDER BY id LIMIT 1")
        return good

    def create(self, model, system="", messages=(), tools=None, max_tokens=1024, **kw):
        p = SIM_MODELS[model]
        messages = list(messages)
        question = next(_block_text(m["content"]) for m in messages if m["role"] == "user")
        kind = (system[:12], bool(tools))
        rng = self._rng(question, kind)
        content, out = self._decide(system, question, messages, tools, p, rng)
        tokens_in, tokens_out = _tokens(system, tools or [], messages), out
        ms = (rng.lognormvariate(0, 0.25) * p["ttft_ms"] + tokens_in / 1000 * p["ms_per_1k_in"]
              + tokens_out * p["ms_per_out_token"] * rng.uniform(0.8, 1.2))
        self.backend.sleep(ms, "model")
        stop = "tool_use" if any(b.type == "tool_use" for b in content) else "end_turn"
        return NS(content=content, stop_reason=stop, stop_details=None,
                  usage=NS(input_tokens=tokens_in, output_tokens=tokens_out))

    def _decide(self, system, question, messages, tools, p, rng):
        text = lambda t: NS(type="text", text=t)
        use = lambda name, inp: NS(type="tool_use", id=f"toolu_{rng.getrandbits(48):x}", name=name, input=inp)
        if system.startswith(WF_SQL):                         # workflow step 1: write the SQL
            sqls = QUESTIONS.get(question, ["SELECT 1"])
            return [text("\n\n".join(f"```sql\n{self._sql(q, p, rng)}\n```" for q in sqls))], 40 * len(sqls)
        if system.startswith(WF_REPAIR):                      # fix the query it was shown
            broken = re.findall(r"```sql\s*(.+?)```", _block_text(messages[1]["content"]), re.S)[0].strip()
            good = "SELECT" + broken[5:] if broken.startswith("SELEC ") else broken
            return [text(f"```sql\n{self._sql(good, p, rng)}\n```")], 40
        if system.startswith((WF_ANSWER, SYNTH)):             # one value per block of results
            blocks = question.split("RESULTS:\n", 1)[-1].split(SEP)
            values = [(b.splitlines()[1] if len(b.splitlines()) > 1 else b).strip() for b in blocks]
            return [text("Answer: " + "; ".join(values))], 20 + 10 * len(values)
        if tools and tools[0]["name"] == "make_plan":         # the lead plans subtasks
            subs = SUBQUESTIONS.get(question, [question])
            return [use("make_plan", {"subtasks": subs})], 30 + 15 * len(subs)
        # the agent: schema first, then one query per part; read errors, retry; then answer
        sqls = QUESTIONS.get(question, ["SELECT 1"])
        state = self.parts.setdefault(question, {"issued": {}, "result": {}, "tries": 0})
        for m in messages:                                    # results for the calls we made
            if m["role"] == "user" and not isinstance(m["content"], str):
                for c in m["content"]:
                    if isinstance(c, dict) and c.get("tool_use_id") in state["issued"]:
                        state["result"][state["issued"][c["tool_use_id"]]] = str(c["content"])
        if len(messages) == 1:
            return [use("get_schema", {})], 20
        todo = [i for i in range(len(sqls))
                if i not in state["result"] or state["result"][i].startswith("ERROR")]
        if todo and state["tries"] < 4:
            state["tries"] += 1
            calls = []
            for i in todo:
                b = use("run_query", {"sql": self._sql(sqls[i], p, rng)})
                state["issued"][b.id] = i
                calls.append(b)
            return calls, 40 * len(calls)
        values = []
        for i in range(len(sqls)):
            rows = state["result"].get(i, "ERROR").splitlines()
            values.append(rows[1] if len(rows) > 1 and not rows[0].startswith("ERROR") else "unknown")
        return [text("Answer: " + "; ".join(values))], 40 + 10 * len(values)


SUBQUESTIONS = {}         # multi-part question -> its parts, for the simulated lead's plan


# ------------------------------------------------------------------ 3. two clocks
class VirtualTime:
    """The simulator's clock. Sleeping advances it and nothing waits, so a run takes
    seconds and gives the same numbers on every machine. Calls made "at the same time"
    all start at the same moment and the clock moves to the latest finish."""
    def __init__(self):
        self.t, self.trace = 0.0, []

    def now(self):
        return self.t

    def ms_since(self, t0):
        return self.t - t0

    def sleep(self, ms, kind="other"):
        self.t += ms
        self.trace.append((kind, ms))

    @contextmanager
    def slot(self, timeout_ms=None):
        yield 0.0                       # queueing for model slots is replayed later (E4)

    def parallel(self, fn, items):
        start, ends, out, kinds = self.t, [], [], set()
        for item in items:
            self.t, mark = start, len(self.trace)
            out.append(fn(item))
            ends.append(self.t)
            kinds.update(k for k, _ in self.trace[mark:])
            del self.trace[mark:]
        self.t = max(ends, default=start)
        self.trace.append(("model" if "model" in kinds else "tool", self.t - start))
        return out


class RealTime(Backend):
    """A real clock, for real models: model slots (a provider limit), real waiting."""
    def now(self):
        return time.perf_counter()

    def sleep(self, ms, kind="other"):
        time.sleep(ms / 1000)

    def parallel(self, fn, items):
        items = list(items)
        with ThreadPoolExecutor(max_workers=max(1, len(items))) as pool:
            return list(pool.map(fn, items))


def replay(tasks, workers, slots, deadline_ms=10_000):
    """E4 in the simulator: `workers` tasks in flight (a closed loop), each a recorded
    timeline of model and tool segments, sharing `slots` model slots, first come first
    served. A task that waits longer than deadline_ms for a slot fails (a 429, in effect).
    An event simulation, not threads and sleeps: exact, and the same on every machine.
    tasks: [{"trace": [(kind, ms), ...], "result": {...}}]. Returns (results, makespan ms)."""
    events, seq = [], 0
    free, waiting = slots, deque()            # waiting: (worker, ticket)
    state, out, nxt = {}, [], 0

    def push(t, kind, w, ticket=None):
        nonlocal seq
        heapq.heappush(events, (t, seq, kind, w, ticket))
        seq += 1

    def begin(w, t):
        nonlocal nxt
        if nxt < len(tasks):
            state[w] = {"task": tasks[nxt], "seg": 0, "t0": t, "queue": 0.0, "models": 0,
                        "failed": False, "ticket": None, "since": None}
            nxt += 1
            push(t, "step", w)

    def grant(t):
        nonlocal free
        while free and waiting:
            w, ticket = waiting.popleft()
            st = state.get(w)
            if st is None or st["ticket"] != ticket:     # it timed out and moved on
                continue
            free -= 1
            st["queue"] += t - st["since"]
            st["ticket"] = None
            push(t + st["task"]["trace"][st["seg"]][1], "model_done", w)

    for w in range(workers):
        begin(w, 0.0)
    end = 0.0
    while events:
        t, _, kind, w, ticket = heapq.heappop(events)
        st = state.get(w)
        if st is None:                        # a stale timeout for a worker with no tasks left
            continue
        end = max(end, t)
        if kind == "model_done":
            free += 1
            st["seg"] += 1
            st["models"] += 1
            grant(t)
            push(t, "step", w)
        elif kind == "timeout":
            if st["ticket"] == ticket:        # still waiting: give up
                st.update(ticket=None, failed=True, seg=len(st["task"]["trace"]))
                st["queue"] += deadline_ms
                push(t, "step", w)
        else:                                 # "step": start the next segment
            trace = st["task"]["trace"]
            if st["seg"] >= len(trace):       # the task is over
                r = dict(st["task"]["result"])
                total = sum(1 for k, _ in trace if k == "model") or 1
                share = 1.0 if not st["failed"] else st["models"] / total
                r.update(ms=t - st["t0"], queue_ms=st["queue"], cost=r.get("cost", 0.0) * share,
                         ok=r["ok"] and not st["failed"],
                         error="queue timeout" if st["failed"] else r.get("error"))
                out.append(r)
                del state[w]
                begin(w, t)
                continue
            seg_kind, ms = trace[st["seg"]]
            if seg_kind != "model":
                st["seg"] += 1
                push(t + ms, "step", w)
            elif free and not waiting:
                free -= 1
                push(t + ms, "model_done", w)
            else:
                ticket = (w, seq)
                st.update(ticket=ticket, since=t)
                waiting.append((w, ticket))
                push(t + deadline_ms, "timeout", w, ticket)
    return out, end


# ------------------------------------------------------------------ 4. calling a model, timed
class Run:
    """Everything one task did: calls, tokens, time by kind, errors, money."""
    def __init__(self, model, backend):
        self.model, self.backend, self.lock = model, backend, threading.Lock()
        self.r = {"ok": False, "steps": 0, "tokens_in": 0, "tokens_out": 0, "cached": 0,
                  "model_ms": 0.0, "tool_ms": 0.0, "queue_ms": 0.0, "retries": 0,
                  "tool_calls": 0, "tool_errors": 0, "error": None}

    def call(self, client, model=None, **kw):
        model = model or self.model
        with self.backend.slot(10_000) as waited:            # the provider's concurrency limit
            t0 = self.backend.now()
            resp = client.messages.create(model=model, max_tokens=kw.pop("max_tokens", 2048), **kw)
            ms = self.backend.ms_since(t0)
        with self.lock:
            self.r["queue_ms"] += waited
            self.r["model_ms"] += ms
            self.r["steps"] += 1
            self.r["tokens_in"] += resp.usage.input_tokens
            self.r["tokens_out"] += resp.usage.output_tokens
            self.r["cost"] = self.r.get("cost", 0.0) + cost_per_task(
                input_tokens=resp.usage.input_tokens, output_tokens=resp.usage.output_tokens,
                model=model)["total"]
        return resp


def tool_runner(run, backend, seed_key, tool_ms, fail_rate):
    """The Chapter 8 tools as if the database were across a network: tool_ms of latency
    per call, and a share of calls that fail transiently (the task decides to retry).
    Each call's draws are keyed by the call itself, so parallel calls stay reproducible."""
    counts, lock = {}, threading.Lock()
    def run_tool(name, args):
        key = f"{name}:{json.dumps(args, sort_keys=True)}"
        with lock:
            n = counts[key] = counts.get(key, -1) + 1
        rng = random.Random(f"{SEED}:{seed_key}:tool:{key}:{n}")
        t0 = backend.now()
        backend.sleep(rng.lognormvariate(0, 0.3) * tool_ms, "tool")
        failed = rng.random() < fail_rate
        out = ("ERROR: the database timed out; try the same query again." if failed
               else sql.run_tool(name, args))
        with run.lock:
            run.r["tool_ms"] += backend.ms_since(t0)
            run.r["tool_calls"] += 1
            run.r["tool_errors"] += out.startswith("ERROR")
        return out
    return run_tool


# ------------------------------------------------------------------ 5. three designs
WF_SQL = "Write SQLite queries that answer the user's question."
WF_REPAIR = "The query failed. Write a corrected SQLite query."
WF_ANSWER = "Answer the user's question in one sentence from the query results."
PLAN = "Split the user's question into at most 3 independent sub-questions for data analysts."
SYNTH = "Combine the analysts' findings into one short answer to the user's question."
PLAN_TOOL = {"name": "make_plan", "description": "Record the sub-questions.",
             "input_schema": {"type": "object", "required": ["subtasks"],
                              "properties": {"subtasks": {"type": "array", "items": {"type": "string"},
                                                          "minItems": 1, "maxItems": 3}}}}


def workflow(case, client, run, run_tool, context=""):
    """Fixed steps, written by you: write SQL, run it (code retries a transient error),
    one repair if the database rejects it, then phrase the answer. Two or three calls."""
    schema = sql.get_schema()
    resp = run.call(client, system=f"{WF_SQL} One query per part, each in its own ```sql block.\n"
                    f"{context}\nSchema:\n{schema}", messages=[{"role": "user", "content": case["question"]}])
    queries = re.findall(r"```sql\s*(.+?)```", _block_text(resp.content), re.S)
    outputs = []
    for q in queries:
        out = run_tool("run_query", {"sql": q.strip()})
        for _ in range(2):                                   # transient: the code retries
            if "timed out" not in out:
                break
            run.r["retries"] += 1
            out = run_tool("run_query", {"sql": q.strip()})
        if out.startswith("ERROR"):                          # wrong SQL: one repair call
            fix = run.call(client, system=f"{WF_REPAIR}\nSchema:\n{schema}",
                           messages=[{"role": "user", "content": case["question"]},
                                     {"role": "assistant", "content": f"```sql\n{q}\n```"},
                                     {"role": "user", "content": out}])
            q2 = re.findall(r"```sql\s*(.+?)```", _block_text(fix.content), re.S)
            out = run_tool("run_query", {"sql": q2[0].strip()}) if q2 else out
        outputs.append(out)
    resp = run.call(client, system=WF_ANSWER,
                    messages=[{"role": "user", "content": f"{case['question']}\nRESULTS:\n" + SEP.join(outputs)}])
    return _block_text(resp.content)


def agent(case, client, run, run_tool, context="", parallel=False, max_steps=8):
    """The Chapter 8 analyst: the model chooses each step. parallel=True runs the tool
    calls of one turn at the same time instead of one after another."""
    messages = [{"role": "user", "content": case["question"]}]
    if True:
        for _ in range(max_steps):
            resp = run.call(client, system=sql.SYSTEM + context, tools=sql.TOOLS, messages=messages)
            messages.append({"role": "assistant", "content": resp.content})
            uses = [b for b in resp.content if b.type == "tool_use"]
            if resp.stop_reason != "tool_use" or not uses:
                return _block_text(resp.content)
            outs = (run.backend.parallel(lambda b: run_tool(b.name, b.input), uses) if parallel
                    else [run_tool(b.name, b.input) for b in uses])
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": b.id, "content": o, "is_error": o.startswith("ERROR")}
                for b, o in zip(uses, outs)]})
        run.r["error"] = "max_steps"
        return ""


def multi_agent(case, client, run, run_tool, context=""):
    """A lead plans sub-questions, one worker agent per sub-question runs in parallel,
    and the lead combines their findings: Chapter 11's orchestrator-worker."""
    resp = run.call(client, system=PLAN, tools=[PLAN_TOOL], tool_choice={"type": "tool", "name": "make_plan"},
                    messages=[{"role": "user", "content": case["question"]}])
    plan = next((b.input for b in resp.content if b.type == "tool_use"), {"subtasks": [case["question"]]})
    subtasks = plan.get("subtasks") or [case["question"]]
    findings = run.backend.parallel(lambda q: agent({"question": q}, client, run, run_tool, context), subtasks)
    resp = run.call(client, system=SYNTH, messages=[{"role": "user", "content":
                    f"{case['question']}\nRESULTS:\n" + SEP.join(f.removeprefix('Answer: ') for f in findings)}])
    return _block_text(resp.content)


DESIGNS = {"workflow": workflow, "agent": agent, "multi-agent": multi_agent}
SEP = "\n---\n"                # between blocks of results in a prompt
PAD_LINE = ("Column notes: orders.status is one of pending, shipped, delivered, cancelled; "
            "dates are ISO 8601 text; prices are in euros including VAT; ")


def long_context(tokens):
    """A data dictionary padded to about `tokens` tokens: the cost of a big system prompt."""
    return "\n" + PAD_LINE * max(1, tokens * 4 // len(PAD_LINE))


# ------------------------------------------------------------------ 6. one task
def task(case, design, *, backend, client_for, model, seed_key, context="", parallel=False,
         tool_ms=250, fail_rate=0.0):
    run = Run(model, backend)
    client = client_for(seed_key, backend)
    run_tool = tool_runner(run, backend, seed_key, tool_ms, fail_rate)
    t0 = backend.now()
    answer = ""
    try:
        fn = DESIGNS[design]
        answer = (fn(case, client, run, run_tool, context, parallel=parallel) if design == "agent"
                  else fn(case, client, run, run_tool, context))
    except QueueTimeout:
        run.r["error"] = "queue timeout"
    except Exception as exc:                                  # a crash is a failed task
        run.r["error"] = f"{type(exc).__name__}: {exc}"[:200]
    run.r.update(ok=bool(answer) and run.r["error"] is None and correct(case, answer),
                 answer=answer[:300], case=case["id"], ms=backend.ms_since(t0))
    run.r.setdefault("cost", 0.0)
    return run.r


# ------------------------------------------------------------------ 7. the experiments
def summarize(rows, label):
    if not rows:
        return {"config": label, "tasks": 0}
    ok = sum(r["ok"] for r in rows)
    lat = [r["ms"] / 1000 for r in rows]
    cost = sum(r.get("cost", 0.0) for r in rows)
    lo, hi = wilson(ok, len(rows))
    return {"config": label, "tasks": len(rows), "success": ok / len(rows), "success_ci": [lo, hi],
            "errors": sum(r.get("error") is not None for r in rows) / len(rows),
            "p50_s": pct(lat, 50), "p95_s": pct(lat, 95), "p99_s": pct(lat, 99),
            "model_calls": statistics.mean(r.get("steps", 0) for r in rows),
            "tokens": statistics.mean(r.get("tokens_in", 0) + r.get("tokens_out", 0) for r in rows),
            "cost_per_task": cost / len(rows), "cost_per_success": cost / ok if ok else None}


def sequential(cases, reps, warmup, make_backend, **kw):
    """Every case `reps` times, one after another, after `warmup` discarded tasks."""
    for case in cases[:warmup]:
        task(case, backend=make_backend(), **{**kw, "seed_key": f"warmup:{kw['seed_key']}:{case['id']}"})
    return [task(case, backend=make_backend(), **{**kw, "seed_key": f"{kw['seed_key']}:{case['id']}:{rep}"})
            for rep in range(reps) for case in cases]


def closed_loop(fn, items, workers, n, backend):
    """Real backends: `workers` threads, each starting the next task when its last ends."""
    lock, counter, results = threading.Lock(), iter(range(n)), []
    def worker():
        while True:
            with lock:
                i = next(counter, None)
            if i is None:
                return
            results.append(fn(items[i % len(items)], backend, i))
    t0 = time.perf_counter()
    threads = [threading.Thread(target=worker) for _ in range(workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results, (time.perf_counter() - t0) * 1000


def run_all(args, client_for, virtual):
    single, multi = load_cases()
    if args.quick:
        single, multi = single[:8], multi[:3]
    for c in single + multi:
        QUESTIONS[c["question"]] = c["sqls"]
    for c in multi:                                          # the simulated lead splits by part
        parts = [f"{c['question']} (part {i + 1}: {q})" for i, q in enumerate(c["sqls"])]
        SUBQUESTIONS[c["question"]] = parts
        for part, q in zip(parts, c["sqls"]):
            QUESTIONS[part] = [q]
    shared = None if virtual else RealTime()
    make_backend = VirtualTime if virtual else (lambda: shared)
    raw, summary, spent = [], {}, [0.0]
    base = dict(client_for=client_for, model=args.model, tool_ms=args.tool_ms)

    def record(exp, label, rows):
        for r in rows:
            raw.append({"experiment": exp, "config": label, **r})
        spent[0] += sum(r.get("cost", 0.0) for r in rows)
        return summarize(rows, label)

    def budget_left():
        if virtual or spent[0] < args.budget:
            return True
        print(f"Budget of ${args.budget:.2f} reached (${spent[0]:.2f}); stopping.")
        return False

    exps = set(args.experiments.split(","))
    if "E1" in exps:
        summary["E1"] = []
        for design in DESIGNS:
            if budget_left():
                rows = sequential(single, args.reps, args.warmup, make_backend, design=design,
                                  seed_key="E1", **base)   # common random numbers: same dice
                summary["E1"].append(record("E1", design, rows))
    if "E2" in exps:
        summary["E2"] = []
        for mode in ("sequential", "parallel"):
            if budget_left():                                # the same seeds: a paired comparison
                rows = sequential(multi, args.reps, args.warmup, make_backend, design="agent",
                                  parallel=mode == "parallel", seed_key="E2", **base)
                summary["E2"].append(record("E2", f"tools {mode}", rows))
    if "E3" in exps:
        summary["E3"] = []
        for model in ([args.small, args.model] if args.backend != "local" else [args.model]):
            for ctx in ((0, args.long_context) if args.long_context else (0,)):
                if budget_left():
                    rows = sequential(single, args.reps, args.warmup, make_backend, design="agent",
                                      seed_key="E3", context=long_context(ctx) if ctx else "",
                                      **{**base, "model": model})
                    summary["E3"].append(record("E3", f"{model}, {'+' + format(ctx, ',') + ' tokens' if ctx else 'base'} context", rows))
    if "E4" in exps:
        summary["E4"] = []
        mix = single[: max(1, len(single) * 7 // 10)] + multi    # about 70% one-part, 30% multi-part
        n = len(mix) * (1 if args.quick else 3)
        for fail in (0.0, args.fail_rate):
            if virtual:                                         # each task's timeline, once
                timelines = []
                for i in range(n):
                    b = VirtualTime()
                    r = task(mix[i % len(mix)], "agent", backend=b, seed_key=f"E4:{i}", parallel=True,
                             fail_rate=fail, **base)
                    timelines.append({"trace": b.trace, "result": r})
            for level in args.concurrency:
                if not budget_left():
                    break
                if virtual:
                    results, wall_ms = replay(timelines, level, args.slots)
                else:
                    backend = RealTime(slots=args.slots)
                    fn = lambda case, b, i: task(case, "agent", backend=b, seed_key=f"E4:{i}", parallel=True,
                                                 fail_rate=fail, **base)
                    results, wall_ms = closed_loop(fn, mix, level, n, backend)
                row = record("E4", f"{level} in flight, {fail:.0%} tool failures", results)
                ok = sum(r["ok"] for r in results)
                row.update(concurrency=level, fail_rate=fail, throughput=len(results) / (wall_ms / 1000),
                           goodput=ok / (wall_ms / 1000),
                           queue_s=statistics.mean(r.get("queue_ms", 0) for r in results) / 1000)
                summary["E4"].append(row)
    return raw, summary, spent[0]


# ------------------------------------------------------------------ 8. provenance and the report
def environment(args):
    def git(*a):
        try:
            return subprocess.run(["git", *a], capture_output=True, text=True, check=True,
                                  cwd=Path(__file__).parent).stdout.strip()
        except Exception:
            return None
    prompts = {"agent": sql.SYSTEM, "workflow": [WF_SQL, WF_REPAIR, WF_ANSWER], "multi": [PLAN, SYNTH],
               "tools": sql.TOOLS}
    return {"backend": args.backend, "model": args.model, "small_model": args.small,
            "simulated_models": SIM_MODELS if args.backend == "sim" else None,
            "commit": os.environ.get("COURSE_COMMIT") or git("rev-parse", "--short=12", "HEAD"),
            "prompts_sha256": hashlib.sha256(json.dumps(prompts, sort_keys=True).encode()).hexdigest()[:16],
            "data_fingerprint": db_fingerprint()[:16], "python": platform.python_version(),
            "platform": platform.platform(), "cpus": os.cpu_count(), "seed": SEED, "reps": args.reps,
            "warmup_tasks_discarded": args.warmup, "tool_latency_ms": args.tool_ms,
            "tool_failure_rate_E4": args.fail_rate, "model_slots_E4": args.slots,
            "long_context_tokens_E3": args.long_context, "concurrency_E4": args.concurrency,
            "quick": args.quick, "started": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "command": " ".join(["python", Path(sys.argv[0]).name, *sys.argv[1:]])}


def fmt(x, kind):
    if x is None:
        return "—"
    return {"pct": f"{x:.0%}", "s": f"{x:.1f}", "usd": f"${x:.4f}", "n": f"{x:.1f}", "tok": f"{x:,.0f}"}[kind]


def markdown(env, summary, spent):
    lines = [f"# Benchmark: {env['backend']} backend", "",
             f"Model `{env['model']}` (small: `{env['small_model']}`), commit `{env['commit']}`, data "
             f"`{env['data_fingerprint']}`, prompts `{env['prompts_sha256']}`, seed {env['seed']}, "
             f"{env['reps']} repetitions after {env['warmup_tasks_discarded']} discarded warm-up tasks, "
             f"tool latency {env['tool_latency_ms']} ms, {env['platform']}, {env['cpus']} CPUs, "
             f"Python {env['python']}, {env['started']}. "
             + (f"Simulated cost at list prices: ${spent:.2f} (nothing was billed)." if env["backend"] == "sim"
                else f"Total spent: ${spent:.2f}."), "",
             f"Rerun: `{env['command']}`", ""]
    if env["backend"] == "sim":
        lines += ["Simulated model: these numbers follow from the assumptions in `SIM_MODELS` (latency, "
                  "error rates), so they show the mechanics of each design exactly, not how good a real "
                  "model is. Same seed, same numbers, on any machine.", ""]
    head = ("| Configuration | Tasks | Success (95% CI) | Errors | p50 s | p95 s | p99 s | Model calls | "
            "Tokens | $/task | $/success |")
    sep = "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    titles = {"E1": "E1. Architecture: workflow, one agent, a team",
              "E2": "E2. Tool execution: one after another, or at the same time",
              "E3": "E3. Model size and context length",
              "E4": "E4. Load: tasks in flight, workload mix and transient failures"}
    for exp, rows in summary.items():
        lines += [f"## {titles[exp]}", "", head if exp != "E4" else head + " Throughput /s | Goodput /s |",
                  sep if exp != "E4" else sep + " ---: | ---: |"]
        for r in rows:
            cells = [r["config"], str(r["tasks"]),
                     f"{fmt(r['success'], 'pct')} ({fmt(r['success_ci'][0], 'pct')}–{fmt(r['success_ci'][1], 'pct')})",
                     fmt(r["errors"], "pct"), fmt(r["p50_s"], "s"), fmt(r["p95_s"], "s"), fmt(r["p99_s"], "s"),
                     fmt(r["model_calls"], "n"), fmt(r["tokens"], "tok"), fmt(r["cost_per_task"], "usd"),
                     fmt(r["cost_per_success"], "usd")]
            if exp == "E4":
                cells += [f"{r['throughput']:.2f}", f"{r['goodput']:.2f}"]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backend", choices=["sim", "claude", "local"], default="sim")
    ap.add_argument("--model", default=None, help="large model (default: claude-sonnet-5, or LOCAL_MODEL)")
    ap.add_argument("--small", default=SMALL)
    ap.add_argument("--experiments", default="E1,E2,E3,E4")
    ap.add_argument("--reps", type=int, default=None, help="default: 5 simulated, 3 real")
    ap.add_argument("--warmup", type=int, default=1)
    ap.add_argument("--tool-ms", type=float, default=250)
    ap.add_argument("--fail-rate", type=float, default=0.10)
    ap.add_argument("--slots", type=int, default=4, help="model calls in flight (E4)")
    ap.add_argument("--concurrency", type=lambda s: [int(x) for x in s.split(",")], default=[1, 2, 4, 8, 16])
    ap.add_argument("--long-context", type=int, default=8000)
    ap.add_argument("--budget", type=float, default=10.0, help="stop real runs after this many dollars")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default="benchmarks")
    ap.add_argument("--quiet", action="store_true", help="don't print the report")
    args = ap.parse_args(argv)
    args.reps = args.reps or (1 if args.quick else 5 if args.backend == "sim" else 3)
    if args.backend == "sim":
        args.model = args.model or LARGE
        client_for, virtual = SimClient, True
    else:
        if args.backend == "local":
            os.environ["PROVIDER"] = "local"
        import ch04_agent
        args.model = args.model or (os.environ.get("LOCAL_MODEL", "qwen3.5:9b") if args.backend == "local"
                                    else ch04_agent.MODEL)
        shared = ch04_agent.get_client()
        client_for, virtual = (lambda seed_key, backend: shared), False
        args.slots = None if args.backend == "claude" else args.slots
    env = environment(args)
    folder = Path(args.out) / f"{args.backend}-{time.strftime('%Y%m%d-%H%M%S')}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "config.json").write_text(json.dumps(env, indent=1) + "\n")
    raw, summary, spent = run_all(args, client_for, virtual)
    with open(folder / "raw.jsonl", "w") as f:
        for r in raw:
            f.write(json.dumps(r, default=str) + "\n")
    (folder / "summary.json").write_text(json.dumps({"environment": env, "spent_usd": spent,
                                                     "summary": summary}, indent=1, default=str) + "\n")
    report = markdown(env, summary, spent)
    (folder / "summary.md").write_text(report + "\n")
    if not args.quiet:
        print("\n" + report + f"\nWrote {folder}/")
    return summary


if __name__ == "__main__":
    main()
