"""Chapters 1-3 reference solutions, run against the scripted model."""
import pytest
from fakemodel import tool, text, last_user_text

# ---------------- chapter 1
def test_1_3_two_system_prompts(model):
    import ex1_3_eli10 as ex
    model.reset(default=[text("A summary.")])
    rows = ex.main()
    assert [r[0] for r in rows] == ["You are a concise technical writer.",
                                    "Explain like I am 10 years old."]
    assert model.calls[1]["system"] == "Explain like I am 10 years old."

def test_1_5_workflow_parses_and_validates(model):
    import ex1_5_workflow as ex
    model.reset([[text('```json\n{"order_id": "A1234", "complaint": "broken"}\n```')],
                 [text("Refund.")], [text("Sorry, refunding now.")]])
    out = ex.handle_email("Order #A1234 arrived broken.")
    assert out["fields"]["order_id"] == "A1234" and out["category"] == "refund"
    # bad JSON and an out-of-set category are handled, not crashes
    model.reset([[text("I cannot find JSON")], [text("sponsorship")], [text("Thanks!")]])
    out = ex.handle_email("Do you sponsor teams?")
    assert out["fields"]["parse_error"] and out["category"] == "other"

def test_1_6_history_vs_broken(model):
    import ex1_6_chat as ex
    model.reset(default=[text("ok")])
    ex.demo(remember=True)
    assert len(model.calls[2]["messages"]) == 5           # all turns resent
    model.reset(default=[text("ok")])
    ex.demo(remember=False)
    assert len(model.calls[2]["messages"]) == 1           # only the latest message

# ---------------- chapter 2
def test_2_2_calculator_safety():
    from sol_ch02_calculator_agent import calculate, run_tool
    assert calculate("sqrt(2) * 50") == "70.7106781187"
    assert calculate("2 ** 10") == "1024"
    for bad in ["__import__('os')", "10 ** 10 ** 10", "sqrt(4, 2)", "open('x')"]:
        out, is_error = run_tool("calculate", {"expression": bad})
        assert is_error and out.startswith("ERROR"), bad

def test_2_5_graceful_errors():
    from sol_ch02_calculator_agent import run_tool
    out, err = run_tool("calculate", {"expression": "5 / 0"})
    assert err and "ZeroDivisionError" in out
    out, err = run_tool("calculate", {"expression": "2 +* 3"})
    assert err and "SyntaxError" in out

def test_2_5_error_reaches_model(model):
    import sol_ch02_calculator_agent as sol
    model.reset([[tool("calculate", {"expression": "5/0"})], [text("You can't divide by zero.")]])
    assert "zero" in sol.ask("What is 5 divided by zero?")
    result = model.calls[1]["messages"][-1]["content"][0]
    assert result["is_error"] is True

def test_2_3_trace_prints_tool_use(model, capsys):
    import ex2_3_trace as ex
    model.reset([[tool("calculate", {"expression": "0.175*84213"})]])
    assert ex.first_response("What is 17.5% of 84,213?").stop_reason == "tool_use"
    assert "tool_use" in capsys.readouterr().out

def test_2_4_description_eval(model):
    import ex2_4_description_eval as ex
    def smart(kw):   # calls the tool for arithmetic unless the description is weak
        q = last_user_text(kw)
        arithmetic = any(ch.isdigit() for ch in q)
        weak = kw["tools"][0]["description"] == ex.WEAK
        if arithmetic and not (weak and "%" in q):
            return [tool("calculate", {"expression": "1+1"})]
        return [text("no tool")]
    model.reset(default=smart)
    report = ex.main()
    assert report["strong"] == 10 and report["weak"] < 10

def test_2_6_two_calls_break_loop_fixes(model):
    import ex2_6_two_tools as ex
    script = [[tool("percent_change", {"old": 84213, "new": 97400})],
              [tool("calculate", {"expression": "0.175*97400"})],
              [text("15.66% growth; 17.5% of 97,400 is 17,045.")]]
    model.reset(list(script))
    assert ex.two_call_ask(ex.QUESTION).startswith("BROKEN")
    model.reset(list(script))
    assert "17,045" in ex.sol.ask(ex.QUESTION)

