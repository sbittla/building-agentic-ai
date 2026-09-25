"""Loaded automatically when this folder is on PYTHONPATH and FAKE_MODEL=1: replaces
the Anthropic client with a generic offline stand-in, so any course script can be
run end to end without an API key. It answers with text, or fills a forced tool."""
import os
if os.environ.get("FAKE_MODEL") == "1":
    import itertools
    from types import SimpleNamespace as S
    import anthropic

    _ids = itertools.count(1)

    def _example(schema):
        t = schema.get("type")
        if isinstance(t, list):
            t = next((x for x in t if x != "null"), "string")
        if "enum" in schema:
            return schema["enum"][0]
        if t == "object":
            props = schema.get("properties", {})
            return {k: _example(v) for k, v in props.items()}
        if t == "array":
            n = max(schema.get("minItems", 2), 1)
            return [_example(schema.get("items", {"type": "string"})) for _ in range(n)]
        return {"integer": 3, "number": 3.0, "boolean": True}.get(t, "offline example")

    def _respond(kw):
        forced = (kw.get("tool_choice") or {}).get("name")
        if forced:
            spec = next(t for t in kw["tools"] if t["name"] == forced)
            content = [S(type="tool_use", id=f"toolu_{next(_ids)}", name=forced,
                         input=_example(spec["input_schema"]))]
            stop = "tool_use"
        elif ((kw.get("output_config") or {}).get("format") or {}).get("type") == "json_schema":
            import json
            schema = kw["output_config"]["format"]["schema"]
            content = [S(type="text", text=json.dumps(_example(schema)))]
            stop = "end_turn"
        else:
            content = [S(type="text", text="OK (offline stand-in model)\n```sql\nSELECT 1\n```")]
            stop = "end_turn"
        if (kw.get("thinking") or {}).get("type") != "disabled":     # like Claude Sonnet 5
            content = [S(type="thinking", thinking="", signature="sig"), *content]
        return S(content=content, stop_reason=stop, model="offline",
                 usage=S(input_tokens=10, output_tokens=5))

    class _Fake:
        messages = S(create=lambda **kw: _respond(kw))

    class _AsyncFake:
        async def _create(self, **kw):
            return _respond(kw)
        @property
        def messages(self):
            return S(create=self._create)

    anthropic.Anthropic = lambda *a, **k: _Fake()
    anthropic.AsyncAnthropic = lambda *a, **k: _AsyncFake()
