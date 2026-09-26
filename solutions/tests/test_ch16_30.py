"""Part 6 (chapters 16-19): reference solutions and course code, fully offline.

The Agent SDK and the tool runner talk to a local fake of the Messages API
(fake_messages_api.py); everything else uses the scripted stand-in model."""
import asyncio
import importlib
import json
import os
import re
import socket
import sqlite3
import sys
import threading
import time
from types import SimpleNamespace as S
import httpx
import pytest
import uvicorn
from fakemodel import MODEL, last_user_text, text, tool, tool_results

# get_schema (and list_tasks) are auto-approved on purpose; the SDK warns about that.
pytestmark = pytest.mark.filterwarnings("ignore:can_use_tool will not be invoked")

def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def serve(app, port):
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", port), 0.2).close()
            return server
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("server did not start")

# ================================================================ chapter 16
def test_16_trim_keeps_pairs_and_compact_summarizes(model):
    import ch16_context as c
    msgs = [{"role": "user", "content": "q1"}]
    for k in range(4):
        msgs += [{"role": "assistant", "content": [S(type="tool_use", id=f"t{k}", name="x", input={})]},
                 {"role": "user", "content": [{"type": "tool_result", "tool_use_id": f"t{k}",
                                               "content": "y" * 1000}]}]
    msgs += [{"role": "assistant", "content": [S(type="text", text="a1")]},
             {"role": "user", "content": "q2"}]
    trimmed = c.trim_old_tool_results(msgs)
    sizes = [len(m["content"][0]["content"]) for m in trimmed
             if m["role"] == "user" and isinstance(m["content"], list)]
    assert sizes[:2] == [sizes[0]] * 2 and sizes[0] < 400 and sizes[2:] == [1000, 1000]
    assert c.estimate_tokens(trimmed) < c.estimate_tokens(msgs)
    model.reset(default=[text("SUMMARY: user asked q1")])
    kept, summary = c.compact(msgs, keep_last_turns=1)
    assert summary.startswith("SUMMARY") and kept[0]["content"].startswith("[Summary")
    assert kept[-1] == {"role": "user", "content": "q2"}

def test_16_3_managed_agent_compacts_under_budget(model):
    import ch16_context as c, ch06_notes_tools as notes
    def policy(kw):
        if kw.get("tools") is None:                 # the compaction call
            return [text("Summary: Kafka lag was caused by fewer consumers.")]
        if kw["messages"][-1]["role"] == "user" and isinstance(kw["messages"][-1]["content"], str):
            return [tool("search_files", {"pattern": "Kafka"})]
        return [text("Answer based on the notes.")]
    model.reset(default=policy)
    history, total = [], {"trims": 0, "compactions": 0}
    for q in ["Which notes mention Kafka?", "Root cause?", "And the follow-up?"]:
        answer, history, stats = c.run_managed_agent(q, notes.TOOLS, notes.run_tool,
                                                     system=notes.SYSTEM, messages=history,
                                                     budget_tokens=400, verbose=False)
        total["trims"] += stats["trims"]; total["compactions"] += stats["compactions"]
    assert total["compactions"] >= 1 and answer
    # every request the model saw had its system prompt and tools marked for caching
    req = [k for k in model.calls if k.get("tools")][0]
    assert req["cache_control"] == {"type": "ephemeral"}          # automatic caching (default)
    kw = c.cache_kwargs("sys", notes.TOOLS, "prefix")
    assert kw["system"][0]["cache_control"] == {"type": "ephemeral"} and "cache_control" in kw["tools"][-1]
    assert "cache_control" not in c.cache_kwargs("sys", notes.TOOLS, "off")

