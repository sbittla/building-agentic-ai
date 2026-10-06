"""Chapters 8-10 reference solutions."""
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
import pytest
from fakemodel import tool, text, last_user_text

def test_8_3_top_customers(model):
    import ch08_sql_tools as s, ch04_agent
    gold = ("SELECT c.name, SUM(oi.quantity * p.price) AS revenue FROM customers c JOIN orders o "
            "ON o.customer_id = c.id JOIN order_items oi ON oi.order_id = o.id JOIN products p ON "
            "p.id = oi.product_id WHERE o.status != 'cancelled' GROUP BY c.id ORDER BY revenue DESC LIMIT 5")
    model.reset([[tool("get_schema", {})], [tool("run_query", {"sql": gold})], [text("Customer 13 leads.")]])
    ch04_agent.run_agent("Top 5 customers?", s.TOOLS, s.run_tool, system=s.SYSTEM, verbose=False)
    result = model.calls[2]["messages"][-1]["content"][0]["content"]
    assert "Customer 13 | 19238.0" in result

def test_8_4_self_correction(model):
    import ex8_4_self_correct as ex
    model.reset([[tool("run_query", {"sql": "SELECT city, COUNT(*) FROM clients GROUP BY city"})],
                 [tool("get_schema", {})],
                 [tool("run_query", {"sql": "SELECT city, COUNT(*) n FROM customers GROUP BY city ORDER BY n DESC LIMIT 1"})],
                 [text("Most customers are in one city.")]])
    answer, errors = ex.main()
    assert len(errors) == 1 and "no such table: clients" in errors[0]

def test_8_5_retry_budget_and_log(ws):
    import sol_ch08_sql_tools as s
    Path(s.LOG).unlink(missing_ok=True); s.new_question()
    for _ in range(3):
        assert s.run_query("SELECT nope FROM nowhere").startswith("ERROR: no such table")
    assert "3 failed queries" in s.run_query("SELECT 1")
    log = [json.loads(l) for l in Path(s.LOG).read_text().splitlines()]
    assert len(log) == 3 and not any(r["ok"] for r in log)
    s.new_question()
    assert s.run_query("SELECT COUNT(*) FROM orders").endswith("400")

def test_8_6_confirm_tables(ws, monkeypatch):
    import sol_ch08_sql_tools as s
    s.new_question()
    monkeypatch.setattr(s, "ask_user", lambda prompt: "customers")      # user narrows it
    assert "approved tables: ['customers']" in s.propose_tables(["customers", "orders"], "count")
    assert "not approved" in s.run_query("SELECT * FROM orders JOIN customers ON 1")
    assert s.run_query("SELECT COUNT(*) FROM customers").endswith("50")
    assert s.propose_tables(["clients"], "x").startswith("ERROR: unknown tables")

def test_8_7_eval_harness(model):
    import ex8_7_eval_harness as ex
    gold = dict(ex.GOLD)
    def answer(kw):
        q = last_user_text(kw)
        sql = gold[q] if q != "How many orders were cancelled?" else "SELECT COUNT(*) FROM orders"
        return [text(f"Here you go.\n```sql\n{sql}\n```")]
    model.reset(default=answer)
    score, results = ex.evaluate()
    assert len(ex.GOLD) == 15 and score == pytest.approx(14 / 15)
    assert [q for q, ok, _ in results if not ok] == ["How many orders were cancelled?"]

def test_m_wilson_and_compare():
    from i_measure import wilson, run_suite, compare, simulated_agent, CASES
    low, high = wilson(17, 20)
    assert round(low, 2) == 0.64 and round(high, 2) == 0.95
    assert wilson(0, 0) == (0.0, 1.0)
    a = run_suite(simulated_agent(0.70, seed=1), CASES, 30)
    b = run_suite(simulated_agent(0.80, seed=2), CASES, 30)
    assert compare(a, b) == "better" and compare(b, a) == "worse"
    assert compare(a, a).startswith("can't tell")

def test_m_3_sql_suite(model, ws):
    import exM_3_sql_suite as ex
    cases = {c["question"]: c for c in ex.load_cases("eval_sql.jsonl") if "answer_sql" in c}
    asked = {}
    def answer(kw):
        q = last_user_text(kw)
        asked[q] = asked.get(q, 0) + 1
        value = ex.expected_value(cases[q])
        if q == "How many customers do we have?" and asked[q] % 2:   # wrong on every other run
            value = "I'm not sure"
        return [text(f"The answer is {value}.")]
    model.reset(default=answer)
    before, after = ex.main(trials=2)
    assert before["runs"] == 2 * len(cases) and "customers" in before["flaky"]
    assert before["passes"] == before["runs"] - 1
    assert ex.states_value("We have 1,234 orders.", {"answer_sql": "SELECT 1234"})

def test_9_3_9_4_organizer_decline_then_undo(ws, monkeypatch):
    import builtins, ch09_organizer as o
    o._plans.clear()
    o.propose_moves()
    monkeypatch.setattr(builtins, "input", lambda p: "n")
    assert o.run_tool("apply_plan", {"plan_id": "plan-1"}).startswith("DECLINED")
    monkeypatch.setattr(builtins, "input", lambda p: "y")
    before = sorted(p.name for p in o.ROOT.iterdir())
    o.run_tool("apply_plan", {"plan_id": "plan-1"})
    o.run_tool("undo_plan", {"plan_id": "plan-1"})
    after = sorted(p.name for p in o.ROOT.iterdir() if p.is_file() or any(p.iterdir()))
    assert set(before) <= set(after) | {d for d in before if (o.ROOT / d).is_dir()}