# ---------------- chapter 3

def test_3_3_get_current_time():
    import sol_ch03_tools as t
    assert "Asia/Tokyo" in t.run_tool("get_current_time", {"timezone": "Asia/Tokyo"})
    assert t.run_tool("get_current_time", {"timezone": "Mars/Base"}).startswith("ERROR")
    assert any(x["name"] == "get_current_time" for x in t.TOOLS)

def test_3_4_routing_eval_reports_flips(model):
    import ex3_4_routing_eval as ex
    expected = dict(ex.CASES)
    calls = {"n": 0}
    def router(kw):
        calls["n"] += 1
        exp = expected[last_user_text(kw)]
        if last_user_text(kw) == "What's 3 + 4?" and calls["n"] > 20:
            exp = None                        # flips on later runs
        return [tool(exp, {})] if exp else [text("answer")]
    model.reset(default=router)
    scores, flips, failures = ex.run(3)
    assert len(ex.CASES) == 20 and scores[0] == 1.0 and flips == ["What's 3 + 4?"]

def test_3_5_forced_tool_returns_dict(model):
    import ex3_5_forced_tool as ex
    model.reset([[tool("record_contact", {"name": "Priya Raman", "email": "priya.raman@acme.example",
                                          "company": "Acme Corp"})]])
    assert ex.extract(ex.SIGNATURES[0])["company"] == "Acme Corp"
    assert model.calls[0]["tool_choice"] == {"type": "tool", "name": "record_contact"}

def test_3_6_ten_tools_and_fix(model):
    import ex3_6_ten_tools as ex
    assert len(ex.TEN_TOOLS) == 10 and len(ex.FIXED_TOOLS) == 9
    assert ex.REGISTRY["add_days"]("2026-03-01", 45) == "2026-04-15"
    expected = dict(ex.CASES)
    def router(kw):
        q = last_user_text(kw); names = [t["name"] for t in kw["tools"]]
        exp = expected[q]
        if "multiply" in names and exp == "add_days":
            return [tool("days_between", {})]         # confused before the fix
        return [tool(exp, {})] if exp else [text("x")]
    model.reset(default=router)
    before, after = ex.main()
    assert after > before


def test_2_first_tool_round_trip(model, capsys):
    import runpy
    model.reset([[tool("get_today", {})], [text("It's Thursday.")]])
    runpy.run_path("ch02_first_tool.py", run_name="__main__")
    out = capsys.readouterr().out
    assert "stop_reason: tool_use" in out and "ANSWER: It's Thursday." in out
    result = model.calls[1]["messages"][-1]["content"][0]
    assert result["type"] == "tool_result" and result["tool_use_id"] == next(b.id for b in model.calls[1]["messages"][1]["content"] if b.type == "tool_use")


def test_3_structured_outputs_through_the_real_sdk():
    """messages.parse() against a local fake of the Messages API: the SDK validates the reply."""
    import socket, ex3_5_forced_tool as ex
    from fake_messages_api import FakeAPI
    from anthropic._client import Anthropic
    with socket.socket() as s_:
        s_.bind(("127.0.0.1", 0)); port = s_.getsockname()[1]
    api = FakeAPI([[{"text": '{"name": "Sam Ortiz", "email": null, "company": "Fabrikam Robotics"}'}]], port).start()
    try:
        c = ex.extract_parsed(ex.SIGNATURES[-1], Anthropic(api_key="sk-test", base_url=f"http://127.0.0.1:{port}"))
        assert c.name == "Sam Ortiz" and c.email is None and c.company == "Fabrikam Robotics"
        fmt = api.requests[0]["output_config"]["format"]
        assert fmt["type"] == "json_schema" and "email" in fmt["schema"]["properties"]
    finally:
        api.stop()

def test_3_strict_tool_schema():
    import ch03_structured as s
    t = s.STRICT_CONVERT
    assert t["strict"] is True and t["input_schema"]["additionalProperties"] is False
