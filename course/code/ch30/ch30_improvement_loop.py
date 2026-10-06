"""Chapter 30: the agent improvement loop. One turn of the production learning loop,
with every gate decided by code and thresholds, not by opinion:

  * mine_failures   production traces + graded evals -> failures, classified with
                    Chapter 28's taxonomy
  * to_cases        failures -> new eval cases, deduplicated, labeled with their class
  * offline_eval    baseline vs candidate on the grown suite, with repeated trials
                    (the measurement interlude) and Chapter 27's regression gate
  * shadow          the candidate answers mirrored traffic; its answers are graded,
                    compared and never shown
  * canary          the candidate serves a small share of real traffic; its SLOs and
                    error-budget burn decide (Chapter 28)
  * improvement_turn  all of the above, ending in promote, reject or roll back, with
                    the evidence recorded

The agents here are fakes: each release answers the same question the same way every
time, so the demo is offline, free and repeatable.

    ./course.sh python ch30_improvement_loop.py"""
import hashlib
import json
import random
import re

from ch27_trajectory import gate
from ch28_agentops import summarize
from ch28_ops import AGENT_SLOS, ERR, build_spans, classify_detailed, measure_slos
from i_measure import compare, contains_expected, run_suite

# ------------------------------------------------------------ the gates, in one place
GATES = {
    "fixed_min": 0.9,          # offline: share of mined-case runs that must pass
    "max_broken": 0,           # offline: old cases that passed every trial and now fail
    "shadow_max_worse": 0.02,  # shadow: share of mirrored requests graded worse
    "canary_share": 0.10,      # canary: share of real traffic the candidate serves
    "canary_min_runs": 30,     # canary: fewer runs than this can't show an SLO is met
    "canary_max_burn": 1.0,    # canary: highest burn rate (1 = spending on pace)
}
CANARY_SLOS = [s for s in AGENT_SLOS if s["key"] in ("passed", "ms", "cost")]

# ------------------------------------------------------------ demo data and fake agents
POOL = [  # a question users ask, and the answer a reviewer accepts
    ("How many orders are there?", "1200"),
    ("How many customers do we have?", "300"),
    ("What is our best-selling product?", "desk lamp"),
    ("How many products are out of stock?", "14"),
    ("What was the average order value in March?", "38.5"),
    ("Which customer spent the most?", "ana lima"),
    ("How many orders were shipped late?", "57"),
    ("How many orders were cancelled?", "31"),
    ("What was revenue in March?", "41877"),
    ("Which region sold the most in March?", "north"),
]
LOOPS = object()      # a fake agent's "answer" when it retries a failing tool forever


def normalize(question: str) -> str:
    """'How many orders were CANCELLED ?' -> 'how many orders were cancelled'."""
    return " ".join(re.findall(r"[a-z0-9]+", question.lower()))


class FakeAgent:
    """One release of the agent: a version, a model and the questions it gets wrong.
    Every other question in POOL gets the right answer. `slow` scales its latency."""
    def __init__(self, version, wrong=None, model="claude-sonnet-5", slow=1.0):
        self.version, self.model, self.slow = version, model, slow
        self.wrong = {normalize(q): a for q, a in (wrong or {}).items()}
        self.right = {normalize(q): f"The answer is {a}." for q, a in POOL}

    def loops(self, question):
        return self.wrong.get(normalize(question)) is LOOPS

    def __call__(self, question):
        key = normalize(question)
        if self.loops(question):
            return "Sorry, I couldn't finish: the query kept failing."
        return self.wrong.get(key) or self.right.get(key, "I don't know.")


def traffic(n: int, seed: int = 0) -> list[dict]:
    """n requests, each with the answer a reviewer would accept (`expect`). Common
    questions come more often, and some arrive with different case and punctuation."""
    common = [{"question": q, "expect": a} for q, a in POOL[:7]] * 3
    rare = [{"question": q, "expect": a} for q, a in POOL[7:]]
    rare += [{"question": "how many orders were CANCELLED ?", "expect": "31"},
             {"question": "What was revenue in March", "expect": "41877"}]
    rng = random.Random(seed)
    return [{"id": f"req-{i}", **rng.choice(common + rare)} for i in range(n)]


