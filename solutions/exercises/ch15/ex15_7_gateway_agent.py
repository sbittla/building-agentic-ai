"""Exercise 15.7: the Chapter 13 agent, with the gateway as its only server.

The host starts the gateway for one agent and hands it that agent's token. The
agent sees two tools, search_tools and use_tool, and finds the rest by searching.
"""
import asyncio
import json
import sys
from pathlib import Path
import ch26_identity as identity
from ch13_mcp_agent import MCPHub, run_mcp_agent
from ch15_gateway import AUDIENCE, AUDIT

SYSTEM = ("You work for Ana. Company tools sit behind a gateway: find them with "
          "company__search_tools, then call them with company__use_tool. If a call "
          "is not allowed, say so plainly; don't look for a way around it.")

def config_for(agent: str, user: str, scopes: set[str]) -> dict:
    token = identity.mint(agent, user, scopes, AUDIENCE, ttl=900)
    return {"servers": {"company": {"command": sys.executable,
                                    "args": ["ch15_gateway.py", "stdio"],
                                    "env": {"AGENT_TOKEN": token}}}}

async def main(question: str = "Add a task 'Book flights' due 2026-10-02, then "
               "tell me how many orders were cancelled.") -> tuple[str, list]:
    AUDIT.unlink(missing_ok=True)
    config = config_for("planner-agent", "ana", {"todo:read", "todo:write"})
    async with MCPHub(config) as hub:
        print("agent sees:", [t["name"] for t in hub.tools])
        answer, _ = await run_mcp_agent(hub, question, system=SYSTEM)
    print("\nAgent:", answer)
    # the gateway only writes the file on a use_tool call: none means an empty trail
    audit = [json.loads(line) for line in AUDIT.read_text().splitlines()] if AUDIT.exists() else []
    print("\nAudit:" if audit else "\nAudit: empty (the agent made no calls through use_tool)")
    for row in audit:
        print(f"  {row['agent']:<22} {row['tool']:<20} {row['outcome']}")
    return answer, audit

if __name__ == "__main__":
    asyncio.run(main(*sys.argv[1:2]))
