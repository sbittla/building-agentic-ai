"""Chapter 19: durable execution for agents. A job is a list of steps saved in SQLite.
Every finished step is a checkpoint, so a crashed job resumes where it stopped instead
of starting over: no repeated side effects, and no paying twice for a model call.

  * checkpoints   each step's status and result are saved before the next one starts
  * retries       failed steps retry with backoff, up to a limit
  * timeouts      every step has a time limit, and the job has a deadline
  * idempotency   side effects carry a key, so a repeated step never repeats them
  * escalation    a step that keeps failing waits for a person instead of guessing
  * compensation  completed steps are undone, newest first, when a job is abandoned
  * leases        a worker owns a job for a while; if it dies, another takes over

    ./course.sh python ch19_durable.py             run the onboarding demo
    ./course.sh python ch19_durable.py --crash 2   crash after 2 steps; run it again"""
import concurrent.futures as cf
import contextlib
import json
import os
import re
import sqlite3
import sys
import threading
import time
import uuid
from pathlib import Path

DB = Path("jobs.db")
MAX_ATTEMPTS = 3
BACKOFF = 1.0              # seconds before the first retry; doubles each time
STEP_TIMEOUT = 60          # seconds one step may take
LEASE = 120                # seconds a worker owns a job before another may take it

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, goal TEXT, status TEXT,
  deadline REAL, worker TEXT, lease_until REAL, note TEXT);
CREATE TABLE IF NOT EXISTS steps (job_id TEXT, idx INTEGER, action TEXT, args TEXT,
  status TEXT DEFAULT 'pending', result TEXT, error TEXT, attempts INTEGER DEFAULT 0,
  PRIMARY KEY (job_id, idx));
CREATE TABLE IF NOT EXISTS events (job_id TEXT, at REAL, what TEXT);
"""

@contextlib.contextmanager
def _db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        con.executescript(SCHEMA)
        yield con
        con.commit()
    finally:
        con.close()

def _log(con, job_id, what):
    con.execute("INSERT INTO events VALUES (?,?,?)", (job_id, time.time(), what))

# ------------------------------------------------------------ 1. actions
class Permanent(Exception):
    """An error that retrying can't fix (bad input, refused by policy)."""

class Crash(BaseException):
    """Simulates the process dying (the demo turns it into a real exit)."""

ACTIONS = {}    # name -> {"run": fn(args, key), "undo": fn or None, "effect": ...}

def action(name, undo=None, effect=None):
    """Register a step type. effect: None (reads only), "keyed" (a side effect the
    receiving system de-duplicates by key) or "unkeyed" (a side effect it can't)."""
    def register(fn):
        ACTIONS[name] = {"run": fn, "undo": undo, "effect": effect}
        return fn
    return register

@action("agent")
def run_agent_step(args, key):
    """A model-driven step. Its answer is checkpointed like any other result, so a
    resumed job never pays for the same model call twice."""
    from ch04_agent import run_agent
    answer, _, stats = run_agent(args["prompt"], [], lambda n, a: "ERROR: no tools",
                                 verbose=False, max_iterations=args.get("max_steps", 4),
                                 model=args.get("model"))
    if stats["stop_reason"] not in ("end_turn", "stop_sequence"):
        raise RuntimeError(f"agent step didn't finish: {answer[:200]}")
    return answer

# ------------------------------------------------------------ 2. jobs
def create_job(goal: str, steps: list[dict], deadline_s: float = 3600) -> str:
    """steps: [{"action": name, "args": {...}}]. "$1" in an argument means
    the result of step 1."""
    job_id = uuid.uuid4().hex[:8]
    with _db() as con:
        con.execute("INSERT INTO jobs VALUES (?,?,?,?,?,?,?)", (job_id, goal, "queued",
                    time.time() + deadline_s, None, None, None))
        con.executemany("INSERT INTO steps (job_id, idx, action, args) "
                        "VALUES (?,?,?,?)",
                        [(job_id, i, s["action"], json.dumps(s.get("args", {})))
                         for i, s in enumerate(steps, 1)])
        _log(con, job_id, f"created with {len(steps)} steps")
    return job_id

def claim(worker: str, job_id: str | None = None) -> str | None:
    """Take a queued job, or a running one whose worker's lease has run out."""
    now = time.time()
    with _db() as con:
        where = ("status IN ('queued','running') "
                 "AND (lease_until IS NULL OR lease_until < ?)")
        row = con.execute(f"SELECT id FROM jobs WHERE {where}"
                          + (" AND id=?" if job_id else "") + " LIMIT 1",
                          (now, job_id) if job_id else (now,)).fetchone()
        if not row:
            return None
        taken = con.execute("UPDATE jobs SET worker=?, lease_until=?, status='running' "
                            f"WHERE id=? AND {where}", (worker, now + LEASE, row["id"],
                                                        now)).rowcount
        if not taken:                      # another worker got there first
            return None
        _log(con, row["id"], f"claimed by {worker}")
    return row["id"]

