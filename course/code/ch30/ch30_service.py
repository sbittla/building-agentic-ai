"""Chapter 30: an agent as a web service. Auth, rate limits, sessions, budgets,
streaming progress, structured logs.
Run:  ./course.sh serve-api   (then open http://localhost:8080/docs)
Needs AGENT_API_KEYS in your .env: the service refuses to start without keys."""
import contextlib
import hashlib
import hmac
import json
import logging
import os
import queue
import sqlite3
import threading
import time
import uuid
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import ch04_agent
import ch08_sql_tools as sql

log = logging.getLogger("agent-api")
logging.basicConfig(level=logging.INFO, format="%(message)s")

# ---------------------------------------------------------------- configuration
# Keys come ONLY from the environment. No default: a service with a built-in key
# is a service anyone who has read this book can call.
API_KEYS = [k.strip() for k in os.environ.get("AGENT_API_KEYS", "").split(",")
            if k.strip()]
RATE_PER_MINUTE = int(os.environ.get("AGENT_RATE_PER_MINUTE", "10"))
MAX_STEPS = int(os.environ.get("AGENT_MAX_STEPS", "8"))
MAX_TOKENS_PER_REQUEST = int(os.environ.get("AGENT_MAX_TOKENS", "40000"))
MAX_HISTORY_MESSAGES = int(os.environ.get("AGENT_MAX_HISTORY", "40"))
DB = os.environ.get("AGENT_SESSIONS_DB", "sessions.db")

@contextlib.asynccontextmanager
async def lifespan(app):
    """Fail CLOSED: refuse to start without API keys, instead of running unprotected."""
    if not API_KEYS:
        raise RuntimeError("AGENT_API_KEYS is not set. Add long random keys to "
                           "your .env, e.g. AGENT_API_KEYS="
                           + uuid.uuid4().hex + uuid.uuid4().hex)
    if any(len(k) < 16 for k in API_KEYS):
        log.warning("Some AGENT_API_KEYS are shorter than 16 characters: "
                    "easy to guess.")
    yield

app = FastAPI(title="Shop analyst agent", version="1.1", lifespan=lifespan)

# ---------------------------------------------------------------- auth
def key_id(key: str) -> str:
    """A fingerprint of a key. Stored and logged INSTEAD of the key itself."""
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def api_key(authorization: str = Header(default="")) -> str:
    """Expect 'Authorization: Bearer <key>'. Returns the caller's key id.
    compare_digest takes the same time wherever the strings differ (no timing attack);
    comparing bytes also copes with non-ASCII input instead of crashing."""
    token = authorization.removeprefix("Bearer ").strip().encode()
    for key in API_KEYS:
        if token and hmac.compare_digest(token, key.encode()):
            return key_id(key)
    raise HTTPException(status_code=401, detail="Missing or invalid API key.")

# ---------------------------------------------------------------- rate limiting
# A token bucket per caller. One process only: with several server processes, keep
# the buckets in Redis or similar.
_buckets: dict = {}
_lock = threading.Lock()

def rate_limit(caller: str = Depends(api_key)) -> str:
    now = time.monotonic()
    with _lock:
        tokens, last = _buckets.get(caller, (RATE_PER_MINUTE, now))
        tokens = min(RATE_PER_MINUTE, tokens + (now - last) * RATE_PER_MINUTE / 60)
        if tokens < 1:
            wait = int((1 - tokens) * 60 / RATE_PER_MINUTE) + 1
            raise HTTPException(status_code=429, detail="Rate limit exceeded.",
                                headers={"Retry-After": str(wait)})
        _buckets[caller] = (tokens - 1, now)
    return caller

# ---------------------------------------------------------------- sessions (SQLite)
def _db():
    con = sqlite3.connect(DB, timeout=10)
    con.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, owner TEXT, "
                "messages TEXT, updated REAL)")
    return con

def _plain(block):
    """SDK content blocks -> JSON-safe dicts, so history can be stored."""
    if isinstance(block, dict):
        return block
    if hasattr(block, "model_dump"):
        return block.model_dump(exclude_none=True)
    d = {"type": block.type}
    for f in ("text", "id", "name", "input"):
        if hasattr(block, f):
            d[f] = getattr(block, f)
    return d

def _serialize(messages):
    return json.dumps([{"role": m["role"],
                        "content": m["content"] if isinstance(m["content"], str)
                        else [_plain(b) for b in m["content"]]} for m in messages])

def bounded(messages, limit=MAX_HISTORY_MESSAGES):
    """Keep at most `limit` messages, cutting only before a plain user message so a
    tool_use is never separated from its tool_result (the rule from chapter 16)."""
    if len(messages) <= limit:
        return messages
    starts = [i for i, m in enumerate(messages)
              if m["role"] == "user" and isinstance(m["content"], str)
              and i >= len(messages) - limit]
    return messages[starts[0]:] if starts else messages[-1:]

