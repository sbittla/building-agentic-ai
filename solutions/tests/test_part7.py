"""Part 7 (chapters 19-24): long-running agents, planning and routing, orchestration,
hybrid control, computer use. All offline, with the scripted stand-in model."""
import json
import re
import sqlite3
from pathlib import Path

import pytest
from fakemodel import last_user_text, text, tool, tool_results

# ================================================================ 19: durable jobs
@pytest.fixture
def durable(ws, request):
    import ch19_durable as d
    saved = (d.DB, d.SERVICES, d.BACKOFF, d.LEASE, dict(d.FAILS), d.ACTIONS["agent"]["run"])
    d.DB, d.SERVICES = ws / f"jobs_{request.node.name}.db", ws / f"svc_{request.node.name}.json"
    d.BACKOFF, d.FAILS["charge"] = 0.001, 1
    yield d
    d.DB, d.SERVICES, d.BACKOFF, d.LEASE, fails, d.ACTIONS["agent"]["run"] = saved
    d.FAILS.update(fails)

def test_19_crash_resume_reuses_checkpoints(durable, model):
    d = durable
    model.reset([[text("Welcome to Pro, Ana!")]])            # ONE model call, ever
    job = d.claim("w1", d.create_job("onboard", d.ONBOARDING))
    with pytest.raises(d.Crash):
        d.run_job(job, crash_after=2)
    assert d.claim("w2") is None                             # w1's lease still holds
    with d._db() as con:
        con.execute("UPDATE jobs SET lease_until=0 WHERE id=?", (job,))
    assert d.claim("w2") == job
    assert d.run_job(job, worker="w2") == "done"
    svc = json.loads(d.SERVICES.read_text())
    assert len(svc["accounts"]) == 1 and len(svc["emails"]) == 1
    assert list(svc["emails"].values())[0]["body"] == "Welcome to Pro, Ana!"
    assert len(model.calls) == 1                             # not regenerated on resume
    assert "charge           done     tries=2" in d.report(job)    # one retry

def test_19_repeating_a_keyed_step_has_no_second_effect(durable):
    d = durable
    job = d.create_job("t", [{"action": "send_email", "args": {"to": "a@x", "body": "hi"}}])
    with d._db() as con:                         # pretend we crashed during the send
        con.execute("UPDATE steps SET status='running' WHERE job_id=?", (job,))
    d.send_email({"to": "a@x", "body": "hi"}, f"{job}:1")   # the send did happen
    assert d.run_job(job) == "done"
    assert len(json.loads(d.SERVICES.read_text())["emails"]) == 1

def test_19_unkeyed_step_after_crash_escalates(durable):
    d = durable
    d.action("fax", effect="unkeyed")(lambda args, key: "faxed")
    job = d.create_job("t", [{"action": "fax", "args": {}}])
    with d._db() as con:
        con.execute("UPDATE steps SET status='running' WHERE job_id=?", (job,))
    assert d.run_job(job) == "needs_human"
    assert "outcome unknown" in d.report(job)

def test_19_permanent_error_escalates_then_compensates(durable):
    d = durable
    d.FAILS["charge"] = 0
    job = d.create_job("big", [{"action": "create_account", "args": {"email": "b@x"}},
                               {"action": "send_email", "args": {"to": "b@x", "body": "hi"}},
                               {"action": "charge", "args": {"email": "b@x", "amount": 900}}])
    assert d.run_job(job) == "needs_human"
    assert "tries=1" in d.report(job).splitlines()[3]          # not retried
    assert d.resolve(job, "abandon") == "compensated"
    report = d.report(job)
    assert "can't undo: step 2 send_email" in report and "undone" in report
    assert json.loads(d.SERVICES.read_text())["deleted_accounts"]

