"""Exercise 16.6 (solution): the head/tail trimming, tested."""
from sol_ch16_context import trim_old_tool_results

def _conversation(n_results=3, lines=200):
    msgs = [{"role": "user", "content": "question"}]
    for k in range(n_results):
        tid = f"toolu_{k}"
        msgs.append({"role": "assistant", "content": [{"type": "tool_use", "id": tid,
                                                        "name": "read_file", "input": {}}]})
        msgs.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": tid,
                     "content": "\n".join(f"line {i}" for i in range(1, lines + 1))}]})
    return msgs

def test_200_lines_become_11():
    msgs = _conversation()
    out = trim_old_tool_results(msgs, keep_last=2)
    first = out[2]["content"][0]["content"].splitlines()
    assert len(first) == 11
    assert first[:5] == [f"line {i}" for i in range(1, 6)]
    assert first[-5:] == [f"line {i}" for i in range(196, 201)]
    assert "190 lines omitted" in first[5]
    # the newest two results are untouched, and the input list was not modified
    assert len(out[4]["content"][0]["content"].splitlines()) == 200
    assert len(msgs[2]["content"][0]["content"].splitlines()) == 200

def test_every_tool_use_still_has_its_result():
    out = trim_old_tool_results(_conversation(5), keep_last=1)
    for a, b in zip(out, out[1:]):
        if a["role"] == "assistant":
            ids = {c["id"] for c in a["content"] if c.get("type") == "tool_use"}
            assert ids == {c["tool_use_id"] for c in b["content"]}

def test_short_results_are_left_alone():
    out = trim_old_tool_results(_conversation(3, lines=8), keep_last=0)
    assert all(len(m["content"][0]["content"].splitlines()) == 8
               for m in out if m["role"] == "user" and isinstance(m["content"], list))
