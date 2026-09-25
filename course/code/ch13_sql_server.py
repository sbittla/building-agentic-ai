"""Chapter 13: the chapter 8 read-only SQL tools as an MCP server."""
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
import ch08_sql_tools as sql

mcp = MCPServer("shopdb")

@mcp.tool()
def get_schema() -> str:
    """CREATE TABLE statements for every table. Call before writing SQL."""
    return sql.get_schema()

@mcp.tool()
def run_query(query: str) -> str:
    """Run one read-only SQLite SELECT (max 50 rows). On error, fix and retry."""
    result = sql.run_query(query)
    if result.startswith("ERROR"):
        raise ToolError(result)
    return result

@mcp.resource("shopdb://definitions")
def definitions() -> str:
    """Business definitions used by analysts."""
    return "Revenue = SUM(quantity * price) over orders whose status != 'cancelled'."

if __name__ == "__main__":
    mcp.run(transport="stdio")