def test_17_3_memory_survives_restart(ws):
    import ch17_memory as m
    m.DB = ws / "memory_test.db"
    assert m.remember("Srini prefers Celsius", "preferences").startswith("Remembered")
    assert m.remember("Srini prefers Celsius").startswith("Already")
    m.remember("Srini's manager is Asha")
    m = importlib.reload(m)                                   # a "restart"
    m.DB = ws / "memory_test.db"
    hits = json.loads(m.recall("what do I prefer?"))          # porter: prefer ~ prefers
    assert hits[0]["fact"] == "Srini prefers Celsius"
    assert m.forget(hits[0]["id"]).startswith("Forgot")
    assert "Celsius" not in m.recall("prefer Celsius")
    assert "Asha" in m.recall("manager")
    m.DB = ws / "memory.db"

def test_16_5_cache_savings(model, monkeypatch):
    import ex16_5_cache_savings as ex
    orig = model.respond
    seen = {"prefix": False, "auto": False}
    def respond(kw):
        r = orig(kw)
        n = sum(len(str(m["content"])) for m in kw["messages"]) // 4      # history size
        if "cache_control" in kw:                     # auto: history is cached too
            first = not seen["auto"]; seen["auto"] = True
            r.usage = S(input_tokens=50, output_tokens=40,
                        cache_creation_input_tokens=3000 + n if first else 60,
                        cache_read_input_tokens=0 if first else 3000 + n)
        elif isinstance(kw.get("system"), list):      # prefix only
            first = not seen["prefix"]; seen["prefix"] = True
            r.usage = S(input_tokens=200 + n, output_tokens=40,
                        cache_creation_input_tokens=3000 if first else 0,
                        cache_read_input_tokens=0 if first else 3000)
        else:
            r.usage = S(input_tokens=3200 + n, output_tokens=40)
        return r
    monkeypatch.setattr(model, "respond", respond)
    model.reset(default=[text("42")])
    rows = ex.main()
    assert rows["off"]["cache_read"] == 0
    assert rows["auto"]["cost"] < rows["prefix"]["cost"] < rows["off"]["cost"]
    assert all(r["calls"] == 5 for r in rows.values())

def test_17_8_assistant_twenty_turns(model, ws):
    import ch05_todo_tools as todo, ch17_memory_policy as mem
    import ex17_8_assistant as ex
    old_db = mem.DB
    todo.STORE, mem.DB = ws / "tasks_17_8.json", ws / "memory_17_8.db"
    def policy(kw):
        if kw.get("tools") is None:
            return [text("Summary of earlier turns.")]
        last = kw["messages"][-1]
        q = last_user_text(kw)
        if last["role"] == "user" and isinstance(last["content"], str):
            if "prefer" in q.lower() or "remember that" in q.lower():
                subject = "manager" if "manager" in q else "preferences"
                return [tool("remember", {"text": q, "subject": subject})]
            if q.startswith("Add"):
                return [tool("add_task", {"title": q.split("'")[1]})]
            if "know" in q or "manager" in q:
                return [tool("recall", {"query": "preferences manager"})]
        return [text(f"Done. ({tool_results(kw)[:1]})")]
    model.reset(default=policy)
    transcript, totals = ex.main(budget_tokens=600)
    assert sum(line.startswith("[") for line in transcript) == 20
    assert totals["compactions"] >= 1
    assert "Asha" in mem.recall("manager")                         # survived the restart
    after_restart = "\n".join(transcript[transcript.index("---- restart: new session, empty history ----"):])
    assert "Asha" in after_restart or "prefer" in after_restart
    assert "quarterly review with Asha" in todo.STORE.read_text()
    todo.STORE, mem.DB = ws / "tasks.json", old_db

# ================================================================ chapter 18
@pytest.fixture
def hashing(monkeypatch):
    monkeypatch.setenv("EMBEDDER", "hashing")
    import ch18_rag
    return ch18_rag.HashingEmbedder()

