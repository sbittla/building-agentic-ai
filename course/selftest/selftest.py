"""Offline self-test of the course image. Needs no API key and no network.

It copies the original course files to a temporary folder, generates the sample
data, and exercises every chapter's tools, agent loops (with a scripted stand-in
for the model), MCP servers, reference servers and the MCP Inspector CLI.
"""
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).parent
results = []

def check(name):
    def deco(fn):
        t0 = time.perf_counter()
        try:
            detail = fn() or ""
            results.append((True, name, detail, time.perf_counter() - t0))
        except Exception as exc:
            tb = traceback.format_exc(limit=2).strip().splitlines()[-1]
            results.append((False, name, f"{type(exc).__name__}: {exc} | {tb}"[:300],
                            time.perf_counter() - t0))
        return fn
    return deco

tmp = Path(tempfile.mkdtemp(prefix="selftest-"))
shutil.copytree("/opt/course/code", tmp, dirs_exist_ok=True)
shutil.copy(HERE / "fakellm.py", tmp)
os.chdir(tmp)
sys.path[:0] = [str(tmp), "/opt/course/data"]
os.environ["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY") or "sk-selftest-dummy"
print(f"Self-test in {tmp}\n", file=sys.stderr)

import generate
from fakellm import Fake, AFake, tool, text

@check("sample data generates")
def _():
    generate.all_data(tmp)
    assert (tmp / "shop.db").exists() and (tmp / "buggy_repo" / "pricing.py").exists()
    return f"{len(list((tmp / 'notes').rglob('*.md')))} notes, library, messy, shop.db, buggy_repo"

@check("ch02 calculator round-trip")
def _():
    import ch02_calculator_agent as c2
    assert c2.calculate("0.175*84213") == "14737.275"
    try:
        c2.calculate("__import__('os')")
        raise AssertionError("unsafe expression accepted")
    except ValueError:
        pass
    c2.client = Fake([[tool("calculate", {"expression": "0.175*84213"})], [text("14,737.28")]])
    return c2.ask("What is 17.5% of 84,213?")

@check("ch03 tools and registry")
def _():
    import ch03_tools as t3
    assert "42.1648 km" in t3.run_tool("convert_units", {"value": 26.2, "from_unit": "mi", "to_unit": "km"})
    assert t3.run_tool("nope", {}).startswith("ERROR")
    return t3.run_tool("days_between", {"start": "2026-09-23", "end": "2027-07-04"})

@check("ch04 agent loop: chaining, parallel calls, cap, should_stop")
def _():
    import ch03_tools as t3, ch04_agent as a4
    a4._client = Fake([[tool("get_current_date", {})],
                       [tool("days_between", {"start": "2026-09-23", "end": "2027-07-04"}),
                        tool("convert_units", {"value": 10, "from_unit": "mi", "to_unit": "km"})],
                       [text("284 days")]])
    ans, _, st = a4.run_agent("q", t3.TOOLS, t3.run_tool, verbose=False)
    assert ans == "284 days" and st["tool_calls"] == 3
    a4._client = Fake([[tool("get_current_date", {})]] * 3)
    assert "max_iterations" in a4.run_agent("q", t3.TOOLS, t3.run_tool, max_iterations=2, verbose=False)[0]
    a4._client = Fake([[tool("get_current_date", {})]] * 3)
    assert "budget" in a4.run_agent("q", t3.TOOLS, t3.run_tool, verbose=False,
                                    should_stop=lambda s: "budget")[0]
    return f"steps={st['steps']} tool_calls={st['tool_calls']}"

@check("ch05 to-do tools (idempotent, persistent)")
def _():
    import ch05_todo_tools as t5
    t5.add_task("Buy milk", "2026-09-25", "high"); t5.add_task("buy milk")
    assert t5.list_tasks().count("Buy milk") == 1
    assert t5.complete_task(1).startswith("Completed")
    return t5.list_tasks(include_done=True).splitlines()[0]

@check("ch06 notes tools + sandbox")
def _():
    import ch06_notes_tools as t6
    assert "kafka" in t6.search_files("kafka").lower()
    assert t6.run_tool("read_file", {"path": "../shop.db"}).startswith("ERROR")
    return t6.search_files("consumer lag").splitlines()[0][:70]

@check("ch07 weather tools (mocked HTTP: retry + cache)")
def _():
    import httpx, ch07_weather_tools as w
    class R:
        def __init__(s, code, data): s.status_code, s._d, s.request = code, data, None
        def json(s): return s._d
        def raise_for_status(s):
            if s.status_code >= 400:
                raise httpx.HTTPStatusError("x", request=None, response=s)
    calls = []
    def fake_get(url, params, timeout):
        calls.append(url)
        if "geocoding" in url:
            return R(200, {"results": [{"name": "Pune", "country": "India", "latitude": 18.5, "longitude": 73.9}]})
        if len(calls) < 3:
            return R(503, {})
        return R(200, {"daily": {"time": ["2026-09-24"], "temperature_2m_min": [21],
                                 "temperature_2m_max": [29], "precipitation_probability_max": [70]}})
    real_get, real_sleep = httpx.get, w.time.sleep
    httpx.get, w.time.sleep = fake_get, (lambda s: None)
    try:
        assert "Pune" in w.geocode("Pune")
        out = w.get_forecast(18.5, 73.9); w.get_forecast(18.5, 73.9)
        assert w.stats["cache_hits"] >= 1
    finally:
        httpx.get, w.time.sleep = real_get, real_sleep
    return out

