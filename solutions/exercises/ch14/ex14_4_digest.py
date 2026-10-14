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
from ex14_3_readonly import CompactHub, is_write

PROMPT = ("Write a weekly engineering digest for {repo}: the last 7 days of commits and "
          "the open issues (GitHub server), grouped into at most five themes, with one or "
          "two example numbers per theme. Keep it under 400 words. Use the time server for "
          "today's date.")

async def main(repo):
    config = json.load(open("servers_github.json"))
    policy = Policy()
    async with CompactHub(config) as hub:
        hub.tools = policy.visible_tools(hub.tools)
        writes = [t["name"] for t in hub.tools if is_write(t["name"])]
        assert not writes, f"write tools visible: {writes}"
        answer, _ = await m13.run_mcp_agent(hub, PROMPT.format(repo=repo), system=SYSTEM,
                                            before_call=policy.before_call, max_tokens=8000)
        print(answer)
        if "[Stopped:" in answer:                  # cut off or refused: not a digest
            raise SystemExit("the digest didn't finish (see the [Stopped: ...] note)")
    calls = [json.loads(line) for line in open(policy.log_path)]
    print(f"\nAudit log: {len(calls)} tool calls, decisions "
          f"{sorted({c['decision'] for c in calls})}:", sorted({c["tool"] for c in calls}))

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else
                     os.environ.get("GITHUB_REPO", "modelcontextprotocol/servers")))