def test_18_index_search_and_eval(ws, hashing):
    import ch18_rag as rag
    index = rag.build(embedder=hashing)
    assert len(index.chunks) >= 30
    assert all("source" in c and "line" in c for c in index.chunks)
    top = index.search("ERR-4471", k=1, mode="keyword")[0]
    assert top["source"] == "library/error-codes.md"
    report = rag.evaluate(index)
    assert set(report) == {"keyword", "vector", "hybrid"} and report["keyword"]["recall@k"] >= 0.75
    out = rag.search_knowledge("consumer lag")
    assert re.search(r"\(notes/work/2026-06-02-incident-kafka-lag\.md:\d+\)", out)
    index.save(str(ws / "idx"))
    again = rag.Index.load(str(ws / "idx"), embedder=hashing)
    assert again.search("vacuum bloat", k=1)[0]["source"] == index.search("vacuum bloat", k=1)[0]["source"]

def test_18_5_paraphrased(ws, hashing, capsys):
    import ex18_5_paraphrased as ex
    report = ex.main(embedder=hashing)
    assert len(ex.PARAPHRASED) == 8
    assert set(report) == {"keyword", "vector", "hybrid"}
    assert "paraphrased questions (8)" in capsys.readouterr().out

class ConceptEmbedder:
    """A stand-in for a semantic model: words with the same meaning share a dimension."""
    name, dims = "concept", 8
    CONCEPTS = {0: {"temperature", "celsius", "units", "degrees"}, 1: {"boss", "manager"},
                2: {"exercise", "runs", "km", "routine"}, 3: {"err-4471", "payments", "error"}}
    def embed(self, texts, input_type="document"):
        import numpy as np
        out = np.full((len(texts), self.dims), 0.01, dtype=np.float32)
        for i, t in enumerate(texts):
            words = set(re.findall(r"[\w-]+", t.lower()))
            for d, ws_ in self.CONCEPTS.items():
                out[i, d] += len(words & ws_)
        return out / np.linalg.norm(out, axis=1, keepdims=True)

def test_18_6_knowledge_agent(model, ws, hashing):
    import ex18_6_knowledge_agent as ex
    unanswerable = {q for q, must in ex.CASES if not must}
    def policy(kw):
        q = last_user_text(kw)
        if kw["messages"][-1]["role"] == "user" and isinstance(kw["messages"][-1]["content"], str):
            return [tool("search_knowledge", {"query": q})]
        if q in unanswerable:
            return [text("Not in the knowledge base.")]
        passage = tool_results(kw)[0].split("\n\n")[0]           # the best passage
        cite, body = passage.split("\n", 1)
        return [text(f"{body.splitlines()[-1]} {cite}")]
    model.reset(default=policy)
    rows, summary = ex.main()
    assert summary["correct_refusals"] == "3/3"
    valid, total = map(int, summary["citation_validity"].split("/"))
    assert total >= 7 and valid >= total - 1

# ================================================================ chapter 24
@pytest.fixture
def fake_api(monkeypatch):
    from fake_messages_api import FakeAPI
    apis = []
    def make(script):
        api = FakeAPI(script, free_port()).start()
        apis.append(api)
        monkeypatch.setenv("ANTHROPIC_BASE_URL", f"http://127.0.0.1:{api.port}")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-offline")
        monkeypatch.setenv("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC", "1")
        return api
    yield make
    for a in apis:
        a.stop()

def _real_client(api):
    from anthropic._client import Anthropic          # the real class (conftest replaced the alias)
    return Anthropic(api_key="sk-test-offline", base_url=f"http://127.0.0.1:{api.port}")

def test_24_2_tool_runner_is_the_loop(fake_api):
    import ch24_tool_runner as tr
    api = fake_api([[{"tool": "get_current_date"}],
                    [{"tool": "days_between", "input": {"start": "2026-09-24", "end": "2027-07-04"}}],
                    [{"text": "283 days; a Sunday."}]])
    assert tr.ask("Days until July 4?", client=_real_client(api)) == "283 days; a Sunday."
    results = [b for b in api.requests[2]["messages"][-1]["content"] if b["type"] == "tool_result"]
    assert "2027-07-04 is a Sunday" in json.dumps(results)

