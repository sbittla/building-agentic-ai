def test_sqrt(ex):
    out = ex.calculate("sqrt(2) * 50")
    assert abs(float(out) - 70.7106781187) < 1e-6, f"sqrt(2) * 50 should be about 70.71, got {out!r}"

def test_still_safe(ex):
    for bad in ["__import__('os')", "open('x')", "sqrt.__class__", "exp(1)"]:
        out, is_error = ex.run_tool("calculate", {"expression": bad})
        assert is_error, f"{bad!r} must still be rejected"

def test_description_mentions_sqrt(ex):
    tool = next(t for t in ex.TOOLS if t["name"] == "calculate")
    assert "sqrt" in tool["description"], "tell the model sqrt exists: update the description"