def serve(agent, request: dict) -> dict:
    """Answer one request and record what production keeps: the trace (Chapter 28's
    span format), the run summary and the grade. The grade stands in for section 27.8's
    checks and calibrated judge; `expect` is the reviewer's label."""
    s, tid = agent.slow, f"{agent.version}:{request['id']}"
    answer = agent(request["question"])
    if agent.loops(request["question"]):
        steps = [("chat", 700 * s, 2500, 90)] + [
            ("tool", "run_query", 300 * s, {**ERR, "tool.args_hash": "a1f3"}),
            ("chat", 800 * s, 3000, 90)] * 4
        stop, results = "tool_use", []
    else:
        steps = [("chat", 900 * s, 2500, 100), ("tool", "run_query", 400 * s, {}),
                 ("chat", 1300 * s, 3100, 200)]
        stop, results = "end_turn", [f"[('{request['expect']}',)]"]
    spans = build_spans(tid, steps, stop, model=agent.model)
    return {"trace_id": tid, "question": request["question"], "version": agent.version,
            "spans": spans, "run": summarize(tid, spans),
            "eval": {"passed": contains_expected(answer, request), "answer": answer,
                     "tool_results": results, "expect": request["expect"]}}

# ------------------------------------------------------------ 1. mine production failures
def mine_failures(records: list[dict]) -> list[dict]:
    """Every graded production run that failed, with its taxonomy classes. A failure
    with no reviewer label can't become a case yet, so it's marked for review."""
    failures = []
    for r in records:
        ev = r["eval"]
        classes = classify_detailed(r["run"], r["spans"], ev)
        if ev.get("passed") is False or classes:
            failures.append({"trace_id": r["trace_id"], "question": r["question"],
                             "classes": classes or ["unclassified"],
                             "expect": ev.get("expect"),
                             "needs_label": not ev.get("expect")})
    return failures

# ------------------------------------------------------------ 2. failures become cases
def to_cases(failures: list[dict], suite: list[dict]) -> tuple[list[dict], dict]:
    """One new eval case per distinct question, labeled with its failure classes and
    the trace it came from. Questions already in the suite are dropped."""
    seen = {normalize(c["question"]) for c in suite}
    new, skipped = [], {"duplicate": 0, "needs_label": 0}
    for f in failures:
        key = normalize(f["question"])
        if f["needs_label"]:
            skipped["needs_label"] += 1
            continue
        if key in seen:
            skipped["duplicate"] += 1
            continue
        seen.add(key)
        short = hashlib.sha1(key.encode()).hexdigest()[:6]
        new.append({"id": f"{f['classes'][-1]}-{short}",
                    "question": f["question"], "expect": f["expect"],
                    "failure_classes": f["classes"], "source": f["trace_id"]})
    return new, skipped

# ------------------------------------------------------------ 3. offline evaluation
def offline_eval(baseline, candidate, suite, new_cases, trials=3, gates=GATES) -> dict:
    """Both versions on the grown suite, every case `trials` times. Pass when the
    regression gate doesn't block, no old case breaks and the mined cases are fixed."""
    cases = suite + new_cases
    b = run_suite(baseline, cases, trials)
    c = run_suite(candidate, cases, trials)
    g = gate([r["passed"] for r in b["results"]], [r["passed"] for r in c["results"]])
    always = {k["id"] for k in cases} - {r["id"] for r in b["results"] if not r["passed"]}
    broken = sorted(always & {r["id"] for r in c["results"] if not r["passed"]})
    mined = {k["id"] for k in new_cases}
    on_mined = [r["passed"] for r in c["results"] if r["id"] in mined]
    fixed = sum(on_mined) / len(on_mined) if on_mined else 1.0
    reasons = []
    if g["block"]:
        reasons.append(f"regression gate blocks (z={g['z']})")
    if len(broken) > gates["max_broken"]:
        reasons.append(f"breaks old cases {broken}")
    if fixed < gates["fixed_min"]:
        reasons.append(f"passes only {fixed:.0%} of mined-case runs")
    return {"stage": "offline", "passed": not reasons, "reasons": reasons,
            "baseline": b, "candidate": c, "gate": g, "verdict": compare(b, c),
            "broken": broken, "fixed": fixed, "cases": len(cases), "trials": trials}

