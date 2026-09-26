"""Chapter 30: calling the agent service and the remote MCP server as a client would."""
import asyncio
import json
import os
import sys
import socket
import httpx

def _address(container, port, path=""):
    """Inside the course, `serve-api` and `serve-mcp` run in containers named
    agentic-ai-api / agentic-ai-mcp, reachable by name from other course
    containers. Anywhere else, use localhost."""
    try:
        socket.gethostbyname(container)
        return f"http://{container}:{port}{path}"
    except OSError:
        return f"http://127.0.0.1:{port}{path}"

API = os.environ.get("AGENT_API_URL") or _address("agentic-ai-api", 8080)
MCP_URL = os.environ.get("MCP_URL") or _address("agentic-ai-mcp", 8000, "/mcp")
# Your key comes from .env: AGENT_API_KEY, or the first of the service's AGENT_API_KEYS.
KEY = os.environ.get("AGENT_API_KEY") or os.environ.get("AGENT_API_KEYS", "").split(",")[0].strip()

def chat(message, session_id=None):
    r = httpx.post(f"{API}/v1/chat", json={"message": message, "session_id": session_id},
                   headers={"Authorization": f"Bearer {KEY}"}, timeout=120)
    r.raise_for_status()
    return r.json()

def chat_stream(message):
    with httpx.stream("POST", f"{API}/v1/chat/stream", json={"message": message},
                      headers={"Authorization": f"Bearer {KEY}"}, timeout=120) as r:
        event = None
        for line in r.iter_lines():
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: "):
                print(f"[{event}] {json.loads(line[6:])}")

async def remote_tools(url=MCP_URL, token=None):
    from mcp import Client
    from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client
    http = create_mcp_http_client(headers={"Authorization": f"Bearer {token or os.environ.get('MCP_TOKEN', '')}"})
    async with Client(streamable_http_client(url, http_client=http)) as c:
        return [t.name for t in (await c.list_tools()).tools]

def chat_words(message):
    """Exercise 30.4: print the answer as it streams from /v1/chat/stream_text."""
    with httpx.stream("POST", f"{API}/v1/chat/stream_text", json={"message": message},
                      headers={"Authorization": f"Bearer {KEY}"}, timeout=120) as r:
        if r.status_code == 404:
            print("The service has no /v1/chat/stream_text endpoint yet: that's exercise 30.4.")
            return
        for piece in r.iter_text():
            print(piece, end="", flush=True)
        print()

def limits(n=4):
    """Exercise 30.3: n quick requests, then one with a wrong key. Prints status codes."""
    for i in range(n):
        r = httpx.post(f"{API}/v1/chat", json={"message": "Say hi in one word."},
                       headers={"Authorization": f"Bearer {KEY}"}, timeout=120)
        print(f"request {i + 1}: {r.status_code}  Retry-After={r.headers.get('retry-after')}")
    r = httpx.post(f"{API}/v1/chat", json={"message": "hi"},
                   headers={"Authorization": "Bearer wrong-key"}, timeout=30)
    print(f"wrong key: {r.status_code}")

if __name__ == "__main__":
    # python ch30_client.py           two chat turns in one session
    # python ch30_client.py stream    watch progress events arrive
    # python ch30_client.py words     stream the answer text (after exercise 30.4)
    # python ch30_client.py limits    trigger 429 and 401 (exercise 30.3)
    # python ch30_client.py mcp       list the remote MCP server's tools
    mode = sys.argv[1] if len(sys.argv) > 1 else "chat"
    if mode == "mcp":
        try:
            print(asyncio.run(remote_tools()))
        except Exception as exc:
            sys.exit(f"Couldn't use the MCP server at {MCP_URL} ({type(exc).__name__}). "
                     "Is it running? Start it with ./course.sh serve-mcp")
    elif mode == "stream":
        chat_stream("Which product category earns the most revenue?")
    elif mode == "words":
        chat_words("Which product category earns the most revenue? Explain in two sentences.")
    elif mode == "limits":
        limits()
    else:
        try:
            httpx.get(f"{API}/health", timeout=5)
        except httpx.HTTPError:
            sys.exit(f"Couldn't reach the agent API at {API}. Start it with ./course.sh serve-api")
        first = chat("How many orders are there?")
        print(first)
        print(chat("And how many of them were cancelled?", first["session_id"]))
