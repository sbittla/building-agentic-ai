"""Exercise 13.9: a coordinator agent (the Chapter 13 hub) that delegates data questions to
an analyst AGENT published as an MCP server, and handles the to-dos itself.
The analyst server needs the API key, so its config names it in pass_env (section 14.3):
a server gets no secrets unless you choose to pass them.

Run:  python ex13_9_coordinator.py"""
import asyncio
import json
from pathlib import Path
import ch13_mcp_agent as m

CONFIG = Path(__file__).with_name("servers_with_analyst.json")
QUESTION = ("Find our three best customers by revenue and add a to-do to send each a "
            "thank-you note.")

def tool_calls(messages):
    return [b.name for msg in messages if msg["role"] == "assistant" and not isinstance(msg["content"], str)
            for b in msg["content"] if getattr(b, "type", "") == "tool_use"]

async def main(config=None, question=QUESTION):
    config = config or json.loads(CONFIG.read_text())
    async with m.MCPHub(config) as hub:
        print("Coordinator tools:", [t["name"] for t in hub.tools])
        answer, messages = await m.run_mcp_agent(
            hub, question, system="You coordinate. Delegate every data question to the analyst "
                                  "in one self-contained question; handle to-dos yourself.")
    calls = tool_calls(messages)
    print("\nTool calls:", calls)
    print(answer)
    return answer, calls

if __name__ == "__main__":
    asyncio.run(main())