@check("ch08 SQL tools: read-only, self-correction errors")
def _():
    import ch08_sql_tools as s8
    top = s8.run_query("SELECT c.name, SUM(oi.quantity*p.price) r FROM customers c JOIN orders o "
                       "ON o.customer_id=c.id JOIN order_items oi ON oi.order_id=o.id JOIN products p "
                       "ON p.id=oi.product_id WHERE o.status!='cancelled' GROUP BY c.id ORDER BY r DESC LIMIT 1")
    assert "Customer 13" in top
    assert "readonly" in s8.run_query("WITH x AS (SELECT 1) DELETE FROM orders")
    assert "no such table" in s8.run_query("SELECT * FROM custmers")
    return top.splitlines()[1]

@check("ch09 organizer: approval gate, collisions, undo")
def _():
    import builtins, ch09_organizer as o
    real_input = builtins.input
    try:
        o.propose_moves()
        builtins.input = lambda p: "n"
        assert o.run_tool("apply_plan", {"plan_id": "plan-1"}).startswith("DECLINED")
        builtins.input = lambda p: "y"
        assert "Moved" in o.run_tool("apply_plan", {"plan_id": "plan-1"})
        assert "Restored" in o.run_tool("undo_plan", {"plan_id": "plan-1"})
    finally:
        builtins.input = real_input
    return "declined, applied and undone"

@check("ch10 fixer tools: tests run, test edits blocked")
def _():
    import ch10_fixer as f
    out = f.run_tests()
    assert "3 failed" in out, out[-300:]
    assert f.write_file("test_pricing.py", "x").startswith("ERROR")
    return "3 failing tests detected; test files protected"

@check("ch11 research team (async, scripted model)")
def _():
    import ch11_research_team as r
    r.client = AFake([[tool("make_plan", {"subtasks": ["cost", "freshness"]})],
                      [tool("search_files", {"pattern": "index"})], [text("- A (x.md:1)")],
                      [text("- B")], [text("final answer")]])
    return asyncio.run(r.research("compare"))

@check("ch12-13 MCP servers via the hub (todo, shopdb, weather)")
def _():
    import ch13_mcp_agent as m
    cfg = {"servers": {"todo": {"command": sys.executable, "args": ["ch13_todo_server.py"]},
                       "shopdb": {"command": sys.executable, "args": ["ch13_sql_server.py"]},
                       "weather": {"command": sys.executable, "args": ["ch12_weather_server.py"]}}}
    fake = AFake([[tool("todo__add_task", {"title": "Test MCP"})],
                  [tool("shopdb__run_query", {"query": "SELECT nope"})], [text("done")]])
    m.AsyncAnthropic = lambda: fake
    async def go():
        async with m.MCPHub(cfg) as hub:
            names = [t["name"] for t in hub.tools]
            assert "weather__geocode" in names and "shopdb__run_query" in names
            ans, msgs = await m.run_mcp_agent(hub, "q")
            assert msgs[4]["content"][0]["is_error"] is True
            res = await hub.clients["weather"].read_resource("weather://favorites")
            return f"{len(names)} tools; resource: {res.contents[0].text.splitlines()[0]}"
    return asyncio.run(go())

@check("ch14 reference servers start and list tools (fs, git, fetch, time)")
def _():
    subprocess.run(["git", "init", "-q"], cwd=tmp)
    import ch13_mcp_agent as m
    from ch14_policy_agent import Policy
    cfg = json.load(open("servers_ecosystem.json"))
    async def go():
        async with m.MCPHub(cfg) as hub:
            visible = Policy("policy.json", "tool_calls.jsonl").visible_tools(hub.tools)
            text_, err = await hub.call("fs__read_text_file", {"path": "/etc/passwd"})
            assert err, "filesystem server allowed a path outside ./notes"
            return f"{len(hub.tools)} tools, {len(visible)} allowed by policy"
    return asyncio.run(go())

@check("GitHub MCP server binary")
def _():
    exe = shutil.which("github-mcp-server")
    assert exe, "github-mcp-server not on PATH"
    r = subprocess.run([exe, "--help"], capture_output=True, text=True, timeout=30)
    if "not included" in r.stderr:
        return "skipped: image built with GITHUB_MCP_IMAGE=nogithub"
    assert r.returncode == 0, r.stderr[:200]
    return "present"

