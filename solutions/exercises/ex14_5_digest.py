"""Exercise 14.5 (Medium): weekly engineering digest from Git + GitHub (read-only).

Needs GITHUB_PERSONAL_ACCESS_TOKEN (read-only) in .env. Usage:
    ./course.sh python exercises/ex14_5_digest.py owner/repo
"""
import asyncio
import json
import sys
import ch13_mcp_agent as m13
from ch14_policy_agent import Policy, SYSTEM

PROMPT = ("Summarize the last 7 days of commits (git server) and the open issues in {repo} "
          "(GitHub server), grouped by theme. Use the time server for today's date.")

async def main(repo):
    config = json.load(open("servers_github.json"))
    policy = Policy()
    async with m13.MCPHub(config) as hub:
        hub.tools = policy.visible_tools(hub.tools)
        writes = [t["name"] for t in hub.tools if any(w in t["name"] for w in
                  ("create", "update", "delete", "merge", "commit", "push"))]
        assert not writes, f"write tools visible: {writes}"
        answer, _ = await m13.run_mcp_agent(hub, PROMPT.format(repo=repo), system=SYSTEM,
                                            before_call=policy.before_call)
        print(answer)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "modelcontextprotocol/servers"))
