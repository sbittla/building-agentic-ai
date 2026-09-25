"""Local model adapter: lets the book's code use a free local model (Ollama) unchanged.

The course code talks to the Claude API through the Anthropic SDK. Ollama speaks the same
Messages API for the basics (messages, system prompts, tools, tool results, streaming,
thinking), so most examples run as they are. This small proxy sits between the SDK and
Ollama and fills the gaps:

  * tool_choice (forcing a tool)  -> an instruction in the system prompt, then up to two
                                     retries if the model answers without calling the tool
  * structured outputs            -> a forced "json_response" tool whose input is checked
    (output_config.format)           against the schema and returned as JSON text
  * cache_control, effort, metadata and other Claude-only fields -> removed
  * thinking {"type": "adaptive"} -> ordinary thinking
  * count_tokens                  -> an estimate (about 4 characters per token)
  * server-side Claude features   -> a clear error that says the exercise needs Claude
    (tool search, code execution, web search, Agent Skills, Managed Agents, batches, files)

Start it with `./course.sh local up` (it runs as the `local-adapter` service).
Settings (in .env):  OLLAMA_URL, LOCAL_THINKING=auto|off
"""
import contextlib
import json
import os

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

OLLAMA = os.environ.get("OLLAMA_URL", "http://local-model:11434").rstrip("/")
THINKING = os.environ.get("LOCAL_THINKING", "auto").lower()      # auto | off
RETRIES = 2                                                      # extra tries for forced tools
TIMEOUT = httpx.Timeout(900.0, connect=10.0)                     # CPUs can be slow
NEEDS_CLAUDE = ("needs Claude, not the local model. Set PROVIDER=claude in .env to run it "
                "(Appendix H of the book lists which exercises need Claude).")
DROP = ("metadata", "service_tier", "context_management", "container", "mcp_servers",
        "betas", "inference_geo")
JSON_TOOL = "json_response"


def error(status, message, kind="invalid_request_error"):
    return JSONResponse({"type": "error", "error": {"type": kind, "message": message}},
                        status_code=status)


def strip_cache(value):
    """Remove every cache_control key, however deeply nested (Ollama has no prompt cache)."""
    if isinstance(value, dict):
        return {k: strip_cache(v) for k, v in value.items() if k != "cache_control"}
    if isinstance(value, list):
        return [strip_cache(v) for v in value]
    return value


def claude_only_feature(body):
    """Name the Claude-only feature a request uses, or None."""
    for tool in body.get("tools") or []:
        if tool.get("defer_loading"):
            return "Tool search (defer_loading) runs on Anthropic's servers and"
        if tool.get("allowed_callers"):
            return "Programmatic tool calling runs on Anthropic's servers and"
        kind = tool.get("type")
        if kind and kind != "custom":
            return f"The server tool '{kind}' runs on Anthropic's servers and"
    if body.get("container") or body.get("mcp_servers"):
        return "This request uses Anthropic's code-execution container or MCP connector and"
    return None


def add_system(body, text):
    system = body.get("system")
    if not system:
        body["system"] = text
    elif isinstance(system, str):
        body["system"] = system + "\n\n" + text
    else:
        body["system"] = list(system) + [{"type": "text", "text": text}]