def test_24_3_agent_sdk_approval_gate(fake_api, ws):
    import ch24_agent_sdk as sdk
    api = fake_api([[{"tool": "mcp__shop__run_query", "input": {"sql": "DELETE FROM orders WHERE status='cancelled'"}}],
                    [{"tool": "mcp__shop__run_query", "input": {"sql": "SELECT COUNT(*) FROM orders WHERE status='cancelled'"}}],
                    [{"text": "I can't delete orders; there are cancelled orders, unchanged."}]])
    before = sqlite3.connect("shop.db").execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    sdk.decisions.clear()
    answer = asyncio.run(sdk.ask("Delete all cancelled orders."))
    assert "can't delete" in answer
    assert sdk.decisions == [("mcp__shop__run_query", "deny"), ("mcp__shop__run_query", "allow")]
    assert sqlite3.connect("shop.db").execute("SELECT COUNT(*) FROM orders").fetchone()[0] == before
    offered = {t["name"] for r in api.requests if r.get("tools") for t in r["tools"]}
    assert offered == {"mcp__shop__get_schema", "mcp__shop__run_query"}   # isolation: nothing else

def test_24_4_sdk_with_stdio_server(fake_api, ws):
    import ex24_4_sdk_mcp as ex
    fake_api([[{"tool": "mcp__todo__list_tasks"}],
              [{"tool": "mcp__todo__add_task", "input": {"title": "review electronics pricing", "due": "2026-10-15"}}],
              [{"tool": "mcp__todo__add_task", "input": {"title": "declined task"}}],
              [{"text": "Added the review task."}]])
    answers = iter([True, False])
    ex.APPROVER = lambda name, args: next(answers)
    ex.decisions.clear()
    asyncio.run(ex.ask("Add a pricing review to-do.", python=sys.executable))
    assert ex.decisions == [("mcp__todo__add_task", "allow"), ("mcp__todo__add_task", "deny")]
    tasks = (ws / "tasks.json").read_text()
    assert "review electronics pricing" in tasks and "declined task" not in tasks

def _scripted_chat(responses):
    from langchain_core.language_models import BaseChatModel
    from langchain_core.outputs import ChatGeneration, ChatResult
    class ScriptedChat(BaseChatModel):
        responses: list
        @property
        def _llm_type(self):
            return "scripted"
        def _generate(self, messages, stop=None, run_manager=None, **kw):
            return ChatResult(generations=[ChatGeneration(message=self.responses.pop(0))])
        def bind_tools(self, tools, **kw):
            return self
    return ScriptedChat(responses=list(responses))

def test_24_3_langchain_agent(ws):
    from langchain_core.messages import AIMessage
    import ch24_langchain as lc
    model = _scripted_chat([AIMessage(content="", tool_calls=[{"name": "add_task", "id": "c1",
                            "args": {"title": "renew passport", "due": "2026-11-01"}}]),
                            AIMessage(content="Added 'renew passport'.")])
    answer, history = lc.ask(lc.build(model), "Add 'renew passport' due 2026-11-01.")
    assert "renew passport" in (ws / "tasks.json").read_text() and "Added" in answer

def test_24_5_compare_harness(model):
    import ex24_5_three_ways as ex
    cases = [{"id": "count", "question": "How many orders?", "must_match": [r"\b400\b"],
              "must_use_tools": ["run_query"]}]
    good = lambda q: ("There are 400 orders.", ["get_schema", "run_query"], 1200)
    bad = lambda q: ("Lots.", [], 300)
    def broken(q):
        raise RuntimeError("model down")
    table = ex.compare(cases, {"good": (good, None), "bad": (bad, None), "broken": (broken, None)})
    assert table["good"]["pass_rate"] == "1/1" and table["bad"]["pass_rate"] == "0/1"
    assert table["broken"]["pass_rate"] == "0/1" and table["good"]["lines_of_code"] >= 1
    model.reset([[tool("run_query", {"sql": "SELECT COUNT(*) FROM orders"})], [text("400 orders.")]])
    answer, used, tokens = ex.hand_built("How many orders?")
    assert used == ["run_query"] and "400" in answer

