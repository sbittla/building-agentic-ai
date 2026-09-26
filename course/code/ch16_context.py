"""Chapter 16: keeping the context window small, cheap and useful."""
import json
import os
import time
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
_client = None

def client():
    global _client
    if _client is None:
        _client = Anthropic()
    return _client

# ---------------------------------------------------------------- 1. measuring
def _text_of(block) -> str:
    if isinstance(block, dict):
        return json.dumps(block)
    return json.dumps(getattr(block, "input", None) or getattr(block, "text", "") or "")

def estimate_tokens(messages, system: str = "", tools=()) -> int:
    """Fast offline estimate: about 4 characters per token for English and code."""
    chars = len(system) + len(json.dumps(list(tools)))
    for m in messages:
        c = m["content"]
        chars += len(c) if isinstance(c, str) else sum(len(_text_of(b)) for b in c)
    return chars // 4

def count_tokens(messages, system: str = "", tools=()) -> int:
    """Exact count from the API (free to call), falling back to the estimate."""
    try:
        return client().messages.count_tokens(model=MODEL, messages=messages,
                                              system=system,
                                              tools=list(tools)).input_tokens
    except Exception:
        return estimate_tokens(messages, system, tools)

# ---------------------------------------------------------------- 2. trimming
def trim_old_tool_results(messages, keep_last: int = 2, max_chars: int = 300):
    """Shorten all but the newest `keep_last` tool results. Returns a NEW list."""
    positions = [(i, j) for i, m in enumerate(messages)
                 if m["role"] == "user" and isinstance(m["content"], list)
                 for j, b in enumerate(m["content"])
                 if isinstance(b, dict) and b.get("type") == "tool_result"]
    old = set(positions[:-keep_last] if keep_last else positions)
    out = []
    for i, m in enumerate(messages):
        if not isinstance(m["content"], list) or m["role"] != "user":
            out.append(m)
            continue
        blocks = []
        for j, b in enumerate(m["content"]):
            if (i, j) in old and len(str(b.get("content", ""))) > max_chars:
                text = str(b["content"])
                b = {**b, "content": text[:max_chars]
                     + f"\n[trimmed {len(text) - max_chars} characters; "
                       "call the tool again if needed]"}
            blocks.append(b)
        out.append({**m, "content": blocks})
    return out

# ---------------------------------------------------------------- 3. compacting
def _safe_cut(messages, keep_last_turns: int) -> int:
    """Index where the kept part starts: always at a plain user message, so a
    tool_use is never separated from its tool_result."""
    starts = [i for i, m in enumerate(messages)
              if m["role"] == "user" and isinstance(m["content"], str)]
    return starts[-keep_last_turns] if len(starts) >= keep_last_turns else 0

def compact(messages, keep_last_turns: int = 2):
    """Summarize everything before the last `keep_last_turns` user turns."""
    cut = _safe_cut(messages, keep_last_turns)
    if cut == 0:
        return messages, None
    transcript = []
    for m in messages[:cut]:
        c = m["content"]
        text = c if isinstance(c, str) else " ".join(_text_of(b) for b in c)
        transcript.append(f"{m['role'].upper()}: {text[:2000]}")
    r = client().messages.create(model=MODEL, max_tokens=2000,
                                 messages=[{"role": "user", "content":
        "Summarize this conversation for yourself so you can continue it. Keep: the "
        "user's goals and preferences, decisions made, facts found (with numbers and "
        "ids), and open questions. Drop small talk and raw tool output.\n\n"
        + "\n".join(transcript)}])
    summary = "".join(b.text for b in r.content if b.type == "text")
    kept = [{"role": "user",
             "content": f"[Summary of our earlier conversation]\n{summary}"},
            {"role": "assistant",
             "content": "Understood. I'll continue from that summary."}]
    return kept + messages[cut:], summary

# ---------------------------------------------------------------- 4. prompt caching
# The API caches a prefix only if it's long enough: from 1,024 to 4,096 tokens
# depending on the model (check the prompt-caching docs for yours). Shorter prefixes
# are simply not cached, with no error: the usage fields stay at 0. Measure before
# you rely on it.
def with_cache(system: str, tools: list):
    """Mark the stable prefix (tools, then system prompt) as cacheable."""
    tools = [dict(t) for t in tools]
    if tools:
        tools[-1] = {**tools[-1], "cache_control": {"type": "ephemeral"}}
    system_blocks = [{"type": "text", "text": system,
                      "cache_control": {"type": "ephemeral"}}]
    return system_blocks, tools

