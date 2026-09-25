"""Exercise 13.3 (Simple): an MCP client with no model at all."""
import asyncio
import sys
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command=sys.executable, args=["ch13_todo_server.py"])
    async with Client(stdio_client(params)) as client:
        print("tools:", [t.name for t in (await client.list_tools()).tools])
        added = await client.call_tool("add_task", {"title": "Read chapter 13", "priority": "high"})
        listed = await client.call_tool("list_tasks", {})
        print(added.content[0].text)
        print(listed.content[0].text)
        return added.content[0].text, listed.content[0].text

if __name__ == "__main__":
    asyncio.run(main())
