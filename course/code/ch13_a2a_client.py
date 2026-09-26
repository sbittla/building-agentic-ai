"""Chapter 13: an A2A client. It finds a remote agent through its agent card, sends it
a task, prints the progress events and the answer, and shows how a coordinator can
use a remote A2A agent as an ordinary tool.

  ./course.sh python ch13_a2a_client.py                  local copy of the analyst
  ./course.sh python ch13_a2a_client.py --coordinator    a local agent delegates to it
  ./course.sh python ch13_a2a_client.py --url http://agentic-ai-a2a:9999 "Question?"
                                                    talks to ./course.sh serve-a2a"""
import asyncio
import os
import sys
import threading
import time

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_stream_response_text, new_text_message
from a2a.types import Role, SendMessageRequest

TOKEN = os.environ.get("A2A_TOKEN", "")

# ------------------------------------------------------------ 1. discover and ask
async def ask_remote_agent(url: str, question: str, show: bool = True) -> str:
    """Send one question to the A2A agent at `url`; return its answer text."""
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    async with httpx.AsyncClient(headers=headers, timeout=900) as http:
        config = ClientConfig(httpx_client=http)
        client = await create_client(url, client_config=config)   # reads the card
        message = new_text_message(question, role=Role.ROLE_USER)
        answer, state = [], "unknown"
        async for event in client.send_message(SendMessageRequest(message=message)):
            kind = event.WhichOneof("payload")   # task, status_update, artifact_update
            text = get_stream_response_text(event).strip()
            if kind == "task" and show:
                print(f"  [task]   {event.task.id}")
            elif kind == "status_update":
                state = event.status_update.status.state
                if show and text:
                    print(f"  [status] {text}")
            elif kind in ("artifact_update", "message") and text:
                answer.append(text)
        await client.close()
    if not answer:
        raise RuntimeError(f"The remote agent returned no answer (state {state}).")
    return "\n".join(answer)

async def show_card(url: str) -> None:
    async with httpx.AsyncClient(timeout=30) as http:
        r = await http.get(f"{url.rstrip('/')}/.well-known/agent-card.json")
    card = r.json()
    print(f"Agent: {card['name']} (v{card['version']})\n  {card['description']}")
    for skill in card.get("skills", []):
        print(f"  skill {skill['id']}: {skill['description']}")

# ------------------------------------------------------ 2. a remote agent as a tool
def a2a_tool(url: str, name: str, description: str):
    """Wrap a remote A2A agent as a tool for run_agent. The coordinator doesn't need
    to know it's an agent, on another machine, possibly built by another team."""
    schema = {"type": "object", "required": ["question"],
              "properties": {"question": {"type": "string"}}}
    tool = {"name": name, "description": description, "input_schema": schema}

    def run_tool(tool_name: str, args: dict) -> str:
        try:
            return asyncio.run(ask_remote_agent(url, args["question"], show=False))
        except Exception as exc:                        # errors are text (section 2.6)
            return f"ERROR: {type(exc).__name__}: {exc}"
    return tool, run_tool

def start_local_server(port: int = 9999) -> str:
    """Start the Chapter 13 A2A analyst in this process, for a one-terminal demo."""
    import uvicorn
    os.environ.setdefault("A2A_PUBLIC_URL", f"http://127.0.0.1:{port}")
    from ch13_a2a_server import build_app
    config = uvicorn.Config(build_app(), host="127.0.0.1", port=port,
                            log_level="warning")
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()
    while not server.started:
        time.sleep(0.1)
    return f"http://127.0.0.1:{port}"

if __name__ == "__main__":
    args = sys.argv[1:]
    url = args[args.index("--url") + 1] if "--url" in args else start_local_server()
    words = [a for a in args if not a.startswith("--") and a != url]
    asyncio.run(show_card(url))
    if "--coordinator" in args:
        from ch04_agent import run_agent
        tool, run_tool = a2a_tool(url, "ask_shop_analyst",
                                  "Ask the shop's data analyst agent one question "
                                  "about customers, products, orders or revenue.")
        question = " ".join(words) or "Which city has the most customers?"
        print(f"\nCoordinator: {question}")
        system = "You coordinate specialist agents. Delegate data questions."
        print(run_agent(question, [tool], run_tool, system=system)[0])
    else:
        question = " ".join(words) or "How many orders were cancelled?"
        print(f"\nYou: {question}")
        print("Analyst:", asyncio.run(ask_remote_agent(url, question)))
