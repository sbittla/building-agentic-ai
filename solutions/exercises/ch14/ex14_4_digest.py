"""Exercise 14.4 (Medium): weekly engineering digest from Git + GitHub (read-only).

Needs GITHUB_PERSONAL_ACCESS_TOKEN (read-only) in .env. Usage:
    ./course.sh python exercises/ex14_4_digest.py [owner/repo]
The repository defaults to GITHUB_REPO in .env, else modelcontextprotocol/servers.
"""
import asyncio
import json
import os
import sys
import ch13_mcp_agent as m13
from ch14_policy_agent import Policy, SYSTEM
from ex14_3_readonly import is_write

PROMPT = ("Summarize the last 7 days of commits and the open issues in {repo} (GitHub "
          "server), grouped by theme. Use the time server for today's date.")

async def main(repo):
    config = json.load(open("servers_github.json"))
    policy = Policy()
    async with m13.MCPHub(config) as hub:
        hub.tools = policy.visible_tools(hub.tools)
        writes = [t["name"] for t in hub.tools if is_write(t["name"])]
        assert not writes, f"write tools visible: {writes}"
        answer, _ = await m13.run_mcp_agent(hub, PROMPT.format(repo=repo), system=SYSTEM,
                                            before_call=policy.before_call)
        print(answer)
    calls = [json.loads(line) for line in open(policy.log_path)]
    print(f"\nAudit log: {len(calls)} tool calls, decisions "
          f"{sorted({c['decision'] for c in calls})}:", sorted({c["tool"] for c in calls}))

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else
                     os.environ.get("GITHUB_REPO", "modelcontextprotocol/servers")))
