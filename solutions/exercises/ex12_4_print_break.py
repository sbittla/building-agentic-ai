"""Exercise 12.4 (Simple): where does print() go in a Python stdio MCP server?

The Python SDK (2.x) points the stdout file descriptor at stderr while it serves,
so print() lands in the server's log instead of corrupting the JSON-RPC stream.
Other SDKs (TypeScript console.log, Java System.out, older Python SDKs) don't do
this: there, the same line would corrupt the stream. So log to stderr anyway.
"""
import asyncio
import sys
from pathlib import Path
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client

TEMPLATE = '''import logging, sys
from mcp.server import MCPServer
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
mcp = MCPServer("demo")

@mcp.tool()
def geocode(city: str) -> str:
    """Pretend geocoder."""
    {line}
    return '{{"name": "' + city + '"}}'

if __name__ == "__main__":
    mcp.run(transport="stdio")
'''

async def call(server: Path, log: Path) -> str:
    # PYTHONUNBUFFERED=1 (set in the course image) makes print() output appear at once
    params = StdioServerParameters(command=sys.executable, args=[str(server)],
                                   env={"PYTHONUNBUFFERED": "1", "PATH": "/usr/bin:/bin"})
    with log.open("w") as errlog:
        async with Client(stdio_client(params, errlog=errlog)) as c:
            r = await asyncio.wait_for(c.call_tool("geocode", {"city": "Pune"}), 15)
            return r.content[0].text

def main():
    results = {}
    for name, line in [("print", 'print("hello from print")'),
                       ("logging", 'logging.info("hello from logging")')]:
        server, log = Path(f"ex12_4_{name}_server.py"), Path(f"ex12_4_{name}.log")
        server.write_text(TEMPLATE.format(line=line))
        reply = asyncio.run(call(server, log))
        in_log = f"hello from {name}" in log.read_text()
        results[name] = (reply, in_log)
        print(f"{name:<8} tool reply: {reply:<18} 'hello' found in the server's stderr log: {in_log}")
    return results

if __name__ == "__main__":
    main()