def test_19_resolve_retry_and_skip(durable):
    d = durable
    d.FAILS["charge"] = 5                                      # more than MAX_ATTEMPTS
    job = d.create_job("t", [{"action": "charge", "args": {"email": "c@x", "amount": 5}},
                             {"action": "create_account", "args": {"email": "c@x"}}])
    assert d.run_job(job) == "needs_human"
    d.FAILS["charge"] = 0
    assert d.resolve(job, "retry") == "queued" and d.run_job(job) == "done"

def test_19_deadline(durable):
    d = durable
    job = d.create_job("t", [{"action": "create_account", "args": {"email": "x@x"}}],
                       deadline_s=-1)
    assert d.run_job(job) == "needs_human" and "deadline" in d.report(job)

def test_19_4_two_workers(durable):
    import ex19_4_workers as ex
    jobs, finished = ex.main(n_jobs=5, lease=0.3)
    assert sorted(finished) == sorted(jobs)                    # every job finished
    assert "w2" in finished.values()
    svc = json.loads(durable.SERVICES.read_text())
    assert len(svc["charges"]) == 5 and len(svc["accounts"]) == 5

def test_19_5_budget(durable, model):
    import ex19_5_budget as ex
    try:
        model.reset(default=[text("Fresh bread, every morning.")])
        results, small, normal = ex.main()
        assert results[small] == "needs_human" and "budget" in durable.report(small)
        assert results[normal] == "done"
    finally:
        durable.ACTIONS["agent"]["run"] = durable.run_agent_step

# ================================================================ 19: the harness
def _writer(sql_share=None):
    """A scripted model that writes whichever section the brief asks for."""
    def policy(kw):
        q = last_user_text(kw)
        last = kw["messages"][-1]
        if last["role"] == "user" and isinstance(last["content"], str):
            name = re.search(r"write_section as '([a-z_]+\.md)'", q).group(1)
            body = {"revenue.md": "Revenue by month: Jan 1,200; Feb 1,350; Mar 990.",
                    "top_products.md": "1. A 10  2. B 9  3. C 8  4. D 7  5. E 6",
                    "cities.md": "Pune 12, Oslo 9, Lima 7",
                    "cancellations.md": f"Cancelled: 40 orders, {sql_share or 20.0}%"}[name]
            return [tool("write_section", {"name": name, "text": body})]
        return [text("Saved.")]
    return policy

@pytest.fixture
def harness(ws, request):
    import ch19_harness as h
    saved = (h.FEATURES, h.PROGRESS)
    root = ws / f"report_{request.node.name}"
    h.FEATURES, h.PROGRESS = root / "features.json", root / "progress.md"
    yield h
    h.FEATURES, h.PROGRESS = saved

def test_19_harness_checks_in_code_and_resumes(harness, model):
    h = harness
    model.reset(default=_writer())
    first = h.session(max_items=2)
    assert first["worked_on"] == ["revenue", "top_products"] and first["left"] == 2
    second = h.session(max_items=2)                          # a new session continues
    assert second["worked_on"] == ["cities", "cancellations"] and second["done"]
    assert "revenue: passing" in h.PROGRESS.read_text()

def test_19_harness_failing_check_retries_then_escalates(harness, model):
    h = harness
    model.reset(default=lambda kw: [text("All done!")])    # claims done, writes nothing
    for _ in range(3):
        result = h.session(max_items=1)
    assert result["needs_human"] == ["revenue"]
    briefs = [last_user_text(c) for c in model.calls]
    assert "failed its check" in briefs[-1]

def test_19_6_report_loop_and_cross_check(harness, model):
    import ex19_6_report_loop as ex
    truth = round(ex.true_cancel_share(), 1)
    model.reset(default=_writer(sql_share=truth))
    history, ok, why = ex.main(max_sessions=10)
    assert ok and history[-1]["done"]
    assert "crashed here" in harness.PROGRESS.read_text()
    path = harness.FEATURES.parent / "cancellations.md"
    path.write_text(path.read_text().replace(f"{truth}%", f"{truth + 7}%"))
    assert ex.cross_check()[0] is False