# ================================================================ chapter 30
@pytest.fixture
def svc(ws, model):
    import ch30_service as s
    s.API_KEYS, s.RATE_PER_MINUTE, s.DB = ["k1", "k2"], 3, str(ws / "sessions_test.db")
    s._buckets.clear()
    from fastapi.testclient import TestClient
    return s, TestClient(s.app)

H = lambda k: {"Authorization": f"Bearer {k}"}

def test_30_auth_rate_limit_sessions(svc, model):
    s, c = svc
    model.reset(default=[text("There are 400 orders.")])
    assert c.get("/health").status_code == 200
    assert c.post("/v1/chat", json={"message": "hi"}).status_code == 401
    assert c.post("/v1/chat", json={"message": "hi"}, headers=H("nope")).status_code == 401
    first = c.post("/v1/chat", json={"message": "How many orders?"}, headers=H("k1"))
    assert first.status_code == 200 and first.json()["answer"] == "There are 400 orders."
    sid = first.json()["session_id"]
    assert c.post("/v1/chat", json={"message": "And cancelled?", "session_id": sid},
                  headers=H("k1")).status_code == 200
    assert len(model.calls[-1]["messages"]) == 3                 # the session's history was sent
    assert c.post("/v1/chat", json={"message": "x", "session_id": sid},
                  headers=H("k2")).status_code == 404            # someone else's session
    assert c.post("/v1/chat", json={"message": "x" * 4001}, headers=H("k2")).status_code == 422
    third = c.post("/v1/chat", json={"message": "3rd"}, headers=H("k1"))
    fourth = c.post("/v1/chat", json={"message": "4th"}, headers=H("k1"))
    assert third.status_code == 200 and fourth.status_code == 429
    assert int(fourth.headers["retry-after"]) >= 1
    assert c.post("/v1/chat", json={"message": "hi"}, headers=H("k2")).status_code == 200  # per key

def test_30_model_failure_is_a_clean_502(svc, model):
    s, c = svc
    def boom(kw):
        raise RuntimeError("secret internal detail")
    model.reset(default=boom)
    r = c.post("/v1/chat", json={"message": "hi"}, headers=H("k1"))
    assert r.status_code == 502 and "secret" not in r.text

def test_30_stream_progress_events(svc, model):
    s, c = svc
    model.reset([[tool("run_query", {"sql": "SELECT COUNT(*) FROM orders"})], [text("400 orders.")]])
    with c.stream("POST", "/v1/chat/stream", json={"message": "How many orders?"}, headers=H("k1")) as r:
        body = "".join(r.iter_text())
    assert body.index("event: tool") < body.index("event: answer") and "400 orders." in body

def test_30_4_stream_text(svc, model):
    s, c = svc
    import sol_ch30_service  # noqa: F401  (adds /v1/chat/stream_text)
    model.reset([[tool("run_query", {"sql": "SELECT COUNT(*) FROM orders"})],
                 [text("There are 400 orders in total.")]])
    with c.stream("POST", "/v1/chat/stream_text", json={"message": "How many orders?"},
                  headers=H("k1")) as r:
        pieces = list(r.iter_text())
        sid = r.headers["x-session-id"]
    assert "".join(pieces).strip() == "There are 400 orders in total."
    assert len(model.calls) == 2
    assert len(s.load_session(sid, s.key_id("k1"))) == 4          # saved: q, tool_use, result, answer

def test_30_client_modes_against_a_real_server(svc, model, capsys, monkeypatch):
    s, _ = svc
    import sol_ch30_service  # noqa: F401
    port = free_port()
    server = serve(s.app, port)
    import ch30_client as cl
    monkeypatch.setattr(cl, "API", f"http://127.0.0.1:{port}")
    monkeypatch.setattr(cl, "KEY", "k1")
    model.reset(default=[text("400")])
    first = cl.chat("How many orders?")
    assert cl.chat("And cancelled?", first["session_id"])["session_id"] == first["session_id"]
    s._buckets.clear()
    cl.limits(n=4)
    out = capsys.readouterr().out
    assert "request 4: 429" in out and "wrong key: 401" in out
    server.should_exit = True