# ------------------------------------------------------------ 4. shadow
def shadow(current, candidate, requests, gates=GATES) -> dict:
    """Both versions answer every mirrored request. Users get only the current
    version's answer; the candidate's is graded and thrown away."""
    shown, worse, better, cur_ok, cand_ok = [], 0, 0, [], []
    for req in requests:
        live, trial = current(req["question"]), candidate(req["question"])
        shown.append(live)                                  # the candidate's never is
        a, b = contains_expected(live, req), contains_expected(trial, req)
        cur_ok.append(a)
        cand_ok.append(b)
        worse, better = worse + (a and not b), better + (b and not a)
    g = gate(cur_ok, cand_ok)
    share = worse / len(requests)
    reasons = []
    if g["block"]:
        reasons.append(f"regression gate blocks (z={g['z']})")
    if share > gates["shadow_max_worse"]:
        reasons.append(f"worse on {share:.0%} of requests")
    return {"stage": "shadow", "passed": not reasons, "reasons": reasons,
            "requests": len(requests), "worse": worse, "better": better,
            "gate": g, "shown": shown}

# ------------------------------------------------------------ 5. canary
def routed_to_candidate(request_id: str, share: float) -> bool:
    """A stable hash, so a request (in production: a user) always gets the same side."""
    return int(hashlib.sha256(request_id.encode()).hexdigest(), 16) % 1000 < share * 1000


def measure_arm(records: list[dict]) -> dict:
    """SLOs and success-budget burn for one side of the canary, from the traces."""
    slos = measure_slos([r["run"] for r in records],
                        {r["trace_id"]: r["eval"] for r in records}, CANARY_SLOS)
    success = next(s for s in slos if s["name"] == "Task success")
    left = success["budget_left"]                # burn rate = 1 - budget left
    burn = None if left is None else round(1 - left, 1)
    return {"runs": len(records), "slos": slos, "burn": burn,
            "missed": [s["name"] for s in slos if s["met"] is False]}


def canary(current, candidate, requests, gates=GATES) -> dict:
    """The candidate serves `canary_share` of real traffic, the current version the
    rest. Roll back if the candidate misses an SLO or burns its error budget too fast."""
    records = [serve(candidate if routed_to_candidate(r["id"], gates["canary_share"])
                     else current, r) for r in requests]
    cand = [r for r in records if r["version"] == candidate.version]
    ctrl = [r for r in records if r["version"] == current.version]
    c, k = measure_arm(cand), measure_arm(ctrl)
    reasons = [f"missed {', '.join(c['missed'])}"] if c["missed"] else []
    if c["burn"] is not None and c["burn"] > gates["canary_max_burn"]:
        reasons.append(f"burn rate {c['burn']} over {gates['canary_max_burn']}")
    hold = c["runs"] < gates["canary_min_runs"] and not reasons
    if hold:                                    # keep watching; don't promote yet
        reasons = ["too few runs to tell"]
    return {"stage": "canary", "passed": not reasons, "hold": hold,
            "reasons": reasons, "candidate": c, "control": k, "records": records}

# ------------------------------------------------------------ 6. one turn of the loop
def improvement_turn(current, candidate, production, suite, mirrored, live,
                     gates=GATES) -> dict:
    """Mine, grow the suite, then offline, shadow and canary, stopping at the first
    gate that fails. The new cases join the suite whatever the decision."""
    failures = mine_failures(production)
    new_cases, skipped = to_cases(failures, suite)
    stages = [offline_eval(current, candidate, suite, new_cases, gates=gates)]
    if stages[-1]["passed"]:
        stages.append(shadow(current, candidate, mirrored, gates))
    if stages[-1]["passed"]:
        stages.append(canary(current, candidate, live, gates))
    last = stages[-1]
    decision = ("promote" if last["passed"] else
                "reject" if last["stage"] != "canary" else      # no user saw it
                "hold" if last["hold"] else "rollback")
    return {"release": candidate.version, "replaces": current.version,
            "decision": decision, "reasons": last["reasons"],
            "stopped_at": None if decision == "promote" else last["stage"],
            "failures": len(failures), "skipped": skipped, "new_cases": new_cases,
            "suite": suite + new_cases, "stages": stages, "gates": dict(gates)}