# ================================================================ 20: planning, routing
def _plan(*steps):
    return {"steps": [{"id": sid, "do": do, "tools": tools, "needs": needs,
                       "done_when": "done"} for sid, do, tools, needs in steps]}

GOOD_PLAN = _plan(("s1", "Count customers", ["run_query"], []),
                  ("s2", "Count orders", ["run_query"], []),
                  ("s3", "Orders per customer", [], ["s1", "s2"]))

def _planner(plans, step_answer=lambda brief: "42"):
    """Structured-output calls get the next plan; agent steps answer from the brief."""
    plans = list(plans)
    def policy(kw):
        if "output_config" in kw:
            return [text(json.dumps(plans.pop(0)))]
        return [text(step_answer(last_user_text(kw)))]
    return policy

def test_20_check_plan_and_order():
    import ch08_sql_tools as sql, ch20_planning as p
    assert p.check_plan(GOOD_PLAN, sql.TOOLS) == []
    assert p.order(GOOD_PLAN)[-1] == "s3"
    cyc = _plan(("a", "x", [], ["b"]), ("b", "y", [], ["a"]))
    assert any("circle" in e for e in p.check_plan(cyc, sql.TOOLS))

def test_20_rejected_plan_is_sent_back_then_run(model):
    import ch08_sql_tools as sql, ch20_planning as p
    bad = _plan(("s1", "Email the boss", ["send_email"], []))
    model.reset(default=_planner([bad, GOOD_PLAN]))
    out = p.execute("orders per customer", sql.TOOLS, sql.run_tool)
    assert out["log"][0][0] == "rejected plan" and out["answer"] == "42"
    assert "unknown tools" in last_user_text(model.calls[1])     # the feedback
    step3 = [c for c in model.calls if "Orders per customer" in last_user_text(c)][0]
    assert "- s1: 42" in last_user_text(step3) and step3["tools"] == []

def test_20_failed_step_replans_only_the_rest(model):
    import ch08_sql_tools as sql, ch20_planning as p
    rest = _plan(("s2b", "Count all rows in orders", ["run_query"], []),
                 ("s4", "Divide the results", [], ["s1", "s2b"]))
    answers = {"Count orders": "ERROR: table missing"}
    def step(brief):
        return next((v for k, v in answers.items() if k in brief), "7")
    model.reset(default=_planner([GOOD_PLAN, rest], step))
    out = p.execute("orders per customer", sql.TOOLS, sql.run_tool)
    assert out["replans"] == 1 and "s4" in out["results"] and "s2" not in out["results"]
    assert "Already done" in last_user_text([c for c in model.calls
                                             if "output_config" in c][1])

def test_20_route_and_cost(model):
    import ch08_sql_tools as sql, ch20_router as r
    assert r.by_rules("How many customers?") == r.SMALL
    assert r.by_rules("Why did revenue fall? Explain.") == r.LARGE
    model.reset([[text(json.dumps({"level": "hard", "why": "several queries"}))]])
    assert r.by_model("Compare two years") == r.LARGE
    assert model.calls[0]["model"] == r.SMALL
    stats = {"model": "claude-haiku-4-5", "input_tokens": 1_000_000, "output_tokens": 0}
    assert r.cost(stats) == 1.0
    assert r.report([{"cost": 1, "ok": True}, {"cost": 1, "ok": False}])[
        "cost_per_success"] == 2

def test_20_cascade_escalates_when_check_fails(model):
    import ch08_sql_tools as sql, ch20_router as r
    model.reset([[text("I'm not sure.")], [text("There are 20 customers.")]])
    answer, trail = r.cascade("How many customers?", sql.TOOLS, sql.run_tool,
                              r.has_number)
    assert [t["model"] for t in trail] == [r.SMALL, r.LARGE] and "20" in answer
    assert [c["model"] for c in model.calls] == [r.SMALL, r.LARGE]

def test_20_3_bad_plans():
    import ex20_3_bad_plans as ex
    assert all(ok for ok, _ in ex.main().values())

