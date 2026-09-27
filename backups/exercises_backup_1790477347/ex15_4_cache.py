"""Exercise 15.4: how many list requests does caching save?

A host asks for the tool list before every model call. Count the requests that
reach the server over ten turns, with the client's cache on and off, and with the
server's hint set to "don't cache".
"""
import asyncio
from mcp import Client
from mcp.server.caching import CacheHint
from ch15_modern import CountingServer, find_products, get_price

def make_server(ttl_ms: int) -> CountingServer:
    server = CountingServer("catalog", cache_hints={
        "tools/list": CacheHint(ttl_ms=ttl_ms, scope="public")})
    server.tool()(find_products)
    server.tool()(get_price)
    return server

async def turns(server, n: int = 10, cache_mode: str = "use") -> int:
    CountingServer.list_requests = 0
    async with Client(server) as client:
        for _ in range(n):
            await client.list_tools(cache_mode=cache_mode)   # before each model call
    return CountingServer.list_requests

async def main() -> dict:
    results = {
        "hint 5 min, cache on": await turns(make_server(300_000)),
        "hint 5 min, cache bypassed": await turns(make_server(300_000),
                                                  cache_mode="bypass"),
        "hint 0 (don't cache)": await turns(make_server(0)),
    }
    for label, count in results.items():
        print(f"{label:<28} {count:>2} of 10 requests reached the server")
    return results

if __name__ == "__main__":
    asyncio.run(main())
