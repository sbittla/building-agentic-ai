"""Exercise 19.5 (solution): stream the answer TEXT as it's generated.

Run it instead of the original:  ./course.sh python -m uvicorn sol_ch19_service:app --host 0.0.0.0 --port 8080
Every model call is streamed; text is forwarded to the client as it arrives, and tool
steps run in between exactly as in the chapter 4 loop."""
import json
import uuid
from fastapi import Depends
from fastapi.responses import StreamingResponse
import ch04_agent
import ch08_sql_tools as sql
from ch19_service import (MAX_STEPS, SYSTEM, ChatRequest, app, load_session,  # noqa: F401
                          rate_limit, save_session, session_lock)

def stream_agent(message, history):
    """A generator: yields text pieces; tool calls run between model calls."""
    messages = list(history) + [{"role": "user", "content": message}]
    for _ in range(MAX_STEPS):
        with ch04_agent.get_client().messages.stream(model=ch04_agent.MODEL, max_tokens=4096,
                                               system=SYSTEM, tools=sql.TOOLS,
                                               messages=messages) as s:
            for text in s.text_stream:
                yield text
            final = s.get_final_message()
        messages.append({"role": "assistant", "content": final.content})
        action, note = ch04_agent.next_action(final)
        if action == "stop":
            yield f"\n[stopped: {note}]"
        if action != "tools":
            return messages
        yield "\n"                                           # keep the client's display tidy
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": b.id, "content": sql.run_tool(b.name, b.input)}
            for b in final.content if b.type == "tool_use"]})
    yield "\n[stopped: step limit reached]"
    return messages

@app.post("/v1/chat/stream_text")
def chat_stream_text(req: ChatRequest, key: str = Depends(rate_limit)):
    session_id = req.session_id or uuid.uuid4().hex
    history = load_session(session_id, key)

    def body():
        gen = stream_agent(req.message, history)
        try:
            while True:
                yield next(gen)
        except StopIteration as done:                       # the generator's return value
            if done.value:
                save_session(session_id, key, done.value)
        except Exception as exc:
            yield f"\n[error: {type(exc).__name__}]"
    return StreamingResponse(body(), media_type="text/plain; charset=utf-8",
                             headers={"X-Session-Id": session_id})