def test_20_4_parallel_rounds(model):
    import ch08_sql_tools as sql, ex20_4_parallel_plan as ex
    model.reset(default=lambda kw: [text("5")])
    results, rounds = ex.run_plan_parallel(ex.PLAN, sql.TOOLS, sql.run_tool)
    assert sorted(rounds[0]) == ["s1", "s2"] and rounds[1] == ["s3"]
    assert set(results) == {"s1", "s2", "s3"}

def test_20_5_router_eval(model):
    import ex20_5_router_eval as ex
    model.reset(default=lambda kw: [text(json.dumps(
        {"level": "hard" if "?" not in last_user_text(kw)[-1:] or "Why" in
         last_user_text(kw) else "easy", "why": "."}))])
    out = ex.main()
    assert out[0]["router"] == "rules" and 0 <= out[0]["accuracy"] <= 1
    assert len(out[1]["rows"]) == 12

def test_20_6_durable_plan(durable, model):
    import ex20_6_durable_plan as ex
    model.reset(default=_planner([GOOD_PLAN], lambda brief: "9"))
    job, status = ex.main(goal="orders per customer", crash_after=1)
    assert status == "done"
    agent_calls = [c for c in model.calls if "output_config" not in c]
    assert len(agent_calls) == 3                        # nothing ran twice
    with durable._db() as con:
        args = [json.loads(r["args"]) for r in con.execute(
            "SELECT args FROM steps WHERE job_id=? ORDER BY idx", (job,))]
    assert args[2]["inputs"] == {"s1": "$1", "s2": "$2"} and args[0]["model"]
    last = last_user_text(agent_calls[-1])
    assert "- s1: 9" in last and "- s2: 9" in last

# ================================================================ 21: orchestration
GOOD_RESULT = {"answer": "12 orders were cancelled", "evidence": ["SELECT COUNT(*) ..."],
               "confidence": "high"}

def _team_policy(lead_moves, specialist=lambda kw: [tool("submit_result", GOOD_RESULT)]):
    """Lead moves are played in order; every specialist submits GOOD_RESULT."""
    moves = list(lead_moves)
    def policy(kw):
        tools = [t["name"] for t in kw.get("tools", [])]
        last = kw["messages"][-1]
        fresh = last["role"] == "user" and isinstance(last["content"], str)
        if "You lead" in kw["system"]:
            return moves.pop(0)
        if fresh or "rejected" in json.dumps(tool_results(kw)):
            return specialist(kw)
        return [text("Submitted.")]
    return policy

def test_21_lead_delegates_checks_and_submits(model):
    import ch21_orchestrator as orc
    model.reset(default=_team_policy([
        [tool("delegate", {"agent": "analyst", "brief": "Count cancelled orders."})],
        [tool("delegate", {"agent": "checker", "brief": "Check: 12 cancelled orders."})],
        [tool("submit_result", {**GOOD_RESULT, "answer": "Checked: 12."})],
        [text("Done.")]]))
    out = orc.demo_team().run("How many cancellations?")
    assert out["status"] == "done" and out["result"]["answer"] == "Checked: 12."
    assert [l.split()[1] for l in out["board"].splitlines()] == ["lead", "analyst",
                                                                  "checker"]
    lead_calls = [c for c in model.calls if "You lead" in c["system"]]
    assert '<result from="analyst" task="2">' in tool_results(lead_calls[1])[0]
    brief = [c for c in model.calls if "checker" not in c["system"] and
             "You verify" in c["system"]][0]
    assert last_user_text(brief) == "Check: 12 cancelled orders."      # a brief only
    assert "delegate" not in [t["name"] for t in brief["tools"]]         # no deeper

