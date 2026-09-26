"""Capstone 5: the chapter 6 notes tools over library/, as an MCP server."""
import logging, sys
from pathlib import Path
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
import ch06_notes_tools as notes

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
notes.ROOT = Path("library").resolve()
mcp = MCPServer("library")

def _run(name, **args):
    out = notes.run_tool(name, args)
    if out.startswith("ERROR"):
        raise ToolError(out)
    return out

@mcp.tool()
def search_docs(pattern: str) -> str:
    """Case-insensitive regex search over the document library; returns file:line: text."""
    return _run("search_files", pattern=pattern)

@mcp.tool()
def read_doc(path: str, start_line: int = 1) -> str:
    """Read a library document with line numbers."""
    return _run("read_file", path=path, start_line=start_line)

@mcp.tool()
def list_docs() -> str:
    """All documents in the library."""
    return _run("list_files")

if __name__ == "__main__":
    mcp.run(transport="stdio")
