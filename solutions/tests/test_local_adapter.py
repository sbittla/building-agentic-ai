"""The local model adapter (course/local_adapter.py), end to end and offline: the real Anthropic
SDK -> the adapter -> a stand-in for Ollama that behaves like a small local model (it rejects
Claude-only fields and sometimes answers in text when a tool is required)."""
import importlib.util
import json
import os
import socket
import threading
import time
from pathlib import Path

import pytest

CODE = Path(os.environ.get("COURSE_CODE", "/opt/course/code"))
uvicorn = pytest.importorskip("uvicorn")
from anthropic._client import Anthropic as RealAnthropic          # conftest fakes the public one
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

CALLS = []


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _serve(app, port):
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(100):
        if server.started:
            return server
        time.sleep(0.05)
    raise RuntimeError("server did not start")


# ------------------------------------------------------------ a stand-in for Ollama
def _reply(body):
    """Like a small local model: ignores nothing, rejects Claude-only fields, and answers
    in text the FIRST time a system prompt demands a tool."""
    for field in ("tool_choice", "output_config", "cache_control", "metadata"):
        if field in body:
            return 400, {"type": "error", "error": {"type": "invalid_request_error",
                                                    "message": f"unsupported field {field}"}}
    if "cache_control" in json.dumps(body):
        return 400, {"type": "error", "error": {"message": "nested cache_control"}}
    if body["model"] != "qwen3.5:9b":
        return 404, {"error": f"model '{body['model']}' not found"}
    system = body.get("system") if isinstance(body.get("system"), str) else json.dumps(body.get("system"))
    must = "You must reply by calling the `" in (system or "")
    nudged = any("Call the `" in json.dumps(m["content"]) or "wasn't valid" in json.dumps(m["content"])
                 for m in body["messages"] if m["role"] == "user")
    content = [{"type": "thinking", "thinking": "Let me think.", "signature": ""}]
    if must and nudged:
        name = system.split("You must reply by calling the `")[1].split("`")[0]
        tool = next(t for t in body["tools"] if t["name"] == name)
        props = tool["input_schema"].get("properties", {})
        args = {k: (3 if v.get("type") == "integer" else "Ada") for k, v in props.items()}
        content.append({"type": "tool_use", "id": "toolu_local1", "name": name, "input": args})
        stop = "tool_use"
    else:
        content.append({"type": "text", "text": "Hello from the local model."})
        stop = "end_turn"
    return 200, {"id": "msg_local", "type": "message", "role": "assistant", "model": body["model"],
                 "content": content, "stop_reason": stop, "stop_sequence": None,
                 "usage": {"input_tokens": 12, "output_tokens": 7}}


async def _ollama(request: Request):
    body = await request.json()
    CALLS.append(body)
    status, data = _reply(body)
    if status == 200 and body.get("stream"):
        from local_adapter import as_events
        return StreamingResponse(as_events(data), media_type="text/event-stream")
    return JSONResponse(data, status_code=status)


async def _tags(request):
    return JSONResponse({"models": [{"name": "qwen3.5:9b"}]})


@pytest.fixture(scope="module")
def client():
    ollama_port, adapter_port = _free_port(), _free_port()
    os.environ["OLLAMA_URL"] = f"http://127.0.0.1:{ollama_port}"
    spec = importlib.util.spec_from_file_location("local_adapter", CODE.parent / "local_adapter.py")
    adapter = importlib.util.module_from_spec(spec)
    import sys
    sys.modules["local_adapter"] = adapter
    spec.loader.exec_module(adapter)
    fake = Starlette(routes=[Route("/v1/messages", _ollama, methods=["POST"]),
                             Route("/api/tags", _tags)])
    s1, s2 = _serve(fake, ollama_port), _serve(adapter.app, adapter_port)
    yield RealAnthropic(api_key="sk-local-ollama", base_url=f"http://127.0.0.1:{adapter_port}",
                        max_retries=0)
    s1.should_exit = s2.should_exit = True


def test_plain_call_strips_cache_control_and_fills_usage(client):
    r = client.messages.create(
        model="qwen3.5:9b", max_tokens=200, metadata={"user_id": "x"},
        system=[{"type": "text", "text": "Be brief.", "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": "Hi"}])
    assert [b.type for b in r.content] == ["thinking", "text"]
    assert r.usage.cache_read_input_tokens == 0 and r.usage.input_tokens == 12


def test_forced_tool_is_retried_until_called(client):
    CALLS.clear()
    tools = [{"name": "record_contact", "description": "Save a contact",
              "input_schema": {"type": "object", "properties": {"name": {"type": "string"}},
                               "required": ["name"]}}]
    r = client.messages.create(model="qwen3.5:9b", max_tokens=500, tools=tools,
                               tool_choice={"type": "tool", "name": "record_contact"},
                               messages=[{"role": "user", "content": "Ada, ada@example.com"}])
    call = next(b for b in r.content if b.type == "tool_use")
    assert call.name == "record_contact" and call.input == {"name": "Ada"}
    assert r.stop_reason == "tool_use" and len(CALLS) == 2       # answered in text once, then nudged


def test_structured_output_becomes_json_text(client):
    schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
              "required": ["name", "age"], "additionalProperties": False}
    r = client.messages.create(model="qwen3.5:9b", max_tokens=500,
                               output_config={"format": {"type": "json_schema", "schema": schema}},
                               messages=[{"role": "user", "content": "Ada is 3."}])
    text = next(b.text for b in r.content if b.type == "text")
    assert json.loads(text) == {"name": "Ada", "age": 3} and r.stop_reason == "end_turn"


def test_streaming_passthrough_and_replayed(client):
    with client.messages.stream(model="qwen3.5:9b", max_tokens=100,
                                messages=[{"role": "user", "content": "Hi"}]) as s:
        assert "".join(s.text_stream) == "Hello from the local model."
    tools = [{"name": "pick", "input_schema": {"type": "object", "properties": {"n": {"type": "integer"}}}}]
    with client.messages.stream(model="qwen3.5:9b", max_tokens=100, tools=tools,
                                tool_choice={"type": "tool", "name": "pick"},
                                messages=[{"role": "user", "content": "Pick"}]) as s:
        final = s.get_final_message()
    assert next(b for b in final.content if b.type == "tool_use").input == {"n": 3}


def test_count_tokens_is_estimated(client):
    n = client.messages.count_tokens(model="qwen3.5:9b",
                                     messages=[{"role": "user", "content": "x" * 400}])
    assert 90 < n.input_tokens < 140


def test_claude_only_features_explain_themselves(client):
    import anthropic
    with pytest.raises(anthropic.BadRequestError, match="needs Claude"):
        client.messages.create(model="qwen3.5:9b", max_tokens=100,
                               tools=[{"type": "tool_search_tool_bm25_20251119", "name": "tool_search"}],
                               messages=[{"role": "user", "content": "Hi"}])
    with pytest.raises(anthropic.BadRequestError, match="needs Claude"):
        client.post("/v1/agents", body={}, cast_to=object)


def test_missing_model_says_how_to_download_it(client):
    import anthropic
    with pytest.raises(anthropic.NotFoundError, match="local up"):
        client.messages.create(model="qwen3.5:27b", max_tokens=10,
                               messages=[{"role": "user", "content": "Hi"}])
