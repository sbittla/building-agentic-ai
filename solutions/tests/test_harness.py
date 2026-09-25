from fakemodel import tool, text

def test_fake_model_round_trip(model):
    import ch04_agent, ch03_tools
    model.reset([[tool("get_current_date", {})], [text("done")]])
    answer, _, stats = ch04_agent.run_agent("q", ch03_tools.TOOLS, ch03_tools.run_tool,
                                            verbose=False)
    assert answer == "done" and stats["tool_calls"] == 1
