"""Exercises 13.4 and 13.6, run end to end with sol_ch13_mcp_agent.ResilientHub.

    python run13_hub.py resources    13.4: resources go into the system prompt at start-up,
                                     so the revenue question uses shopdb://definitions
    python run13_hub.py resilience   13.6: kill the to-do server mid-session; the next
                                     question still works because the hub restarts it
"""
import asyncio
import json
import os
import signal
import sys
from pathlib import Path

import sol_ch13_mcp_agent as sol

CONFIG = json.loads(Path("servers.json").read_text())

def server_pids(script: str) -> list[int]:
    """Child processes of this program running `script` (the stdio MCP servers)."""
    pids = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            cmd = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode()
            ppid = int((proc / "stat").read_text().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            continue
        if script in cmd and ppid == os.getpid():
            pids.append(int(proc.name))
    return pids

async def resources():
    async with sol.ResilientHub(CONFIG) as hub:
        context = await hub.resource_context()
        print("Resources loaded at start-up:\n" + context)
        question = "What was our total revenue? Give the number and the SQL you used."
        print(f"You: {question}")
        answer, messages = await sol.run_with_resources(hub, question)
        sql = [b.input.get("query") or b.input.get("sql", "")      # shopdb's argument: query
               for m in messages if m["role"] == "assistant"
               and not isinstance(m["content"], str)
               for b in m["content"] if getattr(b, "type", "") == "tool_use"]
        print(f"Agent: {answer}")
        used = any("cancelled" in s.lower() for s in sql)
        print(f"\nSQL excludes cancelled orders (the definition from shopdb://definitions): {used}")

async def resilience():
    async with sol.ResilientHub(CONFIG) as hub:
        q1 = "Add a to-do: call the bank, due 2026-11-02."
        print(f"You: {q1}")
        a1, history = await sol.base.run_mcp_agent(hub, q1)
        print(f"Agent: {a1}")
        pids = server_pids("ch13_todo_server.py")
        for pid in pids:
            os.kill(pid, signal.SIGKILL)
        print(f"\n[demo] killed the todo server (pids {pids}) mid-session\n")
        await asyncio.sleep(1)
        q2 = "What is on my to-do list now?"
        print(f"You: {q2}")
        a2, _ = await sol.base.run_mcp_agent(hub, q2, messages=history)
        print(f"Agent: {a2}")
        print(f"\nserver restarts: {hub.restarts}; the next question still worked: "
              f"{hub.restarts >= 1 and 'bank' in a2.lower()}")

if __name__ == "__main__":
    asyncio.run({"resources": resources, "resilience": resilience}[
        sys.argv[1] if len(sys.argv) > 1 else "resources"]())