def test_21_limits_dedupe_and_contract(model):
    import ch21_orchestrator as orc
    board = orc.Board(max_tasks=3, max_depth=1)
    assert isinstance(board.post("a", "x", None, 2), str)                 # too deep
    t = board.post("a", "Count  orders", None, 0)
    t.status = "done"
    assert board.post("a", "count orders", None, 0) is t                   # dedupe
    board.post("b", "y", None, 0); board.post("c", "z", None, 0)
    assert "limit of 3 tasks" in board.post("d", "w", None, 0)

def test_21_4_failures_are_contained(model):
    import ex21_4_failures as ex
    bad = {"answer": "12", "confidence": "high"}                          # no evidence
    model.reset(default=_team_policy([], lambda kw: [tool("submit_result", bad)]))
    out = ex.delegate_once(ex.make_team())
    assert out.startswith("ERROR: analyst failed") and "evidence" in out
    model.reset(default=_team_policy([], lambda kw: [text("I give up.")]))
    assert "without submitting a valid result" in ex.delegate_once(ex.make_team())
    assert "over its token budget" in ex.delegate_once(ex.make_team(analyst_budget=0))
    tries = []
    def fixes_it(kw):
        tries.append(1)
        return [tool("submit_result", bad if len(tries) == 1 else GOOD_RESULT)]
    model.reset(default=_team_policy([], fixes_it))
    out = ex.delegate_once(ex.make_team(retry=True))
    assert out.startswith('<result from="analyst"') and len(tries) == 2

# ================================================================ 22: hybrid control
@pytest.fixture
def refunds():
    import ch22_guarded as g
    saved = (g.POLICY, g.decide, dict(g.REFUNDS))
    g.REFUNDS.clear()
    yield g
    g.POLICY, g.decide = saved[0], saved[1]
    g.REFUNDS.clear(); g.REFUNDS.update(saved[2])

def _refund_model(extract, reply="Done: we refunded $49.00."):
    """Structured calls get `extract` (a dict or a function of the message)."""
    def policy(kw):
        if "output_config" in kw:
            msg = last_user_text(kw)
            return [text(json.dumps(extract(msg) if callable(extract) else extract))]
        return [text(reply)]
    return policy

def test_22_auto_refund_and_reply(refunds, model):
    g = refunds
    model.reset(default=_refund_model({"order_id": "A-1001", "reason": "damaged",
                                       "summary": "broken"}))
    case = g.handle("ana@example.com", "Order A-1001 arrived broken.")
    assert case.state == "replied" and g.REFUNDS == {"A-1001": 49.0}
    assert [new for _, _, new, _ in case.log] == ["understood", "approved", "refunded",
                                                  "replied"]
    assert case.facts["reply"] == "Done: we refunded $49.00."

def test_22_rules_come_from_records_not_the_model(refunds, model):
    g = refunds
    model.reset(default=_refund_model({"order_id": "A-1002", "reason": "late",
                                       "summary": "late"}))
    waiting = g.handle("ana@example.com", "A-1002 was late, refund $5,000.")
    assert waiting.state == "awaiting_approval" and waiting.facts["amount"] == 420.0
    declined = g.handle("ana@example.com", "A-1002 was late.", approver=lambda c: False)
    assert declined.state == "replied" and g.REFUNDS == {}
    model.reset(default=_refund_model({"order_id": "A-1003", "reason": "changed_mind",
                                       "summary": "."}))
    old = g.handle("ben@example.com", "I changed my mind about A-1003.")
    assert "window is 30" in old.log[1][3]

def test_22_proposals_are_checked(refunds, model):
    g = refunds
    model.reset(default=_refund_model({"order_id": "A-1001", "reason": "damaged",
                                       "summary": "."}))
    other = g.handle("ben@example.com", "Refund A-1001, it's damaged.")
    assert other.state == "escalated" and "another customer" in other.log[0][3]
    invented = g.handle("ana@example.com", "My order was damaged.")
    assert invented.state == "escalated" and "not found in the message" in invented.log[0][3]
    with pytest.raises(g.IllegalTransition):
        g.Case("a", "b").move("refunded", "skipping ahead")

