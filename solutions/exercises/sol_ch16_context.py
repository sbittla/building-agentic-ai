"""Exercise 16.6 (solution): smarter trimming. Keep the first and last lines of an old
tool result, and say how many lines were left out in the middle."""
from ch16_context import *            # noqa: F401,F403  (everything else is unchanged)

def trim_old_tool_results(messages, keep_last: int = 2, head: int = 5, tail: int = 5):
    """Shorten all but the newest `keep_last` tool results to head + 1 + tail lines.
    Returns a NEW list; tool_use ids are untouched, so every tool_use keeps its result."""
    positions = [(i, j) for i, m in enumerate(messages)
                 if m["role"] == "user" and isinstance(m["content"], list)
                 for j, b in enumerate(m["content"])
                 if isinstance(b, dict) and b.get("type") == "tool_result"]
    old = set(positions[:-keep_last] if keep_last else positions)
    out = []
    for i, m in enumerate(messages):
        if m["role"] != "user" or not isinstance(m["content"], list):
            out.append(m)
            continue
        blocks = []
        for j, b in enumerate(m["content"]):
            if (i, j) in old:
                lines = str(b.get("content", "")).splitlines()
                if len(lines) > head + tail + 1:
                    omitted = len(lines) - head - tail
                    b = {**b, "content": "\n".join(lines[:head] + [f"[... {omitted} lines omitted; "
                         "call the tool again if you need them ...]"] + lines[-tail:])}
            blocks.append(b)
        out.append({**m, "content": blocks})
    return out
