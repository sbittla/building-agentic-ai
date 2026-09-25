"""Shared host for the capstones: MCP servers + a policy layer + the agent loop."""
import asyncio
import json
import sys
from pathlib import Path
import ch13_mcp_agent as m13
from ch14_policy_agent import Policy, console_approver

HERE = Path(__file__).parent

def server(name, script, *args, log=True):
    """Config entry for a capstone server script, run with this Python."""
    spec = {"command": sys.executable, "args": [str(HERE / script), *args]}
    if log:
        spec["log"] = "capstone_servers.log"
    return name, spec

class CapstonePolicy(Policy):
    """Chapter 14's policy from a dict instead of a file; `approver` decides approvals
    (and outbound requests after private data was read)."""
    def __init__(self, rules, log_path="capstone_calls.jsonl", approver=None):
        super().__init__(rules=rules, log_path=log_path, approver=approver or console_approver)

TOKEN_BUDGET = 150_000        # per question: a runaway agent stops instead of spending

def budget(stats):
    if stats["input_tokens"] + stats["output_tokens"] > TOKEN_BUDGET:
        return f"token budget of {TOKEN_BUDGET} reached"
    return None

async def ask(config, question, system, rules, approver=console_approver, messages=None,
              max_iterations=12, stats=None):
    async with m13.MCPHub(config) as hub:
        policy = CapstonePolicy(rules, approver=approver)
        hub.tools = policy.visible_tools(hub.tools)
        return await m13.run_mcp_agent(hub, question, system=system, messages=messages,
                                       max_iterations=max_iterations,
                                       before_call=policy.before_call,
                                       should_stop=budget, stats=stats)

def chat(config, system, rules, approver=console_approver):
    async def loop():
        async with m13.MCPHub(config) as hub:
            policy = CapstonePolicy(rules, approver=approver)
            hub.tools = policy.visible_tools(hub.tools)
            print("Tools:", [t["name"] for t in hub.tools], file=sys.stderr)
            history = []
            while True:
                q = (await asyncio.to_thread(input, "\nYou: ")).strip()
                if q in ("", "quit", "exit"):
                    return
                stats = {}
                answer, history = await m13.run_mcp_agent(hub, q, system=system, messages=history,
                                                          before_call=policy.before_call,
                                                          should_stop=budget, stats=stats)
                print("Agent:", answer)
                print(f"  [{stats['steps']} steps, {stats['tool_calls']} tool calls, "
                      f"{stats['input_tokens'] + stats['output_tokens']} tokens]", file=sys.stderr)
    asyncio.run(loop())