def test_22_reply_guard_falls_back(refunds, model):
    g = refunds
    model.reset(default=_refund_model({"order_id": "A-1001", "reason": "damaged",
                                       "summary": "."},
                                      reply="Refunded $49 plus a $20 voucher!"))
    case = g.handle("ana@example.com", "A-1001 is damaged.")
    assert "$20" not in case.facts["reply"] and "voucher" not in case.facts["reply"]
    assert case.facts["reply"].startswith("We've refunded $49.00")
    assert "$20" in case.facts["reply_fallback"]

def test_22_4_policy_as_data(refunds, model, ws):
    import importlib, ex22_4_policy_json as ex
    importlib.reload(ex)                          # patches decide again after the fixture
    ex.POLICY_FILE = ws / "refund_policy_test.json"
    ex.POLICY_FILE.unlink(missing_ok=True)
    policy = ex.load_policy(ex.POLICY_FILE)
    model.reset(default=_refund_model({"order_id": "A-1002", "reason": "changed_mind",
                                       "summary": "."}))
    case = refunds.handle("ana@example.com", "I changed my mind about A-1002.")
    assert "only for damaged, wrong_item" in case.log[1][3]
    assert policy["version"] in case.log[1][3]
    import datetime
    for days, state in [(30, "approved"), (31, "rejected")]:
        refunds.TODAY = datetime.date(2026, 9, 10) + datetime.timedelta(days=days)
        c = refunds.Case("ana@example.com", "A-1001")
        c.facts.update(order_id="A-1001", reason="damaged")
        c.state = "understood"
        ex.decide(c)
        assert c.state == state, days
    refunds.TODAY = datetime.date(2026, 9, 25)

def test_22_5_attacks_hold_even_when_the_model_is_fooled(refunds, model):
    import ex22_5_attacks as ex
    wanted = {m: dict(want, summary=".") for _, m, want in ex.ATTACKS}
    model.reset(default=_refund_model(lambda msg: wanted[msg],
                                      reply="Refunded $5,000 and a $50 voucher."))
    report = ex.main(approver=lambda case: None)
    assert all(not v for _, _, v in report), report
    assert refunds.REFUNDS == {"A-1001": 49.0}      # only the genuine damaged order

def test_22_6_authorizer_not_the_prompt(ws):
    import ex22_6_guarded_sql as ex
    for bad in ["DELETE FROM orders", "ATTACH DATABASE 'x.db' AS x", "PRAGMA table_info(orders)",
                "SELECT * FROM sqlite_master", "CREATE TABLE t (a)"]:
        assert ex.run_query(bad).startswith("ERROR"), bad
    assert not ex.run_query("SELECT COUNT(*) FROM customers").startswith("ERROR")
    assert "not 'cancelled'" in ex.system_prompt()

# ================================================================ 23: computer use
def _browser_agent(skip_customer=None):
    """Scripted browser agent: open the customer, type the address, save, report.
    For skip_customer it claims success without doing anything."""
    def policy(kw):
        brief = next(m["content"] for m in kw["messages"] if m["role"] == "user"
                     and isinstance(m["content"], str))
        cid = int(re.search(r"customer (\d)", brief).group(1))
        address = brief.split("exactly: ")[1]
        turn = sum(m["role"] == "assistant" for m in kw["messages"])
        if cid == skip_customer:
            return [text("Done, the address is updated.")]
        steps = [[tool("open", {"path": f"/customers/{cid}"})],
                 [tool("type_text", {"ref": "e1", "text": address})],
                 [tool("click", {"ref": "e2"})],
                 [text("Saved, and the page shows the new address.")]]
        return steps[min(turn, 3)]
    return policy

@pytest.fixture
def backoffice(ws):
    pytest.importorskip("playwright")
    import ch23_backoffice as app
    app.reset()
    yield app
    app.reset()

