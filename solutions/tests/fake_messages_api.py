"""A tiny fake Anthropic Messages API (streaming + non-streaming) for offline tests.
Script: a list of turns; each turn is a list of blocks {"text": ...} or {"tool": name, "input": {...}}."""
import json, threading, itertools
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

class FakeAPI:
    def __init__(self, script, port):
        self.script, self.port, self.requests = list(script), port, []
        self._ids = itertools.count(1)
        app = Starlette(routes=[Route("/v1/messages", self.messages, methods=["POST"]),
                                Route("/v1/messages/count_tokens", self.count, methods=["POST"]),
                                Route("/{path:path}", self.other, methods=["GET", "POST"])])
        self.server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))

    def start(self):
        threading.Thread(target=self.server.run, daemon=True).start()
        import time, socket
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", self.port), 0.2).close(); return self
            except OSError:
                time.sleep(0.1)
        return self

    def stop(self):
        self.server.should_exit = True

    async def other(self, request):
        return JSONResponse({})

    async def count(self, request):
        return JSONResponse({"input_tokens": 100})

    def _blocks(self):
        turn = self.script.pop(0) if self.script else [{"text": "(script exhausted)"}]
        out = []
        for b in turn:
            if "tool" in b:
                out.append({"type": "tool_use", "id": f"toolu_{next(self._ids):04d}", "name": b["tool"], "input": b.get("input", {})})
            else:
                out.append({"type": "text", "text": b["text"]})
        return out

    async def messages(self, request):
        body = await request.json()
        self.requests.append(body)
        # Side requests (titles, summaries) without tools: answer briefly, don't consume the script.
        if not body.get("tools") and len(self.requests) > 1 and self.script:
            blocks = [{"type": "text", "text": "ok"}]
        else:
            blocks = self._blocks()
        stop = "tool_use" if any(b["type"] == "tool_use" for b in blocks) else "end_turn"
        if (body.get("thinking") or {}).get("type") != "disabled":      # Claude Sonnet 5 thinks by default
            blocks = [{"type": "thinking", "thinking": "", "signature": "sig-fake"}, *blocks]
            if body.get("max_tokens", 4096) < 1024:                      # thinking uses up a tiny budget
                blocks, stop = blocks[:1], "max_tokens"
        msg = {"id": f"msg_{next(self._ids)}", "type": "message", "role": "assistant", "model": body.get("model", "x"),
               "content": blocks, "stop_reason": stop, "stop_sequence": None,
               "usage": {"input_tokens": 100, "output_tokens": 20, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}
        if not body.get("stream"):
            return JSONResponse(msg)
        def events():
            def ev(name, data): return f"event: {name}\ndata: {json.dumps(data)}\n\n"
            start = {**msg, "content": [], "stop_reason": None}
            yield ev("message_start", {"type": "message_start", "message": start})
            for i, b in enumerate(blocks):
                if b["type"] == "thinking":
                    yield ev("content_block_start", {"type": "content_block_start", "index": i, "content_block": {"type": "thinking", "thinking": "", "signature": ""}})
                    yield ev("content_block_delta", {"type": "content_block_delta", "index": i, "delta": {"type": "signature_delta", "signature": b["signature"]}})
                elif b["type"] == "text":
                    yield ev("content_block_start", {"type": "content_block_start", "index": i, "content_block": {"type": "text", "text": ""}})
                    yield ev("content_block_delta", {"type": "content_block_delta", "index": i, "delta": {"type": "text_delta", "text": b["text"]}})
                else:
                    yield ev("content_block_start", {"type": "content_block_start", "index": i, "content_block": {**b, "input": {}}})
                    yield ev("content_block_delta", {"type": "content_block_delta", "index": i, "delta": {"type": "input_json_delta", "partial_json": json.dumps(b["input"])}})
                yield ev("content_block_stop", {"type": "content_block_stop", "index": i})
            yield ev("message_delta", {"type": "message_delta", "delta": {"stop_reason": stop, "stop_sequence": None}, "usage": {"output_tokens": 20}})
            yield ev("message_stop", {"type": "message_stop"})
        return StreamingResponse(events(), media_type="text/event-stream")
