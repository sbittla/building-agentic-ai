"""Chapter 13: an AGENT as an MCP server. The Chapter 8 SQL analyst becomes one tool,
ask_sql_analyst(question). Any MCP host (Claude Desktop, VS Code, your Chapter 13 hub, another
agent) can now delegate data questions to it without knowing it's an agent inside.

This is how multi-agent systems are built across teams: each team publishes its agent as
an MCP server, and a coordinator agent uses them like any other tools.

Run as a server:  python ch13_agent_server.py        (stdio)
Use from the hub: add it to servers.json, see exercise 13.9"""
import logging
import sys
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from ch04_agent import run_agent
import ch08_sql_tools as sql

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("sql-analyst-server")
mcp = MCPServer("sql-analyst", instructions="Answers questions about the shop's sales data.")

MAX_STEPS = 8          # the inner agent has its own budget; callers can't raise it

@mcp.tool()
def ask_sql_analyst(question: str) -> str:
    """Answer a question about the shop's customers, products, orders or revenue. A data
    analyst agent writes and runs read-only SQL, then answers in plain English with the
    numbers it found. Ask one self-contained question per call."""
    log.info("question: %s", question[:200])
    answer, _, stats = run_agent(question, sql.TOOLS, sql.run_tool, system=sql.SYSTEM,
                                 max_iterations=MAX_STEPS, verbose=False)
    log.info("answered in %d steps, %d tool calls", stats["steps"], stats["tool_calls"])
    if stats["stop_reason"] not in ("end_turn", "stop_sequence"):
        raise ToolError(f"The analyst didn't finish: {answer}")   # the caller sees is_error
    return answer

if __name__ == "__main__":
    mcp.run()
