"""Capstone 4: code review and fix agent (local PRs as branches)."""
import asyncio
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from anthropic import AsyncAnthropic
import ch13_mcp_agent as m13
from common import server, CapstonePolicy, console_approver

CONFIG = {"servers": dict([server("repo", "c4_review/repo_server.py")])}
RULES = {"allow": {"repo": ["list_prs", "get_pr_diff", "read_file", "run_tests"]},
         "needs_approval": ["repo__propose_fix"]}
SYSTEM = """You review pull requests. For the PR you are given: read the diff, run the tests,
and look for bugs, risks, missing or deleted tests. Deleting a test is always a finding.
If tests fail and the fix is small, propose it with propose_fix (never edit tests).
Severities: bug = the changed code gives a wrong result now (name the input that breaks it);
risk = a deleted or weakened test, or a security or data-loss risk; tests = a test you'd add;
style = naming, docs or formatting. Request changes only for failing tests, a bug or a risk;
a small, correct change with no test of its own is an approve with a "tests" finding."""

def decide_verdict(review: dict, diff: str) -> dict:
    """The model proposes findings; code decides the verdict (Chapter 22). A deleted test
    blocks whatever the model labeled it: code reads that from the diff itself."""
    deletes_test = re.search(r"^-\s*def test_", diff, re.M) is not None
    blocking = (deletes_test or not review.get("tests_passed", False)
                or any(f.get("severity") in ("bug", "risk") for f in review.get("findings", [])))
    return dict(review, verdict="request_changes" if blocking else "approve")

REVIEW ={"name": "submit_review", "description": "The structured review.",
          "input_schema": {"type": "object", "properties": {
              "verdict": {"type": "string", "enum": ["approve", "request_changes"]},
              "tests_passed": {"type": "boolean"},
              "findings": {"type": "array", "items": {"type": "object", "properties": {
                  "file": {"type": "string"}, "line": {"type": "integer"},
                  "severity": {"type": "string", "enum": ["bug", "risk", "tests", "style"]},
                  "comment": {"type": "string"}}, "required": ["file", "line", "severity", "comment"]}}},
              "required": ["verdict", "tests_passed", "findings"]}}

async def review(branch: str, approver=console_approver):
    async with m13.MCPHub(CONFIG) as hub:
        policy = CapstonePolicy(RULES, approver=approver)
        hub.tools = policy.visible_tools(hub.tools)
        _, messages = await m13.run_mcp_agent(hub, f"Review pull request {branch}.", system=SYSTEM,
                                              max_iterations=12, before_call=policy.before_call)
        diff, _ = await hub.call("repo__get_pr_diff", {"branch": branch})
    r = await AsyncAnthropic().messages.create(
        model=m13.MODEL, max_tokens=4096, tools=[REVIEW], tool_choice={"type": "tool", "name": "submit_review"},
        messages=messages + [{"role": "user", "content": "Submit your review."}])
    return decide_verdict(next(b.input for b in r.content if b.type == "tool_use"), diff)

async def review_all(prs):
    # one event loop for every PR: the async model clients are cleaned up on the loop
    # that made them (one asyncio.run per PR prints "Event loop is closed" tracebacks)
    for pr in prs:
        print(pr, json.dumps(await review(pr), indent=1))

if __name__ == "__main__":
    asyncio.run(review_all(sys.argv[1:] or ["pr-1", "pr-2", "pr-3"]))
