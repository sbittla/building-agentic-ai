def test_run_tool(ex):
    assert ex.run_tool("add", {"a": 2, "b": 3}) == "5"
    assert ex.run_tool("greet", {"name": "Asha", "excited": True}) == "Hello, Asha!"
    assert ex.run_tool("greet", {"nme": "typo"}).startswith("ERROR"), "a wrong argument name -> ERROR, no crash"
    assert ex.run_tool("fly", {}).startswith("ERROR"), "an unknown tool -> ERROR, no crash"
    assert isinstance(ex.run_tool("add", {"a": 1, "b": 1}), str), "always return text"