@check("MCP Inspector CLI lists weather tools")
def _():
    r = subprocess.run(["mcp-inspector", "--cli", sys.executable, "ch12_weather_server.py",
                        "--method", "tools/list"], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0 and "get_forecast" in r.stdout, (r.stdout + r.stderr)[-300:]
    return "tools/list OK"

@check("ch15 eval checks and load-test math")
def _():
    from types import SimpleNamespace as S
    import ch15_eval as e, ch15_loadtest as lt
    msgs = [{"role": "assistant", "content": [S(type="tool_use", name="run_query")]}]
    assert e.check({"must_contain": ["400"], "must_use_tools": ["run_query"]}, "400 orders", msgs) == []
    assert lt.pct([1, 2, 3, 4, 100], 95) == 100
    return "checks OK"

@check("ch00 and interludes: JSON schema check, pricing tests, SQL, async")
def _():
    import ch00_json, i_pricing
    assert ch00_json.check({"days": 40}, ch00_json.schema) != []
    assert i_pricing.apply_discount(200, 10) == 180
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                        "test_i_pricing.py"], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout[-300:]
    r = subprocess.run([sys.executable, "i_sql.py"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and "revenue" in r.stdout, r.stderr[-300:]
    return "pytest, SQL and JSON OK"

@check("ch16 context: trim, compact, caching marks; FTS5 memory")
def _():
    import ch16_context as c, ch16_memory as m, ch06_notes_tools as notes
    c._client = Fake([[tool("search_files", {"pattern": "Kafka"})], [text("Summary.")],
                      [text("done")]])
    big = [{"role": "user", "content": "q"}] + [x for k in range(3) for x in (
        {"role": "assistant", "content": [tool("read_file", {"path": "x"})]},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": f"t{k}", "content": "z" * 2000}]})]
    assert c.estimate_tokens(c.trim_old_tool_results(big, keep_last=1)) < c.estimate_tokens(big)
    system, tools = c.with_cache("sys", notes.TOOLS)
    assert "cache_control" in tools[-1] and "cache_control" in system[0]
    m.DB = Path("selftest_memory.db")
    m.remember("Srini prefers Celsius")
    assert "Celsius" in m.recall("prefer")
    return "trim/cache/memory OK"

@check("ch17 RAG: chunks, BM25 + vectors, hybrid, eval")
def _():
    import ch17_rag as rag
    index = rag.build(embedder=rag.HashingEmbedder())
    assert index.search("ERR-4471", k=1, mode="keyword")[0]["source"] == "library/error-codes.md"
    report = rag.evaluate(index)
    local = "local model cached" if any(Path(os.environ.get("HF_HOME", "/opt/hf")).glob(
        "hub/models--minishlab--potion-base-8M")) else "local model NOT downloaded (hashing fallback)"
    return f"{len(index.chunks)} chunks, hybrid recall@3={report['hybrid']['recall@k']}; {local}"

@check("ch18 frameworks import (tool runner, Agent SDK, LangChain)")
def _():
    import ch18_tool_runner, ch18_agent_sdk, ch18_langchain  # noqa: F401
    from importlib.metadata import version
    return " ".join(f"{p}={version(p)}" for p in ("claude-agent-sdk", "langchain", "langgraph"))

@check("ch19 agent API: auth, rate limit, private sessions")
def _():
    import ch19_service as s, ch04_agent as a4
    from fastapi.testclient import TestClient
    s.API_KEYS, s.RATE_PER_MINUTE, s.DB = ["k"], 2, "selftest_sessions.db"
    a4._client = Fake([[text("400")]] * 3)
    c = TestClient(s.app)
    h = {"Authorization": "Bearer k"}
    assert c.post("/v1/chat", json={"message": "hi"}).status_code == 401
    codes = [c.post("/v1/chat", json={"message": "hi"}, headers=h).status_code for _ in range(3)]
    assert codes == [200, 200, 429], codes
    return "401 / 200 / 429 OK"

@check("ch19 remote MCP server: bearer token enforced")
def _():
    import ch19_remote_mcp as rm
    from starlette.testclient import TestClient
    with TestClient(rm.build_app(token="t")) as c:       # "with" runs the app's startup
        assert c.post("/mcp", json={}).status_code == 401
        assert c.post("/mcp", json={}, headers={"Authorization": "Bearer t"}).status_code != 401
    return "token OK"

# ---------------------------------------------------------------- report
print("", file=sys.stderr)
passed = sum(r[0] for r in results)
for good, name, detail, secs in results:
    mark = "\033[32mPASS\033[0m" if good else "\033[31mFAIL\033[0m"
    print(f"{mark}  {name:<62} {secs:5.1f}s  {detail}", file=sys.stderr)
print(f"\n{passed}/{len(results)} checks passed.", file=sys.stderr)
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(0 if passed == len(results) else 1)