def cache_kwargs(system: str, tools: list, mode: str = "auto") -> dict:
    """Request arguments for a caching mode:
    off    -- no caching
    prefix -- cache tools + system prompt only (with_cache)
    auto   -- a top-level cache_control: the API puts the breakpoint at the END
              of the request, so the growing conversation is cached too, not just
              the prefix."""
    if mode == "prefix":
        system_blocks, cached_tools = with_cache(system, tools)
        return {"system": system_blocks, "tools": cached_tools}
    kwargs = {"system": system, "tools": tools}
    if mode == "auto":
        kwargs["cache_control"] = {"type": "ephemeral"}
    return kwargs

# ---------------------------------------------------------------- 5. a managed loop
def run_managed_agent(question, tools, run_tool, system="You are a helpful assistant.",
                      messages=None, budget_tokens=20_000, max_iterations=10,
                      verbose=True, caching="auto"):
    """The chapter 4 loop plus context management and caching on every call."""
    from ch04_agent import next_action
    messages = list(messages or []) + [{"role": "user", "content": question}]
    request = cache_kwargs(system, tools, caching)
    stats = {"steps": 0, "input": 0, "output": 0, "cache_read": 0, "cache_write": 0,
             "trims": 0, "compactions": 0, "stop_reason": None}
    for step in range(1, max_iterations + 1):
        # Trimming or compacting rewrites old messages, which changes the cached
        # prefix: the next call pays a cache WRITE again. That's why both happen only
        # over budget.
        if estimate_tokens(messages, system, tools) > budget_tokens:
            messages = trim_old_tool_results(messages); stats["trims"] += 1
        if estimate_tokens(messages, system, tools) > budget_tokens:
            messages, summary = compact(messages)
            # compact() can only cut at a user turn; inside a single long turn
            # there is nothing it may summarize yet
            if summary:
                stats["compactions"] += 1
        r = client().messages.create(model=MODEL, max_tokens=4096, messages=messages,
                                     **request)
        u = r.usage
        stats["steps"] = step
        stats["input"] += u.input_tokens
        stats["output"] += u.output_tokens
        stats["cache_read"] += getattr(u, "cache_read_input_tokens", 0) or 0
        stats["cache_write"] += getattr(u, "cache_creation_input_tokens", 0) or 0
        stats["stop_reason"] = r.stop_reason
        messages.append({"role": "assistant", "content": r.content})
        action, note = next_action(r)
        text = "".join(b.text for b in r.content if b.type == "text")
        if action == "done":
            return text, messages, stats
        if action == "stop":
            return f"{text}\n\n[Stopped: {note}]".strip(), messages, stats
        if action == "continue":
            continue
        results = [{"type": "tool_result", "tool_use_id": b.id,
                    "content": run_tool(b.name, b.input)}
                   for b in r.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
        if verbose:
            print(f"[step {step}] ~{estimate_tokens(messages, system, tools)} "
                  "tokens in context")
    return "Stopped at max_iterations.", messages, stats

# ------------------------------------------------------------- 6. letting the API do it
SERVER_EDITING = {  # sent with betas=["context-management-2025-06-27"]
    "edits": [{"type": "clear_tool_uses_20250919",  # trim_old_tool_results, server-side
               "trigger": {"type": "input_tokens", "value": 30_000},
               "keep": {"type": "tool_uses", "value": 3}}]}

def create_with_server_editing(messages, system, tools, max_tokens=4096):
    """The API clears old tool results itself once the context passes the trigger. Your
    `messages` list is unchanged; the edit happens on the server for that request."""
    return client().beta.messages.create(
        model=MODEL, max_tokens=max_tokens, system=system, tools=tools,
        messages=messages, betas=["context-management-2025-06-27"],
        context_management=SERVER_EDITING)

# Prices for cost estimates, in dollars per million tokens (Claude Sonnet 5, 2026).
PRICE = {"input": 2.00, "output": 10.00, "cache_write": 2.50, "cache_read": 0.20}

def cost(input_tokens, output_tokens, cache_write=0, cache_read=0) -> float:
    return (input_tokens * PRICE["input"] + output_tokens * PRICE["output"]
            + cache_write * PRICE["cache_write"]
            + cache_read * PRICE["cache_read"]) / 1e6

if __name__ == "__main__":
    import ch06_notes_tools as notes
    history = []
    for q in ["Which notes mention Kafka?",
              "What was the root cause of the lag incident?",
              "And what follow-up did we agree?"]:
        answer, history, stats = run_managed_agent(q, notes.TOOLS, notes.run_tool,
                                                   system=notes.SYSTEM,
                                                   messages=history,
                                                   budget_tokens=3_000)
        print(f"\nQ: {q}\nA: {answer}\n{stats}")
