"""Chapter 15: MCP in 2026. Offline."""
import asyncio
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from fakemodel import text, tool, tool_results

def test_15_modern_describe(ws):
    import ch15_modern as m
    m.CountingServer.list_requests = 0
    report = asyncio.run(m.describe(m.catalog))
    assert report["protocol"] == "2026-07-28" and report["ttl_ms"] == 300_000
    assert report["cache_scope"] == "public" and report["same_answer"]
    assert m.CountingServer.list_requests == 1          # the second list was cached

def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def test_15_3_wire(ws, tmp_path):
    port = _free_port()
    launcher = tmp_path / "run.py"
    launcher.write_text("import ch15_modern as m\nm.catalog.run(transport="
                        f"'streamable-http', host='127.0.0.1', port={port})\n")
    proc = subprocess.Popen([sys.executable, str(launcher)], cwd=os.getcwd(),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
                break
            except OSError:
                time.sleep(0.2)
        import ex15_3_wire as ex
        found = ex.main(f"http://127.0.0.1:{port}/mcp")
    finally:
        proc.terminate()
        proc.wait(timeout=10)
    assert "2026-07-28" in found["discover"]["supportedVersions"]
    assert found["tools"]["ttlMs"] == 300_000
    assert found["call"]["structuredContent"] == {"result": 120.0}
    assert "does not match" in found["mismatch"]["message"]

def test_15_4_cache(ws):
    import ex15_4_cache as ex
    r = asyncio.run(ex.main())
    assert list(r.values()) == [1, 10, 10]

def test_15_gateway(ws):
    import ch30_gateway as g, ch26_identity as identity
    g.AUDIT.unlink(missing_ok=True)
    gw = g.Gateway(g.UPSTREAMS, g.POLICY)
    planner = identity.mint("planner-agent", "ana", {"todo:read", "todo:write"},
                            g.AUDIENCE)
    analyst = identity.mint("analyst-agent", "ana", {"shop:read"}, g.AUDIENCE)
    ok = asyncio.run(g.call(gw, planner, "todo__add_task", {"title": "Gateway test"}))
    denied = asyncio.run(g.call(gw, analyst, "todo__add_task", {"title": "x"}))
    unknown = asyncio.run(g.call(gw, planner, "todo__drop", {}))
    rows = asyncio.run(g.call(gw, analyst, "shopdb__run_query",
                              {"query": "SELECT COUNT(*) AS n FROM orders"}))
    assert "Gateway test" in ok and "lacks todo:write" in denied
    assert "no tool called" in unknown and rows.startswith("n")
    audit = [json.loads(l) for l in g.AUDIT.read_text().splitlines()]
    assert [a["outcome"][:6] for a in audit] == ["ok", "denied", "denied", "ok"]
    assert audit[1]["agent"] == "agent:analyst-agent"

def test_30_gateway_rate_limit(ws, monkeypatch):
    import ch30_gateway as g, ch26_identity as identity
    monkeypatch.setitem(g.RATE, "calls", 2)
    gw = g.Gateway(g.UPSTREAMS, g.POLICY)
    t = identity.mint("planner-agent", "ana", {"todo:read"}, g.AUDIENCE)
    out = [asyncio.run(g.call(gw, t, "todo__list_tasks", {})) for _ in range(3)]
    assert "rate limit" in out[2] and "rate limit" not in out[1]

def test_30_9_scoped_search(ws):
    import ex30_9_scoped_search as ex
    found = asyncio.run(ex.main())
    assert found["reader, 'task'"] == ["todo__list_tasks", "todo__find_tasks"]
    assert found["analyst, 'task'"] == [] and found["no token, 'task'"] == []
    assert set(found["analyst, 'query schema'"]) == {"shopdb__get_schema",
                                                     "shopdb__run_query"}

def test_30_jobs_server(ws):
    import ch30_jobs_server as j
    asyncio.run(j.main())
    with j.durable._db() as con:
        assert con.execute("SELECT status FROM jobs").fetchone()["status"] == "done"

def test_30_jobs_rejects_bad_month(ws):
    from mcp import Client
    import ch30_jobs_server as j
    async def go():
        async with Client(j.mcp) as c:
            return await c.call_tool("start_report", {"month": "2026' OR 1=1 --"})
    assert asyncio.run(go()).is_error

def test_30_10_jobs(ws):
    import ex30_10_jobs as ex
    r = asyncio.run(ex.main())
    assert r["long poll"]["polls"] == 1 and r["short polls"]["polls"] >= 2
    assert all(v["status"] == "completed" and v["retry_same_job"] for v in r.values())

def test_30_11_gateway_agent(model, ws):
    import ex30_11_gateway_agent as ex
    model.reset([[tool("company__search_tools", {"query": "task"})],
                 [tool("company__use_tool", {"name": "todo__add_task",
                                             "arguments": {"title": "Book flights",
                                                           "due": "2026-10-02"}})],
                 [tool("company__use_tool", {"name": "shopdb__run_query",
                                             "arguments": {"query": "SELECT 1"}})],
                 [text("Added the task. I'm not allowed to query orders.")]])
    answer, audit = asyncio.run(ex.main())
    assert [a["tool"] for a in audit] == ["todo__add_task", "shopdb__run_query"]
    assert audit[0]["outcome"] == "ok" and audit[1]["outcome"].startswith("denied")
    assert "todo__add_task" in model.calls[1]["messages"][2]["content"][0]["content"]