def prepare(body):
    """Turn a Claude request into one Ollama accepts. Returns (body, forced tool, schema)."""
    body = strip_cache(dict(body))
    body.pop("cache_control", None)
    forced, schema = None, None

    choice = body.pop("tool_choice", None) or {}
    if choice.get("type") == "tool":
        forced = choice["name"]
    elif choice.get("type") == "any":
        forced = "*"
    elif choice.get("type") == "none":
        add_system(body, "Do not call any tools in this reply. Answer in plain text.")

    config = body.pop("output_config", None) or {}
    fmt = config.get("format") or body.pop("output_format", None)
    if fmt and fmt.get("type") == "json_schema":
        schema = fmt["schema"]
        body["tools"] = [*(body.get("tools") or []),
                         {"name": JSON_TOOL, "input_schema": schema,
                          "description": "Give your final answer by calling this tool. "
                                         "Its input must match the schema exactly."}]
        forced = JSON_TOOL

    for key in DROP:
        body.pop(key, None)

    thinking = body.get("thinking")
    if isinstance(thinking, dict) and thinking.get("type") == "adaptive":
        budget = max(1024, min(int(body.get("max_tokens", 4096)) // 2, 8000))
        body["thinking"] = {"type": "enabled", "budget_tokens": budget}
    if THINKING == "off":
        body["thinking"] = {"type": "disabled"}

    if forced == "*":
        add_system(body, "You must reply by calling one of the provided tools.")
    elif forced:
        add_system(body, f"You must reply by calling the `{forced}` tool. Do not answer in text.")
    return body, forced, schema


def patch_usage(message):
    usage = message.setdefault("usage", {})
    for key in ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                "cache_read_input_tokens"):
        usage[key] = usage.get(key) or 0
    return message


def schema_problem(value, schema):
    """A short description of why `value` doesn't match `schema`, or None."""
    try:
        import jsonschema
        jsonschema.validate(value, schema)
        return None
    except ImportError:
        return None
    except Exception as exc:                     # jsonschema.ValidationError
        return str(getattr(exc, "message", exc))[:300]


async def post(client, body):
    try:
        r = await client.post(f"{OLLAMA}/v1/messages", json={**body, "stream": False})
    except httpx.HTTPError as exc:
        return 503, {"type": "error", "error": {"type": "api_error", "message":
                     f"Can't reach the local model at {OLLAMA} ({type(exc).__name__}). "
                     "Start it with:  ./course.sh local up"}}
    try:
        data = r.json()
    except ValueError:
        data = {"type": "error", "error": {"type": "api_error", "message": r.text[:500]}}
    if r.status_code == 404 and "not found" in json.dumps(data).lower():
        data = {"type": "error", "error": {"type": "not_found_error", "message":
                f"The model '{body.get('model')}' isn't downloaded yet. Run:  ./course.sh local up"}}
    return r.status_code, data


async def create(client, body, forced, schema):
    """One Messages API call, retrying until a forced tool is called (or giving up)."""
    messages = list(body["messages"])
    for attempt in range(RETRIES + 1):
        status, reply = await post(client, {**body, "messages": messages})
        if status != 200:
            return status, reply
        if not forced:
            return 200, patch_usage(reply)
        content = reply.get("content") or []
        calls = [b for b in content if b.get("type") == "tool_use"
                 and (forced == "*" or b.get("name") == forced)]
        problem = None
        if calls:
            call = calls[0]
            if isinstance(call.get("input"), str):           # some models send JSON as text
                try:
                    call["input"] = json.loads(call["input"])
                except ValueError:
                    problem = "the input was not valid JSON"
            if schema and not problem:
                problem = schema_problem(call["input"], schema)
            if not problem:
                kept = [b for b in content if b.get("type") in ("thinking", "redacted_thinking")]
                if schema:                                    # structured output: JSON text
                    reply["content"] = kept + [{"type": "text", "text": json.dumps(call["input"])}]
                    reply["stop_reason"] = "end_turn"
                else:                                         # forced tool: exactly one call
                    text = [b for b in content if b.get("type") == "text"]
                    reply["content"] = kept + text + [call]
                    reply["stop_reason"] = "tool_use"
                return 200, patch_usage(reply)
        name = "one of the tools" if forced == "*" else f"the `{forced}` tool"
        said = [b for b in content if b.get("type") == "text"] or [{"type": "text", "text": "(no answer)"}]
        nudge = (f"That wasn't valid: {problem}. Call {name} again with input that matches its schema."
                 if problem else f"Call {name} now. Don't answer in text.")
        if calls:        # keep the history valid: every tool_use needs a tool_result
            said = [calls[0]]
            nudge = [{"type": "tool_result", "tool_use_id": calls[0]["id"], "is_error": True,
                      "content": nudge}]
        messages = messages + [{"role": "assistant", "content": said},
                               {"role": "user", "content": nudge}]
    return 422, {"type": "error", "error": {"type": "invalid_request_error", "message":
                 f"The local model didn't call {forced if forced != '*' else 'a tool'} correctly "
                 f"after {RETRIES + 1} tries. Try again, or use Claude for this exercise."}}


def as_events(message):
    """Replay a finished message as the server-sent events a streaming call expects."""
    def ev(name, data):
        return f"event: {name}\ndata: {json.dumps(data)}\n\n"
    start = {**message, "content": [], "stop_reason": None}
    yield ev("message_start", {"type": "message_start", "message": start})
    for i, block in enumerate(message.get("content") or []):
        kind = block.get("type")
        if kind == "text":
            yield ev("content_block_start", {"type": "content_block_start", "index": i,
                                             "content_block": {"type": "text", "text": ""}})
            yield ev("content_block_delta", {"type": "content_block_delta", "index": i,
                                             "delta": {"type": "text_delta", "text": block["text"]}})
        elif kind == "tool_use":
            yield ev("content_block_start", {"type": "content_block_start", "index": i,
                                             "content_block": {**block, "input": {}}})
            yield ev("content_block_delta", {"type": "content_block_delta", "index": i, "delta": {
                "type": "input_json_delta", "partial_json": json.dumps(block.get("input", {}))}})
        elif kind == "thinking":
            yield ev("content_block_start", {"type": "content_block_start", "index": i,
                                             "content_block": {"type": "thinking", "thinking": "",
                                                               "signature": ""}})
            yield ev("content_block_delta", {"type": "content_block_delta", "index": i, "delta": {
                "type": "thinking_delta", "thinking": block.get("thinking", "")}})
            yield ev("content_block_delta", {"type": "content_block_delta", "index": i, "delta": {
                "type": "signature_delta", "signature": block.get("signature") or "local"}})
        else:
            continue
        yield ev("content_block_stop", {"type": "content_block_stop", "index": i})
    yield ev("message_delta", {"type": "message_delta",
                               "delta": {"stop_reason": message.get("stop_reason"),
                                         "stop_sequence": None},
                               "usage": {"output_tokens": message["usage"]["output_tokens"]}})
    yield ev("message_stop", {"type": "message_stop"})


async def messages(request: Request):
    try:
        body = await request.json()
    except ValueError:
        return error(400, "The request body is not valid JSON.")
    feature = claude_only_feature(body)
    if feature:
        return error(400, f"{feature} {NEEDS_CLAUDE}")
    wants_stream = bool(body.get("stream"))
    body, forced, schema = prepare(body)
    client = request.app.state.client

    if wants_stream and not forced:              # nothing to fix afterwards: stream it through
        req = client.build_request("POST", f"{OLLAMA}/v1/messages", json={**body, "stream": True})
        try:
            upstream = await client.send(req, stream=True)
        except httpx.HTTPError as exc:
            return error(503, f"Can't reach the local model at {OLLAMA} ({type(exc).__name__}). "
                              "Start it with:  ./course.sh local up", "api_error")
        if upstream.status_code != 200:
            text = (await upstream.aread()).decode(errors="replace")
            await upstream.aclose()
            return error(upstream.status_code, text[:500], "api_error")

        async def relay():
            try:
                async for chunk in upstream.aiter_raw():
                    yield chunk
            finally:
                await upstream.aclose()
        return StreamingResponse(relay(), media_type="text/event-stream")

    status, reply = await create(client, body, forced, schema)
    if status != 200:
        return JSONResponse(reply, status_code=status)
    if wants_stream:
        return StreamingResponse(as_events(reply), media_type="text/event-stream")
    return JSONResponse(reply)


async def count_tokens(request: Request):
    body = await request.json()
    chars = len(json.dumps([body.get("system", ""), body.get("messages", []), body.get("tools", [])]))
    return JSONResponse({"input_tokens": max(1, chars // 4)})


async def health(request: Request):
    try:
        r = await request.app.state.client.get(f"{OLLAMA}/api/tags")
        models = [m["name"] for m in r.json().get("models", [])]
        return JSONResponse({"ok": True, "ollama": OLLAMA, "models": models})
    except Exception as exc:
        return JSONResponse({"ok": False, "ollama": OLLAMA, "error": type(exc).__name__},
                            status_code=503)


async def claude_only(request: Request):
    return error(400, f"The endpoint {request.url.path} is a Claude Platform feature (for example "
                      f"Managed Agents, Agent Skills, Files or Batches) and {NEEDS_CLAUDE}")


@contextlib.asynccontextmanager
async def lifespan(app):
    app.state.client = httpx.AsyncClient(timeout=TIMEOUT)
    yield
    await app.state.client.aclose()


app = Starlette(
    routes=[
        Route("/v1/messages", messages, methods=["POST"]),
        Route("/v1/messages/count_tokens", count_tokens, methods=["POST"]),
        Route("/health", health),
        Route("/{path:path}", claude_only, methods=["GET", "POST", "PUT", "PATCH", "DELETE"]),
    ],
    lifespan=lifespan,
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.environ.get("ADAPTER_HOST", "0.0.0.0"),
                port=int(os.environ.get("ADAPTER_PORT", "8787")), log_level="warning")