def test_30_remote_mcp_and_6_remote_hub(ws, model):
    import ch30_remote_mcp as rm, ch30_client as cl
    import ex30_5_remote_hub as ex
    port = free_port()
    server = serve(rm.build_app(token="t0k3n", host="127.0.0.1"), port)
    url = f"http://127.0.0.1:{port}/mcp"
    assert sorted(asyncio.run(cl.remote_tools(url, token="t0k3n"))) == ["add_task", "list_tasks"]
    assert httpx.post(url, json={}, headers=H("wrong")).status_code == 401
    assert httpx.post(url, json={}).status_code == 401
    cfg = ws / "remote.json"
    cfg.write_text(json.dumps({"servers": {"team": {"url": url, "token": "t0k3n"}}}))
    model.reset([[tool("team__add_task", {"title": "prepare demo", "due": "2026-10-10"})],
                 [tool("team__list_tasks", {})], [text("Added and listed.")]])
    assert asyncio.run(ex.main(str(cfg), ["Add 'prepare demo', then list."])) == 0
    assert "prepare demo" in (ws / "tasks.json").read_text()
    cfg.write_text(json.dumps({"servers": {"team": {"url": url, "token": "wrong"}}}))
    assert asyncio.run(ex.main(str(cfg), ["x"])) == 1               # a clear error, not a crash
    server.should_exit = True

def test_30_6_drill(svc, model):
    s, _ = svc
    s.API_KEYS, s.RATE_PER_MINUTE = ["k1", "k2", "k3", "k4", "k5"], 600
    model.reset(default=[text("400")])
    port = free_port()
    server = serve(s.app, port)
    import ex30_6_drill as ex
    summary = ex.drill(users=4, seconds=1.0, api=f"http://127.0.0.1:{port}")
    assert summary["ok"] >= 4 and summary["502"] == 0 and summary["cost_per_request_usd"] > 0
    s.RATE_PER_MINUTE = 1                                            # now the limit bites
    s._buckets.clear()
    summary = ex.drill(users=5, seconds=2.0, api=f"http://127.0.0.1:{port}")
    assert summary["429"] >= 1, summary
    server.should_exit = True


def test_30_fails_closed_and_stores_no_keys(svc, model, monkeypatch):
    s, c = svc
    from fastapi.testclient import TestClient
    monkeypatch.setattr(s, "API_KEYS", [])
    with pytest.raises(RuntimeError, match="AGENT_API_KEYS"):
        with TestClient(s.app):                                   # "with" runs the startup check
            pass
    monkeypatch.setattr(s, "API_KEYS", ["k1", "k2"])
    model.reset(default=[text("400")])
    assert c.post("/v1/chat", json={"message": "hi"}, headers={"Authorization": "Bearer k\u00e9y".encode("latin-1")}).status_code == 401  # no crash
    sid = c.post("/v1/chat", json={"message": "hi"}, headers=H("k1")).json()["session_id"]
    import sqlite3
    owner = sqlite3.connect(s.DB).execute("SELECT owner FROM sessions WHERE id=?", (sid,)).fetchone()[0]
    assert owner == s.key_id("k1") and "k1" != owner

def test_30_one_request_per_session(svc, model):
    s, c = svc
    with s.session_lock("busy-session"):
        r = c.post("/v1/chat", json={"message": "hi", "session_id": "busy-session"}, headers=H("k1"))
    assert r.status_code == 409

