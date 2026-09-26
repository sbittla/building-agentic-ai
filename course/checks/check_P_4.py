def test_tool(ex):
    assert "get_weather" in ex.TOOLS and ex.TOOLS["get_weather"]["description"] == "Weather for a city."
    assert ex.get_weather("Pune") == "sunny in Pune", "the decorator must return the function unchanged"

def test_count_calls(ex):
    before = ex.calls.get("ping", 0)
    assert ex.ping() == "pong" and ex.ping() == "pong"
    assert ex.calls["ping"] == before + 2