def evidence(turn: dict) -> dict:
    """The decision record to keep: small, JSON-ready, no raw traces or answers."""
    keep = {"offline": lambda s: {"cases": s["cases"], "trials": s["trials"],
                                  "baseline": round(s["baseline"]["rate"], 3),
                                  "candidate": round(s["candidate"]["rate"], 3),
                                  "z": s["gate"]["z"], "broken": s["broken"],
                                  "fixed": s["fixed"]},
            "shadow": lambda s: {"requests": s["requests"], "worse": s["worse"],
                                 "better": s["better"], "z": s["gate"]["z"]},
            "canary": lambda s: {"runs": s["candidate"]["runs"],
                                 "burn": s["candidate"]["burn"],
                                 "slos": {x["name"]: x["value"]
                                          for x in s["candidate"]["slos"]},
                                 "control_burn": s["control"]["burn"]}}
    return {k: turn[k] for k in ("release", "replaces", "decision", "stopped_at",
                                 "reasons", "gates")} | {
        "new_cases": [{"id": c["id"], "source": c["source"]} for c in turn["new_cases"]],
        "stages": {s["stage"]: {"passed": s["passed"], **keep[s["stage"]](s)}
                   for s in turn["stages"]}}

# ------------------------------------------------------------ demo
def _slo(arm: dict, name: str):
    return next(s["value"] for s in arm["slos"] if s["name"].startswith(name))


def show(turn: dict) -> None:
    print(f"{turn['release']} (replacing {turn['replaces']})")
    print(f"  mined     {turn['failures']} failed runs -> {len(turn['new_cases'])} new "
          f"cases ({turn['skipped']['duplicate']} duplicates dropped)")
    for c in turn["new_cases"]:
        print(f"              {c['id']:<24}{c['question']}")
    for s in turn["stages"]:
        verdict = "PASS" if s["passed"] else "STOP"
        if s["stage"] == "offline":
            b, c = s["baseline"], s["candidate"]
            print(f"  offline   {verdict}  {s['cases']} cases x {s['trials']} trials: "
                  f"baseline {b['rate']:.0%}, candidate {c['rate']:.0%}\n            "
                  f"z={s['gate']['z']}, old cases broken {len(s['broken'])}, "
                  f"mined cases passed {s['fixed']:.0%}")
        elif s["stage"] == "shadow":
            print(f"  shadow    {verdict}  {s['requests']} mirrored requests: candidate "
                  f"better on {s['better']}, worse on {s['worse']}\n            "
                  f"users saw only {turn['replaces']}'s answers")
        else:
            c, k = s["candidate"], s["control"]
            print(f"  canary    {verdict}  {c['runs']} runs: success "
                  f"{_slo(c, 'Task'):.0%}, p95 {_slo(c, 'p95'):,.0f} ms, "
                  f"${_slo(c, 'Cost'):.3f}/task, burn {c['burn']}\n"
                  f"            current version: success "
                  f"{_slo(k, 'Task'):.0%}, burn {k['burn']}")
        if s["reasons"]:
            print(f"            because: {'; '.join(s['reasons'])}")
    print(f"  decision  {turn['decision'].upper()}\n")


SUITE = [{"id": "-".join(normalize(q).split()[:4]), "question": q, "expect": a}
         for q, a in POOL[:7]]                    # the cases written before launch


def releases() -> tuple:
    """The demo's releases: 1.4 in production, and two candidates that fix it."""
    v14 = FakeAgent("support-agent 1.4", wrong={
        "How many orders were cancelled?": LOOPS,
        "What was revenue in March?": "Revenue in March was $48,210.",
        "Which region sold the most in March?": "The south region sold the most."})
    v15 = FakeAgent("support-agent 1.5")               # new prompt and tool description
    v16 = FakeAgent("support-agent 1.6", slow=3.5)     # the same fixes, far more thinking
    return v14, v15, v16


if __name__ == "__main__":
    v14, v15, v16 = releases()
    production = [serve(v14, r) for r in traffic(200, seed=1)]
    turns = [improvement_turn(v14, cand, production, SUITE,
                              traffic(100, seed=2), traffic(400, seed=3))
             for cand in (v15, v16)]
    for t in turns:
        show(t)
    with open("release_decisions.json", "w") as f:
        json.dump([evidence(t) for t in turns], f, indent=1)
    print("wrote release_decisions.json; the suite now has "
          f"{len(turns[0]['suite'])} cases")