# ------------------------------------------------------------ 3. running a step
def _resolve(args: dict, results: dict) -> dict:
    """Replace "$n" with the result of step n."""
    text = json.dumps(args)
    return json.loads(re.sub(r'"\$(\d+)"', lambda m: json.dumps(results[int(m[1])]),
                             text))

def _attempt(fn, args, key):
    """Run one attempt with a time limit. A timed-out thread can't be killed in
    Python, so real side effects need their own timeouts too."""
    pool = cf.ThreadPoolExecutor(max_workers=1)
    try:
        return str(pool.submit(fn, args, key).result(timeout=STEP_TIMEOUT))
    except cf.TimeoutError:
        raise TimeoutError(f"step took longer than {STEP_TIMEOUT}s") from None
    finally:
        pool.shutdown(wait=False)

def _run_step(con, job_id, step, results):
    spec = ACTIONS[step["action"]]
    key = f"{job_id}:{step['idx']}"          # the same key on every attempt
    if step["status"] == "running" and spec["effect"] == "unkeyed":
        # We crashed during this step last time. Did the side effect happen? We can't
        # tell, and doing it twice could be worse than not at all: ask a person.
        return "escalate", "crashed mid-step; outcome unknown for an unkeyed effect"
    args = _resolve(json.loads(step["args"]), results)
    error = "no attempts left"
    for attempt in range(step["attempts"] + 1, MAX_ATTEMPTS + 1):
        con.execute("UPDATE steps SET status='running', attempts=? WHERE job_id=? "
                    "AND idx=?", (attempt, job_id, step["idx"]))
        con.commit()                          # "running" must survive a crash
        try:
            return "done", _attempt(spec["run"], args, key)
        except Permanent as exc:
            return "escalate", f"{step['action']}: {exc}"
        except Exception as exc:              # transient: wait, then try again
            error = f"{type(exc).__name__}: {exc}"
            _log(con, job_id, f"step {step['idx']} attempt {attempt} failed: {error}")
            con.commit()
            if attempt < MAX_ATTEMPTS:
                time.sleep(BACKOFF * 2 ** (attempt - 1))
    return "escalate", f"{step['action']} failed {MAX_ATTEMPTS} times: {error}"

# ------------------------------------------------------------ 4. the executor
def run_job(job_id: str, worker: str = "worker-1", crash_after: int | None = None):
    """Run a job's remaining steps in order, checkpointing each. Safe to call again
    after a crash: finished steps are skipped and their results reused."""
    finished = 0
    with _db() as con:
        job = con.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        steps = con.execute("SELECT * FROM steps WHERE job_id=? ORDER BY idx",
                            (job_id,)).fetchall()
        results = {s["idx"]: s["result"] for s in steps if s["status"] == "done"}
        for step in steps:
            if step["status"] in ("done", "skipped"):
                continue
            if time.time() > job["deadline"]:
                return _escalate(con, job_id, step["idx"], "job deadline passed")
            outcome, value = _run_step(con, job_id, step, results)
            if outcome == "escalate":
                return _escalate(con, job_id, step["idx"], value)
            results[step["idx"]] = value
            con.execute("UPDATE steps SET status='done', result=?, error=NULL "
                        "WHERE job_id=? AND idx=?", (value, job_id, step["idx"]))
            con.execute("UPDATE jobs SET lease_until=? WHERE id=?",
                        (time.time() + LEASE, job_id))            # still alive
            _log(con, job_id, f"step {step['idx']} {step['action']} done")
            con.commit()                                          # the checkpoint
            finished += 1
            if crash_after and finished >= crash_after:
                raise Crash(f"simulated crash after {finished} steps")
        con.execute("UPDATE jobs SET status='done', worker=NULL, lease_until=NULL "
                    "WHERE id=?", (job_id,))
        _log(con, job_id, "job done")
    return "done"

def _escalate(con, job_id, idx, reason):
    con.execute("UPDATE steps SET status='failed', error=? WHERE job_id=? AND idx=?",
                (reason, job_id, idx))
    con.execute("UPDATE jobs SET status='needs_human', note=?, lease_until=NULL "
                "WHERE id=?", (f"step {idx}: {reason}", job_id))
    _log(con, job_id, f"escalated: step {idx}: {reason}")
    return "needs_human"

# ------------------------------------------------------------ 5. people and undo
def resolve(job_id: str, decision: str, result: str = "") -> str:
    """A person's answer to an escalation: retry, skip (with a result), or abandon."""
    with _db() as con:
        failed = con.execute("SELECT idx FROM steps WHERE job_id=? AND status='failed'",
                             (job_id,)).fetchone()
        if decision == "abandon":
            return compensate(job_id)
        status = "skipped" if decision == "skip" else "pending"
        con.execute("UPDATE steps SET status=?, attempts=0, result=? WHERE job_id=? "
                    "AND idx=?", (status, result or None, job_id, failed["idx"]))
        con.execute("UPDATE jobs SET status='queued', note=NULL WHERE id=?", (job_id,))
        _log(con, job_id, f"human decision on step {failed['idx']}: {decision}")
    return "queued"

