"""Exercise 14.4 (Medium): weekly engineering digest from Git + GitHub (read-only).

Needs GITHUB_PERSONAL_ACCESS_TOKEN (read-only) in .env. Usage:
    ./course.sh python exercises/ex14_4_digest.py [owner/repo]
The repository defaults to GITHUB_REPO in .env, else modelcontextprotocol/servers.
"""
import asyncio
import json
import os
import re
import sys
import ch13_mcp_agent as m13
from ch04_agent import MODEL, get_client
from ch14_policy_agent import Policy, SYSTEM
from ex14_3_readonly import CompactHub, is_write

SHAPE = ("Start with the heading 'Weekly engineering digest', then one line per theme "
         "(at most five), each naming the theme and citing one or two issue or pull "
         "request numbers from the results, like #1234. Keep it under 400 words.")
PROMPT = ("Write a weekly engineering digest for {repo}: the last 7 days of commits and "
          "the open issues (GitHub server), grouped into themes. Use the time server for "
          "today's date. Your final reply is the digest itself. " + SHAPE)
# A small model can answer the last tool result ("today is October 14") instead of the
# task, write one vague paragraph, or invent plausible issue numbers. Check the digest
# against what GitHub actually returned. If it misses, ask again from the results alone:
# no tools and no history, so a small context has room for the answer.
REWRITE = ("Write a weekly engineering digest for {repo} from this list only. Cite only "
           "the numbers in it. " + SHAPE +
           "\n\nThe last attempt's problem: {problem}.\n\nWhat GitHub returned:\n{results}")

def citable(seen: list[str]) -> str:
    """The issues and commits GitHub returned, one short line each: what a rewrite may
    cite. Far smaller than the raw results, and nothing in it invites a made-up number."""
    lines = []
    for text in seen:
        try:
            data = json.loads(text)
        except ValueError:
            continue
        for it in data.get("items", []) if isinstance(data, dict) else []:
            if "number" in it:
                lines.append(f"#{it['number']} {it.get('title', '')}")
            elif "message" in it:
                lines.append(f"commit {it.get('sha', '')}: {it['message']}")
    return "\n".join(lines) or "\n\n".join(seen)

def problems(answer: str, seen: list[str]) -> list[str]:
    """What's wrong with this digest: cut off, no themes with numbers, or numbers GitHub
    never returned. An empty list means it's a digest we can send."""
    if "[Stopped:" in answer:
        return ["the reply was cut off"]
    body = answer.lower().partition("weekly engineering digest")[2]
    body = re.sub(r"(?m)^[\s*#-]*#\d\b", "", body)     # "#3 Security": a list number
    cited = set(re.findall(r"#(\d+)\b", body))         # not a commit sha like #3f6aaf4
    if not cited:
        return ["no themes with issue numbers"]
    known = set(re.findall(r"\b\d+\b", " ".join(seen)))
    invented = sorted(cited - known, key=int)
    if invented:
        return ["these numbers aren't in the results: " + ", ".join("#" + n for n in invented)]
    return []

async def main(repo):
    config = json.load(open("servers_github.json"))
    policy = Policy()
    seen = []                                   # every tool result, to check citations
    # A small local model has an 8K context: keep GitHub's results short.
    async with CompactHub(config, max_items=15, max_chars=2500) as hub:
        hub.tools = policy.visible_tools(hub.tools)
        writes = [t["name"] for t in hub.tools if is_write(t["name"])]
        assert not writes, f"write tools visible: {writes}"
        call = hub.call
        async def recorded(name, args):
            text, is_error = await call(name, args)
            seen.append(text)
            return text, is_error
        hub.call = recorded
        answer, _ = await m13.run_mcp_agent(hub, PROMPT.format(repo=repo), system=SYSTEM,
                                            before_call=policy.before_call, max_tokens=8000)
        for _ in range(2):
            wrong = problems(answer, seen)
            if not wrong:
                break
            reply = get_client().messages.create(model=MODEL, max_tokens=4000, messages=[
                {"role": "user", "content": REWRITE.format(
                    repo=repo, problem=wrong[0], results=citable(seen))}])
            answer = "".join(b.text for b in reply.content if b.type == "text")
        print(answer)
        wrong = problems(answer, seen)
        print("\nDigest check:", wrong[0] if wrong else "every cited number is in the results")
        if wrong:
            raise SystemExit(f"not a usable digest: {wrong[0]}")
    calls = [json.loads(line) for line in open(policy.log_path)]
    print(f"\nAudit log: {len(calls)} tool calls, decisions "
          f"{sorted({c['decision'] for c in calls})}:", sorted({c["tool"] for c in calls}))

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else
                     os.environ.get("GITHUB_REPO", "modelcontextprotocol/servers")))