def test_9_5_9_6_partial_and_by_date(ws, monkeypatch):
    import ch09_organizer as o, importlib
    o._plans.clear()
    import sol_ch09_organizer as sol
    importlib.reload(sol)
    out = sol.run_tool("propose_by_date", {})
    assert "photos/" in out or "0 moves" in out
    sol.run_tool("propose_moves", {})
    plan = f"plan-{len(o._plans)}"
    n = len(o._plans[plan])
    monkeypatch.setattr(sol, "ask_human", lambda prompt: "1,2")
    res = sol.run_tool("apply_plan", {"plan_id": plan})
    assert "Moved 2 files" in res or "auto-approved" in res
    monkeypatch.setattr(sol, "ask_human", lambda prompt: "y")
    sol.run_tool("undo_plan", {"plan_id": plan})

@pytest.fixture
def fresh_repo(ws):
    shutil.rmtree("buggy_repo", ignore_errors=True)
    subprocess.run([sys.executable, "ch10_make_repo.py"], check=True, capture_output=True)
    import ch10_fixer
    ch10_fixer.REPO = Path("buggy_repo").resolve(); ch10_fixer.history.clear()
    return Path("buggy_repo")

FIX_SUBTOTAL = ("sum(price for price, qty in items)", "sum(price * qty for price, qty in items)")
FIX_DISCOUNT = ("amount * percent ", "amount * percent / 100 ")

def test_10_3_fixer_with_write_file(model, fresh_repo):
    import ch10_fixer as f, ch04_agent
    src = (fresh_repo / "pricing.py").read_text()
    fixed = src.replace(*FIX_SUBTOTAL).replace(*FIX_DISCOUNT)
    model.reset([[tool("run_tests", {})], [tool("read_file", {"path": "pricing.py"})],
                 [tool("write_file", {"path": "pricing.py", "content": fixed})],
                 [tool("run_tests", {})], [text("Fixed quantity and percent bugs.")]])
    ch04_agent.run_agent("Make all tests pass.", f.TOOLS, f.run_tool, system=f.SYSTEM,
                         max_iterations=15, should_stop=f.should_stop, verbose=False)
    assert f.history == [3, 0]

def test_10_4_protection(model, fresh_repo):
    import ex10_4_protection as ex
    model.reset([[tool("write_file", {"path": "test_pricing.py", "content": "def test(): pass"})],
                 [text("I was not allowed to edit tests.")]])
    assert len(ex.main()) == 1
    assert "def test_total" in (fresh_repo / "test_pricing.py").read_text()

def test_10_5_and_10_6_replace_in_file(model, fresh_repo):
    subprocess.run([sys.executable, str(Path(__file__).parents[1] / "exercises" / "sol_ch10_make_repo2.py")],
                   check=True, capture_output=True)
    import sol_ch10_fixer as sol, ch04_agent, ch10_fixer
    tools, run_tool = sol.make_tools()
    assert "5 failed" in run_tool("run_tests", {})
    assert "appears 0 times" in run_tool("replace_in_file", {"path": "pricing.py", "old": "nope", "new": "x"})
    assert run_tool("replace_in_file", {"path": "test_pricing.py", "old": "a", "new": "b"}).startswith("ERROR")
    script = [[tool("replace_in_file", {"path": "pricing.py", "old": a, "new": b})] for a, b in (FIX_SUBTOTAL, FIX_DISCOUNT)]
    script += [[tool("replace_in_file", {"path": "shipping.py", "old": "cost = cost + 2", "new": "cost = cost * 2"})],
               [tool("replace_in_file", {"path": "shipping.py", "old": "min(cost, 30.0)", "new": "min(cost, 40.0)"})],
               [tool("run_tests", {})], [text("All 7 tests pass.")]]
    model.reset(script)
    answer, messages, _ = ch04_agent.run_agent("Make all tests pass.", tools, run_tool, system=sol.SYSTEM,
                         max_iterations=10, should_stop=sol.should_stop, verbose=False)
    outputs = [c["content"] for m in messages if m["role"] == "user" and isinstance(m["content"], list) for c in m["content"]]
    assert "7 passed" in run_tool("run_tests", {}), outputs

@pytest.mark.skipif(not Path("/opt/course/course.py").exists(), reason="runs in the course image")
def test_10_7_benchmark_through_sandbox(model, ws, monkeypatch):
    """Starts the real sandbox worker (from the course CLI) in a thread."""
    os.environ["COURSE_WORKSPACE"] = str(ws)
    sys.path.insert(0, "/opt/course")
    import course
    course.WS = ws
    import ch10_sandbox
    monkeypatch.setattr(ch10_sandbox, "QUEUE", ws / ".sandbox")
    threading.Thread(target=course.cmd_sandbox_worker, args=([],), daemon=True).start()
    import ex10_7_benchmark as ex
    fixes = {"off_by_one": ("xs[-n - 1:]", "xs[-n:]"), "wrong_operator": ("w + h", "w * h")}
    def fixer(kw):
        n = len(kw["messages"])
        repo = ex.base.REPO.name
        if n == 1:
            return [tool("run_tests", {})]
        if n == 3:
            return [tool("replace_in_file", {"path": "mod.py", "old": fixes[repo][0], "new": fixes[repo][1]})]
        if n == 5:
            return [tool("run_tests", {})]
        return [text("fixed")]
    model.reset(default=fixer)
    rows = ex.main(runs=1, use_sandbox=True, bugs=["off_by_one", "wrong_operator"])
    assert all(r["passed"] and r["tests_unchanged"] for r in rows)

def test_10_7_bug_catalogue_is_really_buggy(ws):
    import ex10_7_benchmark as ex, sol_ch10_fixer as sol, ch10_fixer as base
    for name in ex.BUGS:
        base.REPO = ex.make_repo(name).resolve()
        _, run_tool = sol.make_tools()
        assert "1 failed" in run_tool("run_tests", {}), name
