"""Capstone 1: hand a conversation to a human with a written summary."""
import json, logging, sys, time
from mcp.server import MCPServer

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
mcp = MCPServer("handoff")

@mcp.tool()
def escalate(summary: str, priority: str = "normal") -> str:
    """Hand off to a human. Use when the customer asks for a person, is upset, or when
    you can't help within policy. priority: low, normal or urgent."""
    with open("handoff_queue.jsonl", "a") as f:
        f.write(json.dumps({"ts": time.time(), "priority": priority, "summary": summary}) + "\n")
    return "Handed off. A person will reply within 4 business hours."

if __name__ == "__main__":
    mcp.run(transport="stdio")