def test_30_history_is_bounded(svc):
    s, _ = svc
    msgs = []
    for i in range(30):
        msgs += [{"role": "user", "content": f"q{i}"},
                 {"role": "assistant", "content": [{"type": "tool_use", "id": f"t{i}", "name": "x", "input": {}}]},
                 {"role": "user", "content": [{"type": "tool_result", "tool_use_id": f"t{i}", "content": "r"}]},
                 {"role": "assistant", "content": [{"type": "text", "text": "a"}]}]
    kept = s.bounded(msgs, limit=10)
    assert len(kept) == 8 and kept[0] == {"role": "user", "content": "q28"}   # whole turns only

def test_30_stream_stops_when_client_disconnects(svc, model):
    s, _ = svc
    import threading
    cancelled = threading.Event(); cancelled.set()
    model.reset(default=[tool("run_query", {"sql": "SELECT 1"})])
    answer, _, stats = s.run("loop forever", [], cancelled=cancelled)
    assert "disconnected" in answer and stats["steps"] == 1

def test_30_remote_mcp_scopes_and_metadata(ws, model):
    import ch30_remote_mcp as rm, ch30_client as cl
    port = free_port()
    server = serve(rm.build_app(token="rw-token-123456", readonly_token="ro-token-123456",
                                host="127.0.0.1"), port)
    base = f"http://127.0.0.1:{port}"
    r = httpx.post(base + "/mcp", json={})
    assert r.status_code == 401 and "resource_metadata" in r.headers["www-authenticate"]
    meta = httpx.get(base + "/.well-known/oauth-protected-resource/mcp").json()
    assert meta["authorization_servers"] and "todo:read" in meta["scopes_supported"]
    assert httpx.post(base + "/mcp", json={}, headers={**H("rw-token-123456"), "Host": "evil.example"}).status_code == 421
    async def call(token, name, args):
        from mcp import Client
        from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client
        async with create_mcp_http_client(headers=H(token)) as http:
            async with Client(streamable_http_client(base + "/mcp", http_client=http)) as c:
                r = await c.call_tool(name, args)
                return r.is_error, " ".join(getattr(b, "text", "") for b in r.content)
    assert asyncio.run(call("ro-token-123456", "list_tasks", {}))[0] is False
    err, msg = asyncio.run(call("ro-token-123456", "add_task", {"title": "sneaky"}))
    assert err and "todo:write" in msg
    assert asyncio.run(call("rw-token-123456", "add_task", {"title": "allowed"}))[0] is False
    server.should_exit = True

# ---- 19.8: the smoke test a deployment must pass
def test_30_7_smoke_test_against_the_service(svc, model, capsys):
    import ch30_smoke_test as smoke
    s, c = svc
    model.reset(default=[text("There are 50 customers.")])
    assert smoke.smoke(c, "http://testserver", "k1", chat=True)
    out = capsys.readouterr().out
    assert "FAIL" not in out and "a real question gets an answer" in out
    assert "bad input is rejected (422)" in out

def test_30_7_smoke_test_catches_problems(svc, model, capsys):
    import ch30_smoke_test as smoke
    s, c = svc
    assert not smoke.smoke(c, "http://agents.example.com", None)      # plain HTTP in production
    assert "FAIL  uses HTTPS" in capsys.readouterr().out
    s.API_KEYS.append("open-sesame")
    assert smoke.smoke(c, "http://testserver", "open-sesame")
    s.API_KEYS.remove("open-sesame")

def test_30_7_production_image_is_minimal():
    import os
    code = os.environ["COURSE_CODE"]
    docker = open(os.path.join(code, "ch30_service.Dockerfile")).read()
    assert "USER app" in docker and "HEALTHCHECK" in docker and "${PORT}" in docker
    copies = [l for l in docker.splitlines() if l.startswith("COPY")]
    assert copies and not any(".env" in l or " . " in l for l in copies)   # no secrets, no "copy everything"
    for f in docker.split("COPY ch04_agent.py", 1)[1].split("./")[0].split():
        assert os.path.exists(os.path.join(code, f)), f
    reqs = open(os.path.join(code, "ch30_requirements.txt")).read().split()
    assert all("==" in r for r in reqs if not r.startswith("#") and "=" in r)