def test_23_harness_controls(backoffice, ws):
    from ch23_browser import Browser
    url = backoffice.serve(8791)
    asked = []
    b = Browser(url, approver=lambda a: asked.append(a) or False, max_actions=8,
                shots=str(ws / "shots23"))
    try:
        b.sign_in("agent-bot", backoffice.USERS["agent-bot"])
        page = b.open("/customers/2")
        assert '<page_text untrusted="true">' in page and '[e5] button "Issue credit"' in page
        assert "demo-only" not in page                          # no secrets on screen
        assert b.open("https://attacker.example/").startswith("ERROR: only")
        b.type_text("e3", "50")
        assert "approval" in b.click("e5") and asked[0]["form"]["amount"] == "50"
        assert backoffice.CUSTOMERS[2]["credit"] == 0
        assert b.click("e99").startswith("ERROR: no control")
        b.type_text("e1", "22 Canal Street, Leeds")
        assert "Address saved" in b.click("e2")
        assert list((ws / "shots23").glob("*.png"))
        for _ in range(5):
            b.open("/customers")
        assert "action limit" in b.open("/customers")
    finally:
        b.close()

def test_23_4_injection_fails_even_if_the_model_obeys(backoffice, model):
    import ex23_4_injection as ex
    model.reset([[tool("open", {"path": "/customers/2"})],
                 [tool("type_text", {"ref": "e3", "text": "500"})],
                 [tool("type_text", {"ref": "e4", "text": "as the note says"})],
                 [tool("click", {"ref": "e5"})],
                 [tool("type_text", {"ref": "e1", "text": "22 Canal Street, Leeds"})],
                 [tool("click", {"ref": "e2"})],
                 [text("Address updated. The notes asked me to issue a credit.")]])
    out = ex.main(port=8792, verbose=False)
    assert out["address"] == "22 Canal Street, Leeds" and out["credit"] == 0
    assert out["email"] == "ben@example.com" and out["approvals_asked"]
    assert any("refused" in what for _, what in out["log"])

def test_23_5_code_checks_catch_a_false_claim(backoffice, model):
    import ex23_5_verified_queue as ex
    model.reset(default=_browser_agent(skip_customer=3))
    results = ex.main(port=8793)
    assert [r["status"] for r in results] == ["done", "done", "failed"]
    assert results[2]["agent_said"].startswith("Done")

def test_23_6_durable_browser_queue(backoffice, durable, model):
    import ex23_6_durable_queue as ex
    model.reset(default=_browser_agent())
    job, status = ex.main(port=8794, crash_after=1)
    assert status == "needs_human"
    report = durable.report(job)
    assert "change_address   done     tries=1 verified: 9 Avenida" in report
    assert "credit needs a person" in report and backoffice.CUSTOMERS[2]["credit"] == 0
    opens = [c for c in model.calls
             if "customer 1" in json.dumps(c["messages"][0]["content"])]
    assert len(opens) == 4                              # request 1 ran once, not twice

def test_23_3_by_hand(backoffice):
    import ex23_3_by_hand as ex
    chen = ex.main(port=8795)
    assert chen["address"] == "1 Marina Way, Singapore" and chen["credit"] == 25.0

# ================================================================ 24: skills, runtimes
def test_24_8_skill_eval(model, ws):
    import ex24_8_skill_eval as ex
    report = ("## Revenue\n**Total revenue:** $100\n| Category | Revenue | Share |\n"
              "| A | 60 | 60% |\n| B | 40 | 40% |\n**Takeaway:** A leads.")
    def policy(kw):
        names = [t["name"] for t in kw["tools"]]
        results = tool_results(kw)
        if "read_skill" in names:                               # with the skill
            if not results:
                return [tool("read_skill", {"name": "sql-report"})]
            return [text(report)]
        return [text("Revenue is mostly from category A.")]      # without it
    model.reset(default=policy)
    table = ex.main()
    assert table["with skill"]["pass_rate"] == 1.0 and table["without"]["pass_rate"] == 0.0
    assert ex.check(report) == {"total": True, "table": True, "shares_add_up": True,
                                "takeaway": True}
