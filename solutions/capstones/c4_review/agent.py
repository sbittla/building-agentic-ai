"""Capstone 4: code review and fix agent (local PRs as branches)."""
import asyncio
import json
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
If tests fail and the fix is small, propose it with propose_fix (never edit tests)."""
REVIEW = {"name": "submit_review", "description": "The structured review.",
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
    r = await AsyncAnthropic().messages.create(
        model=m13.MODEL, max_tokens=4096, tools=[REVIEW], tool_choice={"type": "tool", "name": "submit_review"},
        messages=messages + [{"role": "user", "content": "Submit your review."}])
    return next(b.input for b in r.content if b.type == "tool_use")

if __name__ == "__main__":
    for pr in (sys.argv[1:] or ["pr-1", "pr-2", "pr-3"]):
        print(pr, json.dumps(asyncio.run(review(pr)), indent=1))
