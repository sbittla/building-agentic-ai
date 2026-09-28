"""Chapter 4: the agent loop. Every later chapter reuses run_agent()."""
import json
import os
import time
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
_client = None

def get_client():
    global _client
    if _client is None:
        # A timeout per request and a few automatic retries (with backoff) for
        # overloaded or rate-limited responses. The defaults would wait 10 minutes.
        # (A local model on a CPU is much slower: the course sets MODEL_TIMEOUT for it.)
        _client = Anthropic(timeout=float(os.environ.get("MODEL_TIMEOUT", 120)), max_retries=3)
    return _client

def next_action(response):
    """What to do after a model response:
    ("tools" | "done" | "continue" | "stop", note). Every loop in this course uses
    this, so no stop reason is ever mistaken for success."""
    reason = response.stop_reason
    if reason == "tool_use":
        return "tools", None
    if reason in ("end_turn", "stop_sequence"):
        return "done", None
    if reason == "pause_turn":            # a long server-side step paused: send it back
        return "continue", None
    notes = {
        "max_tokens": "the reply was cut off at max_tokens "
                      "(raise max_tokens or ask for less)",
        "refusal": "the model declined to continue with this request",
        "model_context_window_exceeded":
            "the conversation no longer fits in the context window "
            "(trim or compact it, chapter 16)",
    }
    note = notes.get(reason, f"unexpected stop_reason {reason!r}")
    # refusals say why: e.g. category "cyber"
    details = getattr(response, "stop_details", None)
    if (reason == "refusal" and details is not None
            and getattr(details, "category", None)):
        note += f" (category: {details.category})"
    return "stop", note

def run_agent(question, tools, run_tool, system="You are a helpful assistant.",
              max_iterations=8, verbose=True, messages=None, should_stop=None,
              max_tokens=4096, thinking=None, effort=None, model=None):
    """Loop: call the model, run any tools it asks for, repeat until it stops.

    tools     -- list of tool descriptions (JSON Schema) sent to the model
    run_tool  -- function(name, args) -> str that actually executes a tool
    messages  -- optional existing history (for multi-turn chats)
    should_stop -- optional function(stats) -> reason or None, checked every step
    thinking  -- e.g. {"type": "adaptive"} to let the model reason before it acts
    effort    -- "low" | "medium" | "high" | ...: how hard the model works
                 (and what it costs)
    model     -- which model to call (default MODEL); Chapter 20 routes steps
                 between models
    Returns (answer_text, messages, stats). stats["stop_reason"] says how it ended.
    """
    messages = list(messages or []) + [{"role": "user", "content": question}]
    stats = {"steps": 0, "tool_calls": 0, "input_tokens": 0, "output_tokens": 0,
             "stop_reason": None}

    extra = {}
    if thinking:
        extra["thinking"] = thinking
    if effort:
        extra["output_config"] = {"effort": effort}

    for step in range(1, max_iterations + 1):
        response = get_client().messages.create(
            model=model or MODEL, max_tokens=max_tokens, system=system,
            tools=tools, messages=messages, **extra)
        stats["steps"] = step
        stats["input_tokens"] += response.usage.input_tokens
        stats["output_tokens"] += response.usage.output_tokens
        stats["stop_reason"] = response.stop_reason
        stats["model"] = model or MODEL
        # Append the WHOLE content, unchanged: with thinking on, it includes thinking
        # blocks (with signatures) that the API requires back on the next call.
        messages.append({"role": "assistant", "content": response.content})

        action, note = next_action(response)
        text = "".join(b.text for b in response.content if b.type == "text")
        if action == "done":                           # the model is finished
            return text, messages, stats
        if action == "stop":                           # cut off, refused, too long...
            return f"{text}\n\n[Stopped: {note}]".strip(), messages, stats
        if action == "continue":                       # pause_turn: just ask again
            continue

        results = []                                   # run EVERY tool call
        for block in response.content:
            if block.type != "tool_use":
                continue
            t0 = time.perf_counter()
            output = run_tool(block.name, block.input)
            stats["tool_calls"] += 1
            if verbose:
                ms = (time.perf_counter() - t0) * 1000         # this tool's time only
                print(f"[step {step}] {block.name}({json.dumps(block.input)}) "
                      f"-> {output[:80]!r}  ({ms:.0f} ms)")
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": output,
                            "is_error": output.startswith("ERROR")})
        messages.append({"role": "user", "content": results})

        if should_stop and (reason := should_stop(stats)):   # budgets, no progress...
            return f"Stopped early: {reason}", messages, stats

    return (f"Stopped: reached max_iterations={max_iterations} without a final answer.",
            messages, stats)

if __name__ == "__main__":
    from ch03_tools import TOOLS, run_tool
    answer, _, stats = run_agent(
        "How many days until July 4 next, and what weekday will it be?",
        TOOLS, run_tool)
    print("\nANSWER:", answer)
    print("STATS:", stats)