def compensate(job_id: str) -> str:
    """Undo finished steps, newest first (the saga pattern). Steps that can't be
    undone, like a sent email, are listed so a person can follow up."""
    with _db() as con:
        done = con.execute("SELECT * FROM steps WHERE job_id=? AND status='done' "
                           "ORDER BY idx DESC", (job_id,)).fetchall()
        manual = []
        for s in done:
            undo = ACTIONS[s["action"]]["undo"]
            if undo is None:
                if ACTIONS[s["action"]]["effect"]:
                    manual.append(f"step {s['idx']} {s['action']}")
                continue
            undo(json.loads(s["args"]), s["result"], f"{job_id}:{s['idx']}:undo")
            con.execute("UPDATE steps SET status='undone' WHERE job_id=? AND idx=?",
                        (job_id, s["idx"]))
        note = "can't undo: " + ", ".join(manual) if manual else None
        con.execute("UPDATE jobs SET status='compensated', note=? WHERE id=?",
                    (note, job_id))
        _log(con, job_id, "compensated" + (f"; {note}" if note else ""))
    return "compensated"

def report(job_id: str) -> str:
    with _db() as con:
        job = con.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        rows = [f"Job {job_id}: {job['status']}" + (f" ({job['note']})"
                                                     if job["note"] else "")]
        for s in con.execute("SELECT * FROM steps WHERE job_id=? ORDER BY idx",
                             (job_id,)):
            detail = (s["result"] or s["error"] or "")[:50]
            rows.append(f"  {s['idx']}. {s['action']:<16} {s['status']:<8} "
                        f"tries={s['attempts']} {detail}")
    return "\n".join(rows)

# ------------------------------------------------------------ 6. demo services
# Stand-ins for a CRM, a mail service and a payment provider. Like real ones (Stripe,
# for example), they accept an idempotency key and ignore a request they've seen.
SERVICES = Path("services.json")
FAILS = {"charge": int(os.environ.get("FAIL_CHARGE", "1"))}   # transient failures

def _svc():
    return json.loads(SERVICES.read_text()) if SERVICES.exists() else {}

_lock = threading.Lock()                # one "service" shared by several worker threads

def _call(kind, key, value):
    with _lock:
        return _record(kind, key, value)

def _record(kind, key, value):
    data = _svc()
    seen = data.setdefault(kind, {})
    if key not in seen:                                   # de-duplicate by key
        seen[key] = value
        SERVICES.write_text(json.dumps(data, indent=1))
    return seen[key]

def _delete_account(args, result, key):
    _call("deleted_accounts", key, args["email"])

def _refund(args, result, key):
    _call("refunds", key, args["amount"])

@action("create_account", undo=_delete_account, effect="keyed")
def create_account(args, key):
    return f"account {_call('accounts', key, args['email'])} created"

@action("send_email", effect="keyed")                     # an email can't be unsent
def send_email(args, key):
    _call("emails", key, {"to": args["to"], "body": args["body"]})
    return f"email sent to {args['to']}"

@action("charge", undo=_refund, effect="keyed")
def charge(args, key):
    if FAILS["charge"] > 0:
        FAILS["charge"] -= 1
        raise ConnectionError("payment provider timed out")
    if args["amount"] > 500:
        raise Permanent("amount over the $500 limit for automatic charges")
    return f"charged ${_call('charges', key, args['amount'])}"

ONBOARDING = [
    {"action": "create_account", "args": {"email": "ana@example.com"}},
    {"action": "agent", "args": {"prompt": "Write a two-sentence welcome message for "
                                           "a new Pro plan customer. Text only."}},
    {"action": "send_email", "args": {"to": "ana@example.com", "body": "$2"}},
    {"action": "charge", "args": {"email": "ana@example.com", "amount": 49}},
]

if __name__ == "__main__":
    args = sys.argv[1:]
    crash = int(args[args.index("--crash") + 1]) if "--crash" in args else None
    job = claim("worker-1")                  # resume an unfinished job, if any
    if job is None:
        job = claim("worker-1", create_job("Onboard ana@example.com", ONBOARDING))
    try:
        print("Result:", run_job(job, crash_after=crash))
    except Crash as exc:
        print(f"{exc}. Run the same command again (without --crash) to resume.")
        with _db() as con:                       # a real crash never releases its lease
            con.execute("UPDATE jobs SET lease_until=0 WHERE id=?", (job,))
        print(report(job))
        os._exit(1)
    print(report(job))
    print("Services:", json.dumps(_svc(), indent=1)[:600])