def load_session(session_id, owner):
    with contextlib.closing(_db()) as con:
        row = con.execute("SELECT owner, messages FROM sessions WHERE id=?",
                          (session_id,)).fetchone()
    if row is None:
        return []
    # never serve another caller's conversation
    if not hmac.compare_digest(row[0], owner):
        raise HTTPException(status_code=404, detail="No such session.")
    return bounded(json.loads(row[1]))

def save_session(session_id, owner, messages):
    with contextlib.closing(_db()) as con, con:
        con.execute("INSERT OR REPLACE INTO sessions VALUES (?,?,?,?)",
                    (session_id, owner, _serialize(bounded(messages)), time.time()))

_session_locks: dict = {}

@contextlib.contextmanager
def session_lock(session_id):
    """One request per session at a time. Two concurrent requests would both load the
    same history and the second save would silently drop the first one's turn."""
    with _lock:
        lock = _session_locks.setdefault(session_id, threading.Lock())
    if not lock.acquire(timeout=0):
        raise HTTPException(status_code=409,
                            detail="This session is busy; retry shortly.")
    try:
        yield
    finally:
        lock.release()

# ---------------------------------------------------------------- the agent
SYSTEM = sql.SYSTEM + " Keep answers short: the numbers first, then one sentence."

def run(message, history, on_tool=None, cancelled=None):
    def run_tool(name, args):
        out = sql.run_tool(name, args)
        if on_tool:
            on_tool(name, args, out)
        return out

    def should_stop(stats):
        if cancelled is not None and cancelled.is_set():
            return "the client disconnected"
        if stats["input_tokens"] + stats["output_tokens"] > MAX_TOKENS_PER_REQUEST:
            return f"token budget of {MAX_TOKENS_PER_REQUEST} reached"
        return None
    return ch04_agent.run_agent(message, sql.TOOLS, run_tool, system=SYSTEM,
                                messages=history, max_iterations=MAX_STEPS,
                                verbose=False, should_stop=should_stop)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=64)

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    steps: int
    tool_calls: int
    input_tokens: int
    output_tokens: int

@app.get("/health")
def health():
    return {"status": "ok", "model": ch04_agent.MODEL}

@app.post("/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest, caller: str = Depends(rate_limit)):
    request_id, t0 = uuid.uuid4().hex[:8], time.perf_counter()
    session_id = req.session_id or uuid.uuid4().hex
    with session_lock(session_id):
        history = load_session(session_id, caller)
        try:
            answer, messages, stats = run(req.message, history)
        except Exception as exc:
            # model/API failure: log it, return a clean 502
            log.error(json.dumps({"request_id": request_id, "caller": caller,
                                  "error": type(exc).__name__}))
            raise HTTPException(status_code=502,
                                detail="The model service failed; try again.")
        save_session(session_id, caller, messages)
    # no text, no keys
    log.info(json.dumps({"request_id": request_id, "caller": caller,
                         "session": session_id,
                         "ms": round((time.perf_counter() - t0) * 1000), **stats}))
    return ChatResponse(session_id=session_id, answer=answer, steps=stats["steps"],
                        tool_calls=stats["tool_calls"],
                        input_tokens=stats["input_tokens"],
                        output_tokens=stats["output_tokens"])

@app.post("/v1/chat/stream")
def chat_stream(req: ChatRequest, caller: str = Depends(rate_limit)):
    """Server-Sent Events: a `tool` event per tool call, then one `answer` event.
    A comment line every 15 s keeps proxies from closing a quiet connection, and if the
    client goes away the agent stops at its next step instead of spending tokens."""
    request_id, t0 = uuid.uuid4().hex[:8], time.perf_counter()
    session_id = req.session_id or uuid.uuid4().hex
    history = load_session(session_id, caller)
    events: queue.Queue = queue.Queue()
    cancelled = threading.Event()

    def worker():
        try:
            with session_lock(session_id):
                answer, messages, stats = run(
                    req.message, history, cancelled=cancelled,
                    on_tool=lambda n, a, o: events.put(
                        ("tool", {"name": n, "input": a, "result_preview": o[:200]})))
                save_session(session_id, caller, messages)
            log.info(json.dumps({"request_id": request_id, "caller": caller,
                                 "stream": True,
                                 "ms": round((time.perf_counter() - t0) * 1000),
                                 **stats}))
            events.put(("answer", {"session_id": session_id, "answer": answer,
                                   **stats}))
        except HTTPException as exc:
            events.put(("error", {"error": exc.detail}))
        except Exception as exc:
            log.error(json.dumps({"request_id": request_id,
                                  "error": type(exc).__name__}))
            events.put(("error", {"error": type(exc).__name__}))
        events.put(None)

    threading.Thread(target=worker, daemon=True).start()

    def stream():
        try:
            while True:
                try:
                    item = events.get(timeout=15)
                except queue.Empty:
                    # an SSE comment: clients ignore it
                    yield ": keep-alive\n\n"
                    continue
                if item is None:
                    return
                name, data = item
                yield f"event: {name}\ndata: {json.dumps(data)}\n\n"
        finally:
            # runs when the client disconnects too
            cancelled.set()
    return StreamingResponse(stream(), media_type="text/event-stream")
