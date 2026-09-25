from types import SimpleNamespace as S
import itertools
_id = itertools.count(1)
def tool(name, inp): return S(type="tool_use", id=f"toolu_{next(_id)}", name=name, input=inp)
def text(t): return S(type="text", text=t)
class Fake:
    def __init__(self, script): self.script = list(script)
    def _next(self, kw):
        msgs = kw["messages"]
        for a, b in zip(msgs, msgs[1:]):
            if a["role"] == "assistant":
                ids = {c.id for c in a["content"] if getattr(c, "type", "") == "tool_use"}
                if ids:
                    assert ids == {c["tool_use_id"] for c in b["content"]}
        blocks = self.script.pop(0)
        stop = "tool_use" if any(b.type == "tool_use" for b in blocks) else "end_turn"
        return S(content=blocks, stop_reason=stop, usage=S(input_tokens=100, output_tokens=20))
    @property
    def messages(self): return S(create=lambda **kw: self._next(kw))
class AFake(Fake):
    @property
    def messages(self):
        async def create(**kw): return self._next(kw)
        return S(create=create)
