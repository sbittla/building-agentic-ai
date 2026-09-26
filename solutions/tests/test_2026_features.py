"""Features added for the September 2026 update: tool search (3.6), programmatic tool calling
(16.7), Agent Skills (18.7) and Claude Managed Agents (18.8). All offline."""
import json
from types import SimpleNamespace as S
import pytest
from fakemodel import text, tool

# ---------------------------------------------------------------- 3.6 tool search
def test_tool_search_defers_all_but_the_essentials(model):
    import ch03_tool_search as ts
    tools = ts.with_tool_search(ts.ALL_TOOLS)
    assert tools[0]["type"].startswith("tool_search_tool_") and "defer_loading" not in tools[0]
    loaded = [t["name"] for t in tools[1:] if not t.get("defer_loading")]
    assert loaded == ["basic_get_current_date"] and len(tools) == len(ts.ALL_TOOLS) + 1
    assert len({t["name"] for t in ts.ALL_TOOLS}) == len(ts.ALL_TOOLS)   # names stay unique

def test_tool_search_agent_runs_only_client_tools(model, ws):
    import ch03_tool_search as ts
    from ch04_agent import run_agent
    search = S(type="server_tool_use", id="srvtoolu_1", name="tool_search_tool_bm25",
               input={"query": "sql orders"})
    found = S(type="tool_search_tool_result", tool_use_id="srvtoolu_1",
              content={"type": "tool_search_tool_search_result", "tool_references": [
                  {"type": "tool_reference", "tool_name": "sql_run_query"}]})
    model.reset([[search, found, tool("sql_run_query", {"sql": "SELECT COUNT(*) AS n FROM orders"})],
                 [text("There are 400 orders.")]])
    answer, messages, stats = run_agent("How many orders?", ts.with_tool_search(ts.ALL_TOOLS),
                                        ts.run_tool, verbose=False)
    assert "400" in answer and stats["tool_calls"] == 1
    result = messages[2]["content"][0]["content"]
    assert "400" in result                      # the real query ran through the namespaced route
    assert ts.run_tool("nope", {}).startswith("ERROR")

# ---------------------------------------------------------------- 16.7 programmatic tool calling
def test_programmatic_tool_calling_loop(model, ws, monkeypatch):
    import ch16_programmatic as pg
    def step1(kw):
        assert kw["tools"][0]["type"] == "code_execution_20260120"
        assert kw["tools"][1]["allowed_callers"] == ["code_execution_20260120"]
        call = tool("run_query", {"sql": "SELECT category, COUNT(*) AS n FROM products GROUP BY category"})
        call.caller = S(type="code_execution_20260120", tool_id="srvtoolu_9")
        return [S(type="server_tool_use", id="srvtoolu_9", name="code_execution", input={"code": "..."}), call]
    def step2(kw):
        assert kw["container"] == "container_abc"          # the same sandbox, every step
        rows = json.loads(kw["messages"][-1]["content"][0]["content"])
        assert rows and {"category", "n"} <= set(rows[0])
        return [text("Electronics leads.")]
    model.reset([step1, step2])
    real_respond = model.respond
    def respond(kw):
        r = real_respond(kw)
        r.container = S(id="container_abc")
        return r
    monkeypatch.setattr(model, "respond", respond)
    answer, stats = pg.ask("Revenue share by category?", verbose=False)
    assert answer == "Electronics leads." and stats["tool_calls"] == 1
    assert stats["result_chars_kept_out"] > 10
    assert pg.run_query_json("DELETE FROM orders").startswith("ERROR")   # read-only

# ---------------------------------------------------------------- 18.7 Agent Skills
def test_skill_validation_and_progressive_disclosure(ws, monkeypatch, tmp_path):
    import ch24_skills as sk
    monkeypatch.setattr(sk, "SKILLS_DIR", tmp_path / "skills")
    folder = sk.make_example_skill()
    assert sk.validate(folder) == []
    assert sk.catalog().startswith("- sql-report: Writes a short")
    assert "references/schema.md" in sk.read_skill("sql-report")
    assert "order_items" in sk.read_skill("sql-report", "references/schema.md")
    assert sk.read_skill("sql-report", "../../../etc/passwd").startswith("ERROR")
    assert sk.read_skill("missing").startswith("ERROR")
    bad = tmp_path / "skills" / "Bad_Skill"
    bad.mkdir()
    (bad / "SKILL.md").write_text("---\nname: Bad_Skill\ndescription: \n---\nhi")
    problems = sk.validate(bad)
    assert any("lowercase" in p for p in problems) and any("description" in p for p in problems)
    assert "sql-report" in sk.system_prompt()

def test_agent_uses_skill_then_data(model, ws, monkeypatch, tmp_path):
    import ch24_skills as sk
    import ch08_sql_tools as sql
    from ch04_agent import run_agent
    monkeypatch.setattr(sk, "SKILLS_DIR", tmp_path / "skills")
    sk.make_example_skill()
    model.reset([[tool("read_skill", {"name": "sql-report"})],
                 [tool("run_query", {"sql": "SELECT COUNT(*) FROM products"})],
                 [text("## Revenue by category ...")]])
    run = lambda n, a: sk.read_skill(**a) if n == "read_skill" else sql.run_tool(n, a)
    answer, messages, _ = run_agent("Revenue report please", sk.TOOLS + sql.TOOLS, run,
                                    system=sk.system_prompt(), verbose=False)
    assert "Revenue" in answer and "SUM(quantity * price)" in messages[2]["content"][0]["content"]
    assert "sql-report" in model.calls[0]["system"]

