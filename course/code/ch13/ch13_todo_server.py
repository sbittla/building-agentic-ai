"""Chapter 13: the chapter 5 to-do tools as an MCP server."""
from mcp.server import MCPServer
import ch05_todo_tools as todo

mcp = MCPServer("todo")

@mcp.tool()
def add_task(title: str, due: str | None = None, priority: str = "normal") -> str:
    """Add a to-do. due is YYYY-MM-DD; priority is low, normal or high."""
    return todo.add_task(title, due, priority)

@mcp.tool()
def list_tasks(include_done: bool = False, due_before: str | None = None) -> str:
    """List open tasks, optionally only those due on or before a date."""
    return todo.list_tasks(include_done, due_before)

@mcp.tool()
def find_tasks(text: str) -> str:
    """Find open tasks whose title contains text (use to get ids)."""
    return todo.find_tasks(text)

@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark a task done by id. Ask the user first if several tasks could match."""
    return todo.complete_task(task_id)

@mcp.tool()
def today() -> str:
    """Today's date, YYYY-MM-DD."""
    return todo.today()

if __name__ == "__main__":
    mcp.run(transport="stdio")
