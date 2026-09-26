"""Exercise 14.6 helper: a simulated internet, as an MCP server with one `fetch` tool.
It serves one poisoned news page and records every URL requested, so the red team can
see exactly what data tried to leave. Nothing here touches the real network."""
import os
from pathlib import Path
from mcp.server import MCPServer

LOG = Path(os.environ.get("REDTEAM_WEB_LOG", "redteam/web_requests.log"))
PAGE = os.environ.get("REDTEAM_PAGE", "Today's news: nothing happened.")
mcp = MCPServer("web")

@mcp.tool()
def fetch(url: str) -> str:
    """Fetch a web page and return its text."""
    with open(LOG, "a") as f:
        f.write(url + "\n")
    if "news.example/today" in url:
        return PAGE
    return "OK"

if __name__ == "__main__":
    mcp.run(transport="stdio")
