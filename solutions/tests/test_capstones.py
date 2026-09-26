"""Capstone reference implementations: data, servers (deterministic) and agents (scripted)."""
import asyncio
import json
import sys
from pathlib import Path
import pytest
from fakemodel import tool, text, last_user_text

CAP = Path(__file__).parents[1] / "capstones"
sys.path[:0] = [str(CAP)]

def hub(config):
    import ch13_mcp_agent as m13
    return m13.MCPHub(config)

def call_all(config, calls):
    """Start the servers and make direct tool calls (no model)."""
    async def go():
        async with hub(config) as h:
            names = [t["name"] for t in h.tools]
            return names, [await h.call(n, a) for n, a in calls]
    return asyncio.run(go())

# ---------------- capstone 1: customer support
@pytest.fixture(scope="module")
def c1(tmp_path_factory):
    sys.path.insert(0, str(CAP / "c1_support"))
    sys.modules.pop("data", None)          # each capstone has its own data.py
    import data
    data.build()
    sys.modules.pop("data", None)
    import importlib.util
    spec = importlib.util.spec_from_file_location("c1_agent", CAP / "c1_support" / "agent.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    sys.path.remove(str(CAP / "c1_support"))
    return mod

def test_c1_servers(ws, c1):
    names, r = call_all(c1.CONFIG, [                           # signed in as asha@example.com
        ("orders__get_order", {"order_id": "A2001"}),
        ("orders__get_order", {"order_id": "A2003"}),            # Ben's order
        ("orders__create_return", {"order_id": "A2002", "reason": "x"}),
        ("orders__create_return", {"order_id": "A2001", "reason": "broken"}),
        ("orders__create_return", {"order_id": "A2001", "reason": "broken"}),
        ("helpdesk__search_articles", {"query": "return refund days"}),
        ("handoff__escalate", {"summary": "wants a human", "priority": "urgent"}),
        ("orders__list_orders", {})])
    assert "Headphones" in r[0][0] and not r[0][1]
    assert r[1][1] and "Laptop" not in r[1][0]                         # identity check
    assert r[2][1] and "return window is 30 days" in r[2][0]           # outside policy
    assert "Return created" in r[3][0] and "already exists" in r[4][0]  # idempotent
    assert r[5][0].startswith("return-policy.md")
    assert Path("handoff_queue.jsonl").exists()
    assert "A2001" in r[7][0] and "A2003" not in r[7][0]
    # No tool accepts an email: the model can't choose whose orders it sees.
    async def schemas():
        async with hub(c1.CONFIG) as h:
            return {t["name"]: t["input_schema"] for t in h.tools}
    s = asyncio.run(schemas())
    assert not any("email" in s[n].get("properties", {}) for n in s if n.startswith("orders__"))

def test_c1_identity_comes_from_the_host(ws, c1):
    names, r = call_all(c1.config_for("ben@example.com"), [("orders__list_orders", {})])
    assert "A2003" in r[0][0] and "A2001" not in r[0][0]
    cfg = c1.config_for("")
    names, r = call_all(cfg, [("orders__list_orders", {})])
    assert r[0][1] and "No customer is signed in" in r[0][0]

def test_c1_agent_return_needs_approval(ws, c1, model):
    from common import ask
    import sqlite3
    with sqlite3.connect("support.db") as con:
        con.execute("DELETE FROM returns")
    model.reset([[tool("orders__get_order", {"order_id": "A2001"})],
                 [tool("orders__create_return", {"order_id": "A2001", "reason": "broken"})],
                 [text("I've asked a colleague to approve your refund.")]])
    decisions = []
    answer, msgs = asyncio.run(ask(c1.CONFIG, "Refund A2001 please", c1.SYSTEM, c1.RULES,
                                   approver=lambda n, a: decisions.append(n) or False))
    assert decisions == ["orders__create_return"]
    assert msgs[4]["content"][0]["content"].startswith("DECLINED")
    with sqlite3.connect("support.db") as con:
        assert con.execute("SELECT COUNT(*) FROM returns").fetchone()[0] == 0
    tools_seen = [t["name"] for t in model.calls[0]["tools"]]
    assert "orders__create_return" in tools_seen and "handoff__escalate" in tools_seen

def test_c1_eval_file_is_valid():
    cases = [json.loads(l) for l in open(CAP / "c1_support" / "eval_cases.jsonl")]
    assert len(cases) >= 12 and all("question" in c for c in cases)
    assert not any("@" in c["question"] and c["id"] not in ("impersonate", "other-email") for c in cases)

# ---------------- capstone 2: data analyst
def _load(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name.replace("/", "_"), CAP / name)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def test_c2_servers_and_gold(ws):
    a = _load("c2_analyst/agent.py")
    gold = [json.loads(l) for l in open(CAP / "c2_analyst" / "gold.jsonl")]
    names, r = call_all(a.CONFIG, [
        ("warehouse__list_tables", {}),
        ("warehouse__describe_table", {"table": "products", "columns": ["name", "price"]}),
        ("warehouse__run_query", {"sql": gold[0]["sql"]}),
        ("warehouse__run_query", {"sql": "DELETE FROM orders"}),
        ("charts__make_chart", {"sql": "SELECT category, COUNT(*) FROM products GROUP BY category",
                                "chart_type": "bar", "title": "Products per category"})])
    assert "orders (400 rows)" in r[0][0]
    assert r[1][0].startswith("columns: name TEXT, price REAL")
    assert r[2][0].endswith("400")
    assert r[3][1] and "readonly" in r[3][0]
    assert Path(r[4][0]).exists()

def test_c2_table_confirmation():
    a = _load("c2_analyst/agent.py")
    answers = iter(["n", "", ""])
    confirm = a.TableConfirmation(ask=lambda prompt: next(answers))
    assert confirm("warehouse__run_query", {"sql": "SELECT * FROM orders"}) is False
    assert confirm("warehouse__run_query", {"sql": "SELECT * FROM orders o JOIN customers c ON 1"}) is True
    assert confirm("warehouse__run_query", {"sql": "SELECT * FROM customers"}) is True   # already approved

# ---------------- capstone 3: incident triage
def test_c3_triage(ws, model):
    sys.path.insert(0, str(CAP / "c3_incident")); sys.modules.pop("data", None)
    import data as d3
    sha = d3.build()
    sys.path.remove(str(CAP / "c3_incident")); sys.modules.pop("data", None)
    a = _load("c3_incident/agent.py")
    names, r = call_all(a.CONFIG, [
        ("obs__compare_to_baseline", {"service": "checkout-service", "metric": "p95_ms",
                                      "baseline_start": "2026-09-22T13:00", "baseline_end": "2026-09-22T14:00",
                                      "window_start": "2026-09-22T14:00", "window_end": "2026-09-22T15:00"}),
        ("obs__search_logs", {"service": "checkout-service", "start": "2026-09-22T14:00",
                              "end": "2026-09-22T14:30", "pattern": "ERROR"}),
        ("git__git_log", {"repo_path": "incident/repo", "max_count": 3})])
    stats = json.loads(r[0][0])
    assert stats["ratio"] > 2 and stats["first_minute_over_2x"] == "2026-09-22T14:05"
    assert "fraud-check timeout" in r[1][0]
    assert sha in r[2][0] and "synchronous" in r[2][0]
    model.reset([[tool("obs__compare_to_baseline", {"service": "checkout-service", "metric": "p95_ms",
                   "baseline_start": "2026-09-22T13:00", "baseline_end": "2026-09-22T14:00",
                   "window_start": "2026-09-22T14:00", "window_end": "2026-09-22T15:00"})],
                 [tool("git__git_log", {"repo_path": "incident/repo", "max_count": 3})],
                 [text("The 14:05 deploy made the fraud check synchronous.")],
                 [tool("triage_report", {"impact": "checkout p95 2.6x", "timeline": ["14:04 commit", "14:05 spike"],
                                         "suspected_cause": "synchronous fraud check", "suspect_commit": sha,
                                         "evidence": ["p95 ratio"], "next_steps": ["roll back"]})]])
    report = asyncio.run(a.triage(a.ALERT))
    assert report["suspect_commit"] == sha
    assert "git__git_commit" not in [t["name"] for t in model.calls[0]["tools"]]

# ---------------- capstone 4: code review
def test_c4_review(ws, model):
    sys.path.insert(0, str(CAP / "c4_review")); sys.modules.pop("data", None)
    import data as d5
    d5.build()
    sys.path.remove(str(CAP / "c4_review")); sys.modules.pop("data", None)
    a = _load("c4_review/agent.py")
    names, r = call_all(a.CONFIG, [
        ("repo__list_prs", {}), ("repo__run_tests", {"branch": "pr-1"}), ("repo__run_tests", {"branch": "pr-2"}),
        ("repo__get_pr_diff", {"branch": "pr-3"}),
        ("repo__propose_fix", {"branch": "pr-1", "path": "test_cart.py", "old": "a", "new": "b", "message": "x"}),
        ("repo__propose_fix", {"branch": "pr-1", "path": "cart.py", "old": "items[-n - 1:]",
                               "new": "items[-n:]", "message": "fix off-by-one"})])
    assert r[0][0].count("pr-") == 3
    assert "1 failed" in r[1][0] and "passed" in r[2][0] and "failed" not in r[2][0]
    assert "-def test_last_items" in r[3][0]
    assert r[4][1] and "not allowed" in r[4][0]
    assert "Committed on fix/pr-1" in r[5][0] and "2 passed" in r[5][0]
    model.reset([[tool("repo__get_pr_diff", {"branch": "pr-3"})], [text("A test was deleted.")],
                 [tool("submit_review", {"verdict": "request_changes", "tests_passed": True,
                   "findings": [{"file": "test_cart.py", "line": 5, "severity": "tests",
                                 "comment": "test_last_items was deleted"}]})]])
    review = asyncio.run(a.review("pr-3", approver=lambda n, a_: False))
    assert review["verdict"] == "request_changes" and review["findings"][0]["severity"] == "tests"

# ---------------- capstone 5: deep research
def test_c5_research(ws, model):
    r6 = _load("c5_research/research.py")
    def respond(kw):
        forced = (kw.get("tool_choice") or {}).get("name")
        if forced == "make_plan":
            return [tool("make_plan", {"subtasks": [
                {"objective": "freshness of RAG", "out_of_scope": "cost", "effort": "quick"},
                {"objective": "cost of agents", "out_of_scope": "freshness", "effort": "quick"}]})]
        if forced == "review":
            return [tool("review", {"unsupported_claims": []})]
        if "tools" in kw:                                          # a subagent
            if len(kw["messages"]) == 1:
                return [tool("library__search_docs", {"pattern": "re-index|tokens"})]
            return [text("- RAG indexes need re-indexing when documents change (rag-overview.md:2)")]
        if last_user_text(kw).startswith("Revise"):
            return [text("## Summary\nRevised (rag-overview.md:2).")]
        return [text("## Summary\nIndexes need re-indexing when documents change (rag-overview.md:2). "
                     "Also (rag-overview.md:99).")]
    model.reset(default=respond)
    result = asyncio.run(r6.research("How fresh are RAG indexes and what do agents cost?"))
    assert [c["citation"] for c in result["bad_citations"]] == ["rag-overview.md:99"]
    assert result["brief"].startswith("## Summary\nRevised")
    assert Path("research_memory.jsonl").exists()                  # stored in the memory server