# ---------------------------------------------------------------- 18.8 Managed Agents
class FakeManaged:
    """Just enough of client.beta for ch24_managed_agent.run()."""
    def __init__(self, events):
        self.events, self.sent, self.created, self.archived = events, [], {}, []
        me = self
        class Stream:
            def __enter__(s): return iter(me.events)
            def __exit__(s, *a): return False
        self.beta = S(
            agents=S(create=lambda **kw: me.created.setdefault("agent", S(id="agent_1", **{"kw": kw}))),
            environments=S(create=lambda **kw: me.created.setdefault("env", S(id="env_1", kw=kw))),
            sessions=S(create=lambda **kw: me.created.setdefault("session", S(id="sesn_1", kw=kw)),
                       archive=lambda sid: me.archived.append(sid),
                       events=S(stream=lambda sid: Stream(),
                                send=lambda sid, events: me.sent.append(events))))

def test_managed_agent_session(ws):
    import ch24_managed_agent as ma
    events = [
        S(type="agent.custom_tool_use", id="evt_1", name="run_query",
          input={"sql": "SELECT COUNT(*) AS n FROM orders"}),
        S(type="agent.tool_use", id="evt_2", name="bash", input={"command": "rm -rf /"},
          evaluated_permission="ask"),
        S(type="session.status_idle", stop_reason=S(type="requires_action", event_ids=["evt_2"])),
        S(type="agent.message", content=[S(type="text", text="Done.")]),
        S(type="session.status_idle", stop_reason=S(type="end_turn")),
    ]
    fake = FakeManaged(events)
    ended = ma.run("How many orders?", client=fake, approve=lambda e: False)
    assert ended == "end_turn" and fake.archived == ["sesn_1"]
    agent_kw = fake.created["agent"].kw
    toolset = agent_kw["tools"][0]
    assert {"name": "bash", "permission_policy": {"type": "always_ask"}} in toolset["configs"]
    assert fake.created["session"].kw["budget"]["max_list_cost"]["amount"] == "100"
    assert fake.created["env"].kw["config"]["networking"]["type"] == "limited"
    first, _msg = fake.sent[0], None
    assert first[0]["type"] == "user.message"
    result = fake.sent[1][0]
    assert result["type"] == "user.custom_tool_result" and "400" in result["content"][0]["text"]
    denial = fake.sent[2][0]
    assert denial == {"type": "user.tool_confirmation", "tool_use_id": "evt_2", "result": "deny",
                      "deny_message": "The user declined this command."}

def test_managed_agent_stops_on_budget(ws):
    import ch24_managed_agent as ma
    fake = FakeManaged([S(type="session.status_idle", stop_reason=S(type="budget_reached"))])
    assert ma.run("q", client=fake) == "budget_reached" and fake.archived == ["sesn_1"]

# ---------------------------------------------------------------- solutions 3.8, 16.8, 18.8, 18.9
def test_3_7_compare(model, ws):
    import ex3_7_tool_search as ex
    def respond(kw):
        deferred = any(t.get("defer_loading") for t in kw["tools"])
        if kw["messages"][-1]["role"] == "user" and isinstance(kw["messages"][-1]["content"], str):
            q = kw["messages"][-1]["content"]
            expected = dict(ex.QUESTIONS)[q]
            blocks = [tool(expected, {})]
            if deferred:
                blocks.insert(0, S(type="server_tool_use", id="srv_1", name="tool_search_tool_bm25",
                                   input={"query": q[:20]}))
            return blocks
        return [text("done")]
    model.reset(default=respond)
    table = ex.compare(ex.QUESTIONS[:3])
    assert table["tool search"]["accuracy"] == "3/3" and table["tool search"]["searches"] == 3
    assert table["all loaded"]["searches"] == 0

def test_16_7_compare(model, ws, monkeypatch):
    import ex16_7_programmatic_compare as ex
    model.reset([[tool("run_query", {"sql": "SELECT 1"})], [text("plain answer")]])
    answer, row = ex.plain(ex.FAN_OUT)
    assert answer == "plain answer" and row["tool_calls"] == 1 and row["model_calls"] == 2

def test_18_7_second_skill(model, ws, monkeypatch, tmp_path):
    import ch24_skills as sk
    import ex24_6_skills as ex
    monkeypatch.setattr(sk, "SKILLS_DIR", tmp_path / "skills")
    assert ex.install() == {"customer-lookup": [], "sql-report": []}
    assert "customer-lookup: Looks up one customer" in sk.catalog()
    model.reset([[tool("read_skill", {"name": "customer-lookup"})], [text("Customer 7 ...")]])
    _, messages, _ = __import__("ch04_agent").run_agent("What has Customer 7 bought?", sk.TOOLS,
                                                        ex.run_tool, system=sk.system_prompt(),
                                                        verbose=False)
    assert ex.skills_loaded(messages) == ["customer-lookup"]
    assert "Spend = SUM" in ex.run_tool("read_skill", {"name": "customer-lookup",
                                                       "file": "references/tables.md"})

def test_18_8_budget_is_applied(ws):
    import ch24_managed_agent as ma
    import ex24_7_managed as ex
    fake = FakeManaged([S(type="session.status_idle", stop_reason=S(type="budget_reached"))])
    assert ex.run_with_budget(2, client=fake) == "budget_reached"
    assert fake.created["session"].kw["budget"]["max_list_cost"]["amount"] == "2"
    assert ma.BUDGET["max_list_cost"]["amount"] == "100"          # restored afterwards
