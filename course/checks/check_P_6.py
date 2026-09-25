def test_add_tag(ex):
    assert ex.add_tag("a") == ["a"] and ex.add_tag("b") == ["b"], "each call must start with a NEW list"

def test_last_n(ex):
    assert ex.last_n([1, 2, 3, 4], 2) == [3, 4] and ex.last_n([1, 2, 3], 3) == [1, 2, 3]

def test_parse_amount(ex):
    assert ex.parse_amount("12.50") == 12.5
    out = ex.parse_amount("x")
    assert isinstance(out, str) and out.startswith("ERROR"), "don't swallow the error: return a message"
