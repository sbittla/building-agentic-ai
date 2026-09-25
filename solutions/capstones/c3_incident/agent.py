"""Capstone 3: incident triage. Investigates, then returns a STRUCTURED summary."""
import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from anthropic import AsyncAnthropic
import ch13_mcp_agent as m13
from common import server, CapstonePolicy

CONFIG = {"servers": dict([server("obs", "c3_incident/obs_server.py"),
                           ("git", {"command": "mcp-server-git", "args": ["--repository", "incident/repo"],
                                    "log": "capstone_servers.log"})])}
RULES = {"allow": {"obs": ["*"], "git": ["git_log", "git_show", "git_diff"]}}
SYSTEM = """You are the first responder for a production incident. Investigate with the tools:
compare metrics to a baseline before the alert, search error logs in the incident window,
list recent commits (git_log with repo_path 'incident/repo') and read the matching runbook.
Only claim what the tools showed. Never run remediation yourself."""
REPORT = {"name": "triage_report", "description": "The structured incident summary.",
          "input_schema": {"type": "object", "properties": {
              "impact": {"type": "string"}, "timeline": {"type": "array", "items": {"type": "string"}},
              "suspected_cause": {"type": "string"},
              "suspect_commit": {"type": "string", "description": "short SHA or 'unknown'"},
              "evidence": {"type": "array", "items": {"type": "string"}},
              "next_steps": {"type": "array", "items": {"type": "string"}}},
              "required": ["impact", "timeline", "suspected_cause", "suspect_commit", "evidence", "next_steps"]}}

async def triage(alert: str):
    async with m13.MCPHub(CONFIG) as hub:
        policy = CapstonePolicy(RULES)
        hub.tools = policy.visible_tools(hub.tools)
        findings, messages = await m13.run_mcp_agent(hub, alert, system=SYSTEM, max_iterations=15,
                                                     before_call=policy.before_call)
    r = await AsyncAnthropic().messages.create(
        model=m13.MODEL, max_tokens=4096, tools=[REPORT],
        tool_choice={"type": "tool", "name": "triage_report"},
        messages=messages + [{"role": "user", "content": "Now fill in the triage report."}])
    return next(b.input for b in r.content if b.type == "tool_use")

ALERT = ("ALERT 2026-09-22 14:12: checkout-service p95 latency above 700 ms and error rate above 3% "
         "for 5 minutes. Triage it.")

if __name__ == "__main__":
    print(json.dumps(asyncio.run(triage(ALERT)), indent=2))
