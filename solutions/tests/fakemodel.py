"""A scriptable stand-in for the Anthropic client, so solutions run with no API key.

Each test sets a script: a list whose items are either a list of content blocks,
or a function(kwargs) -> list of blocks (to react to what the code sent).
Every request is recorded in .calls so tests can check tools, tool_choice, etc.
"""
import itertools
from types import SimpleNamespace as S

_ids = itertools.count(1)

def tool(name, inp):
    return S(type="tool_use", id=f"toolu_{next(_ids):04d}", name=name, input=inp)

def text(t):
    return S(type="text", text=t)

def thinking():
    """Claude Sonnet 5 thinks by default, and with display "omitted" the reply STARTS with an
    empty thinking block. Code that reads content[0].text breaks on the real model, so the
    fake does the same."""
    return S(type="thinking", thinking="", signature="sig-fake")

class APIError400(Exception):
    """What the real API returns for requests Claude Sonnet 5 rejects."""

class ScriptExhausted(AssertionError):
    pass

class FakeModel:
    def __init__(self):
        self.reset()

    def reset(self, script=None, default=None):
        self.script = list(script or [])
        self.default = default            # used when the script runs out
        self.calls = []

    def respond(self, kw):
        self.calls.append({**kw, "messages": list(kw.get("messages", []))})  # snapshot
        msgs = kw.get("messages", [])
        # Requests Claude Sonnet 5 rejects with a 400 error:
        for p in ("temperature", "top_p", "top_k"):
            if kw.get(p) is not None:
                raise APIError400(f"{p} is not supported on this model")
        th = kw.get("thinking") or {}
        if th.get("type") == "enabled":
            raise APIError400("manual extended thinking (budget_tokens) was removed; use adaptive")
        if msgs and msgs[-1]["role"] == "assistant":        # allowed only to resume a pause_turn
            last = msgs[-1]["content"]
            if isinstance(last, str) or not any(getattr(b, "type", "") == "server_tool_use" for b in last):
                raise APIError400("prefilling the assistant message is not supported")
        # The real API rejects a tool_use without a matching tool_result: check it.
        for a, b in zip(msgs, msgs[1:]):
            if a["role"] == "assistant" and isinstance(a["content"], list):
                ids = {c.id for c in a["content"] if getattr(c, "type", "") == "tool_use"}
                if ids:
                    got = {c["tool_use_id"] for c in b["content"]
                           if isinstance(c, dict) and c.get("type") == "tool_result"}
                    assert ids == got, f"tool_use ids {ids} != tool_result ids {got}"
        if self.script:
            item = self.script.pop(0)
        elif self.default is not None:
            item = self.default
        else:
            raise ScriptExhausted(f"model called more times than scripted ({len(self.calls)})")
        blocks = item(kw) if callable(item) else item
        stop = "tool_use" if any(b.type == "tool_use" for b in blocks) else "end_turn"
        if th.get("type") != "disabled" and not any(b.type == "thinking" for b in blocks):
            blocks = [thinking(), *blocks]
            if kw.get("max_tokens", 4096) < 1024:           # thinking uses up a tiny budget
                blocks, stop = blocks[:1], "max_tokens"
        return S(content=blocks, stop_reason=stop, model="fake-model",
                 usage=S(input_tokens=100, output_tokens=20))

    # --- the shapes the code under test uses ---
    @property
    def messages(self):
        return S(create=lambda **kw: self.respond(kw), stream=lambda **kw: _Stream(self.respond(kw)))

class _Stream:
    """Like client.messages.stream(...): a context manager with .text_stream (the text
    in small pieces) and .get_final_message()."""
    def __init__(self, message):
        self.message = message
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        return False
    @property
    def text_stream(self):
        for b in self.message.content:
            if b.type == "text":
                words = b.text.split(" ")
                for i, w in enumerate(words):
                    yield w + (" " if i < len(words) - 1 else "")
    def get_final_message(self):
        return self.message

class AsyncFacade:
    def __init__(self, fake):
        self.fake = fake

    @property
    def messages(self):
        async def create(**kw):
            return self.fake.respond(kw)
        return S(create=create)

MODEL = FakeModel()

def last_user_text(kw):
    """Text of the latest plain user message (not tool results)."""
    for m in reversed(kw["messages"]):
        if m["role"] == "user" and isinstance(m["content"], str):
            return m["content"]
    return ""

def tool_results(kw):
    """Contents of tool_result blocks in the last user message."""
    last = kw["messages"][-1]
    if last["role"] == "user" and isinstance(last["content"], list):
        return [c["content"] for c in last["content"] if c.get("type") == "tool_result"]
    return []
