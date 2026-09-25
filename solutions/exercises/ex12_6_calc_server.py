"""Exercise 12.6 (Medium): the chapter 3 tools as an MCP server (+ resource + prompt)."""
import logging
import sys
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
import ch03_tools as t

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
mcp = MCPServer("calc", instructions="Exact arithmetic, dates and unit conversion.")

def _run(name, **args):
    out = t.run_tool(name, args)
    if out.startswith("ERROR"):
        raise ToolError(out)
    return out

@mcp.tool()
def calculate(expression: str) -> str:
    """Exact arithmetic on an expression (+ - * / ** % parentheses). Not for dates or units."""
    return _run("calculate", expression=expression)

@mcp.tool()
def get_current_date() -> str:
    """Today's date and weekday. Use for anything relative to today."""
    return _run("get_current_date")

@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between km, mi, m (distance) or kg, lb, g (weight)."""
    return _run("convert_units", value=value, from_unit=from_unit, to_unit=to_unit)

@mcp.tool()
def days_between(start: str, end: str) -> str:
    """Days between two ISO dates (YYYY-MM-DD) and the weekday of the end date."""
    return _run("days_between", start=start, end=end)

@mcp.resource("calc://units")
def supported_units() -> str:
    """Units convert_units supports."""
    return "distance: km, mi, m\nweight: kg, lb, g"

@mcp.prompt()
def countdown(event: str, date: str) -> str:
    """How many days until an event."""
    return f"Use the tools to tell me how many days until {event} on {date}, and its weekday."

if __name__ == "__main__":
    mcp.run(transport="stdio")
