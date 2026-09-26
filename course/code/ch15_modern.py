"""Chapter 15: what a 2026-07-28 MCP server and client say to each other.

    python ch15_modern.py            # in-process demo: discovery, cache hints, caching
    ./course.sh serve ch15_modern.py # the same server over Streamable HTTP on :8000/mcp

No model and no API key needed.
"""
import asyncio
import os
import sys
from mcp import Client
from mcp.server import MCPServer
from mcp.server.caching import CacheHint

# ------------------------------------------------------------ 1. a server with hints
class CountingServer(MCPServer):
    """An MCPServer that counts the list requests that actually reach it."""
    list_requests = 0

    async def list_tools(self):
        CountingServer.list_requests += 1
        return await super().list_tools()

catalog = CountingServer(
    "catalog", version="1.2.0",
    instructions="Product catalogue lookups. Read-only.",
    cache_hints={
        # The tool list changes only when we deploy: any client may reuse it
        # for five minutes, and one user's copy is as good as another's.
        "tools/list": CacheHint(ttl_ms=300_000, scope="public"),
        # Resources can differ per user, so cached copies stay with that user.
        "resources/list": CacheHint(ttl_ms=60_000, scope="private"),
    })

PRODUCTS = {"P-1": ("Trail shoes", 89.0), "P-2": ("Rain jacket", 120.0),
            "P-3": ("Water bottle", 15.0)}

@catalog.tool()
def find_products(text: str) -> str:
    """Products whose name contains text, one per line: id, name, price."""
    rows = [f"{pid}  {name}  {price:.2f}" for pid, (name, price) in PRODUCTS.items()
            if text.lower() in name.lower()]
    return "\n".join(rows) or "No products match."

@catalog.tool()
def get_price(product_id: str) -> float:
    """The current price of one product, in euros."""
    if product_id not in PRODUCTS:
        raise ValueError(f"unknown product {product_id}; use find_products")
    return PRODUCTS[product_id][1]

# ------------------------------------------------------------ 2. a client that looks
async def describe(target) -> dict:
    """Connect, then report what the server told us about itself."""
    async with Client(target) as client:          # mode="auto": probes server/discover
        info = client.server_info
        caps = client.server_capabilities
        tools = await client.list_tools()
        again = await client.list_tools()          # served from the client's cache
        return {"protocol": client.protocol_version,
                "server": f"{info.name} {info.version}",
                "tools": [t.name for t in tools.tools],
                "ttl_ms": tools.ttl_ms, "cache_scope": tools.cache_scope,
                "list_changed": caps.tools.list_changed if caps.tools else False,
                "same_answer": [t.name for t in again.tools]
                               == [t.name for t in tools.tools]}

# ------------------------------------------------------------ 3. the raw wire
ENVELOPE = {"io.modelcontextprotocol/protocolVersion": "2026-07-28",
            "io.modelcontextprotocol/clientCapabilities": {}}

def post(url: str, method: str, params: dict | None = None) -> dict:
    """One complete MCP request over HTTP: no handshake and no session. The
    headers repeat the method (and tool name) so a gateway can route without
    reading the body; the server rejects a request whose headers disagree."""
    import httpx
    params = {**(params or {}), "_meta": ENVELOPE}
    headers = {"Accept": "application/json, text/event-stream",
               "MCP-Protocol-Version": "2026-07-28", "Mcp-Method": method}
    if "name" in params:
        headers["Mcp-Name"] = params["name"]
    body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    return httpx.post(url, json=body, headers=headers, timeout=30).json()

async def main():
    report = await describe(catalog)
    for key, value in report.items():
        print(f"{key:>13}: {value}")
    print(f"list requests that reached the server: {CountingServer.list_requests}")

if __name__ == "__main__":
    if sys.argv[1:] == ["streamable-http"]:
        from mcp.server.transport_security import TransportSecuritySettings
        catalog.run(transport="streamable-http",
                    host=os.environ.get("MCP_HOST", "127.0.0.1"),
                    transport_security=TransportSecuritySettings(
                        allowed_hosts=["127.0.0.1:*", "localhost:*"],
                        allowed_origins=["http://localhost:*", "http://127.0.0.1:*"]))
    else:
        asyncio.run(main())
