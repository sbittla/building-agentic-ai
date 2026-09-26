def test_time_tool(ex):
    tool = next((t for t in ex.TOOLS if t["name"] == "get_current_time"), None)
    assert tool, "add get_current_time to TOOLS"
    assert "get_current_time" in ex.REGISTRY, "and to REGISTRY"
    tz = tool["input_schema"]["properties"]["timezone"]
    assert "Asia/Tokyo" in tz.get("enum", []), "an enum of time zones including Asia/Tokyo"
    out = ex.run_tool("get_current_time", {"timezone": "Asia/Tokyo"})
    out = out[0] if isinstance(out, tuple) else out
    assert ":" in out and not out.startswith("ERROR"), f"got {out!r}"
