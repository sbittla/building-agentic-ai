"""Exercise 13.8 (host side): the two callbacks a host provides so servers can ask the user
(elicitation) and borrow the host's model (sampling). The host stays in control: the user
sees every request and can refuse it.

Run:  python ex13_8_host.py        (starts ex13_8_trip_server.py over stdio)"""
import asyncio
import json
import os
import sys
from anthropic import AsyncAnthropic
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CreateMessageResult, ElicitResult, ErrorData, TextContent

MODEL = os.environ.get("MODEL", "claude-sonnet-5")

def make_elicitation_callback(ask=input):
    """Show the server's question and fill each field from the user. 'ask' is injectable
    so tests can answer without a keyboard."""
    async def on_elicit(context, params) -> ElicitResult:
        print(f"\n[server asks] {params.message}")
        if ask("Answer? [y/n] ").strip().lower() != "y":
            return ElicitResult(action="decline")
        content = {}
        for name, prop in params.requested_schema.get("properties", {}).items():
            raw = ask(f"  {prop.get('description', name)}: ").strip()
            content[name] = int(raw) if prop.get("type") == "integer" else raw
        return ElicitResult(action="accept", content=content)
    return on_elicit

def make_sampling_callback(generate=None, ask=input):
    """Let a server use the host's model, but only after the user approves the request."""
    client = None
    async def default_generate(system, messages, max_tokens):
        nonlocal client
        client = client or AsyncAnthropic()
        r = await client.messages.create(model=MODEL, max_tokens=max_tokens, system=system or "",
                                         messages=messages)
        return "".join(b.text for b in r.content if b.type == "text")
    generate = generate or default_generate

    async def on_sample(context, params):
        messages = [{"role": m.role, "content": m.content.text} for m in params.messages
                    if isinstance(m.content, TextContent)]
        print(f"\n[server wants the model] {json.dumps(messages)[:300]}")
        if ask("Allow this model call? [y/n] ").strip().lower() != "y":
            return ErrorData(code=-1, message="The user refused the sampling request.")
        max_tokens = min(params.max_tokens, 1000)          # the host caps the cost, not the server
        text = await generate(params.system_prompt, messages, max_tokens)
        return CreateMessageResult(role="assistant", model=MODEL, stop_reason="endTurn",
                                   content=TextContent(type="text", text=text))
    return on_sample

async def main():
    here = os.path.dirname(os.path.abspath(__file__))
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(here, "ex13_8_trip_server.py")])
    async with Client(stdio_client(params), elicitation_callback=make_elicitation_callback(),
                      sampling_callback=make_sampling_callback()) as client:
        r = await client.call_tool("book_trip", {"city": "Lisbon"})
        print("\n[tool result]", r.content[0].text)
        r = await client.call_tool("summarize_notes", {"notes": "Tram 28 is crowded before 10am. "
                                   "Pastel de nata at Manteigaria. Sintra needs a full day."})
        print("\n[tool result]", r.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
