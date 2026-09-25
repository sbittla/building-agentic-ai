"""Capstone 1: help-center articles (read-only)."""
import logging, re, sys
from pathlib import Path
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
ROOT = Path("helpcenter").resolve()
mcp = MCPServer("helpdesk")

@mcp.tool()
def search_articles(query: str) -> str:
    """Search help-center articles (policies and how-tos). Returns name: first line."""
    words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2]
    scored = []
    for p in ROOT.glob("*.md"):
        text = p.read_text().lower()
        score = sum(text.count(w) for w in words)
        if score:
            scored.append((score, p.name, p.read_text().splitlines()[0]))
    return "\n".join(f"{n}: {t}" for _, n, t in sorted(scored, reverse=True)[:5]) or "No articles found."

@mcp.tool()
def read_article(name: str) -> str:
    """Read one article by file name, e.g. return-policy.md."""
    p = (ROOT / name).resolve()
    if ROOT not in p.parents or not p.exists():
        raise ToolError(f"No article called {name}. Use search_articles.")
    return p.read_text()

@mcp.resource("helpdesk://return-policy")
def return_policy() -> str:
    """The return policy, for the host to put in the system prompt."""
    return (ROOT / "return-policy.md").read_text()

if __name__ == "__main__":
    mcp.run(transport="stdio")
