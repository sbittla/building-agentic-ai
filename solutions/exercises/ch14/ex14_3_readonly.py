"""Exercise 14.3 (Simple): GitHub's server in read-only mode.

Needs GITHUB_PERSONAL_ACCESS_TOKEN (read-only scopes) in .env. Usage:
    ./course.sh python exercises/ex14_3_readonly.py [owner/repo]
The repository defaults to GITHUB_REPO in .env, else modelcontextprotocol/servers.
"""
import asyncio
import json
import os
import sys
import ch13_mcp_agent as m13
from ch14_policy_agent import Policy, SYSTEM

WRITE_VERBS = ("create", "update", "delete", "merge", "close", "add", "push", "assign",
               "fork", "request", "dismiss", "remove", "commit", "write", "edit")

def is_write(name: str) -> bool:
    """github__create_issue is a write; github__list_commits is not."""
    return name.partition(m13.SEP)[2].split("_")[0] in WRITE_VERBS

def compact_result(text: str, max_items: int = 40, max_chars: int = 6000) -> str:
    """GitHub returns every field of every issue or commit: tens of thousands of tokens,
    more than a small model's whole context. Keep what a summary needs (Chapter 16)."""
    try:
        data = json.loads(text)
    except ValueError:
        return text[:max_chars]
    items = data if isinstance(data, list) else next(
        (v for v in data.values() if isinstance(v, list)), None) if isinstance(data, dict) else None
    if items is None:
        return text[:max_chars]
    rows = []
    for it in items[:max_items]:
        if not isinstance(it, dict):
            continue
        commit = it.get("commit") or {}
        row = {k: it[k] for k in ("number", "title", "state", "created_at") if k in it}
        if it.get("labels"):
            row["labels"] = [l.get("name", "") if isinstance(l, dict) else l for l in it["labels"]]
        if it.get("sha"):
            row["sha"] = it["sha"][:7]
        if message := commit.get("message") or it.get("message"):
            row["message"] = message.splitlines()[0][:120]
        if date := (commit.get("author") or {}).get("date") or it.get("date"):
            row["date"] = date
        rows.append(row)
    return json.dumps({"items": rows, "shown": len(rows), "in_this_page": len(items)})[:max_chars]

def CompactHub(config):
    """The Chapter 13 hub, with GitHub results compacted before the model sees them."""
    hub = m13.MCPHub(config)
    call = hub.call
    async def compacted(name, args):
        text, is_error = await call(name, args)
        if name.startswith("github") and not is_error:
            text = compact_result(text)
        return text, is_error
    hub.call = compacted
    return hub

async def main(repo):
    config = json.load(open("servers_github.json"))
    policy = Policy()
    async with CompactHub(config) as hub:
        hub.tools = policy.visible_tools(hub.tools)
        github = [t["name"] for t in hub.tools if t["name"].startswith("github")]
        writes = [n for n in github if is_write(n)]
        print(f"{len(github)} GitHub tools, write tools among them: {writes or 'none'}")
        assert github, "the GitHub server offered no tools: is the token set?"
        assert not writes, f"write tools visible: {writes}"
        summary, history = await m13.run_mcp_agent(
            hub, f"Summarize the open issues in {repo}: how many there are, and the main "
                 "themes, with two or three example issue numbers. Keep it under 300 words.",
            system=SYSTEM, before_call=policy.before_call)
        print("\nSummary:\n" + summary)
        if "[Stopped:" in summary:
            raise SystemExit("the summary didn't finish (see the [Stopped: ...] note)")
        reply, _ = await m13.run_mcp_agent(hub, f"Now close issue 3 in {repo}.", system=SYSTEM,
                                           messages=history, before_call=policy.before_call)
        print("\nClose issue 3:\n" + reply)
    calls = [json.loads(line) for line in open(policy.log_path)]
    print(f"\nAudit log: {len(calls)} tool calls:",
          sorted({c['tool'] for c in calls}) or "none")

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else
                     os.environ.get("GITHUB_REPO", "modelcontextprotocol/servers")))
