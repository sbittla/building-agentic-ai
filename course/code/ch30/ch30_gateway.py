"""Chapter 30: an MCP gateway. One front door for many servers.

Agents connect to the gateway only. It knows the real servers, decides which tools
each agent may see and call (with Chapter 26's tokens), limits how fast each agent
may call them, and writes one audit trail for everything.

    python ch30_gateway.py           # in-process demo, no API key needed
"""
import asyncio
import json
import logging
import os
import time
from collections import defaultdict
from pathlib import Path
from mcp import Client
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import TextContent
import ch26_identity as identity
import ch13_todo_server
import ch13_sql_server

SEP = "__"
AUDIENCE = "mcp-gateway"
AUDIT = Path("gateway_audit.jsonl")

# The only tools that exist behind the gateway, and the scope each needs.
# A tool an upstream server adds later stays invisible until someone adds it here.
POLICY = {
    "todo__list_tasks": "todo:read",
    "todo__find_tasks": "todo:read",
    "todo__add_task": "todo:write",
    "todo__complete_task": "todo:write",
    "shopdb__get_schema": "shop:read",
    "shopdb__run_query": "shop:read",
}
RATE = {"calls": 30, "per_s": 60}             # per agent

identity.AGENTS.update({                      # which scopes each agent may ever hold
    "planner-agent": {"todo:read", "todo:write"},
    "analyst-agent": {"shop:read", "orders:read"},
})

class Gateway(MCPServer):
    def __init__(self, upstreams: dict, policy: dict, progressive: bool = False):
        super().__init__("gateway",
                         instructions="Company tools. Every call is audited.")
        self.upstreams = upstreams            # name -> server object or URL
        self.policy = policy
        self.progressive = progressive
        self.catalog: dict[str, object] = {}  # full name -> upstream Tool
        self.expires = 0.0
        self.calls = defaultdict(list)        # agent -> recent call times
        self.tool()(self.search_tools)
        self.tool()(self.use_tool)

    # -------------------------------------------------------- discovery
    async def _refresh(self):
        """Ask every upstream for its tools, keeping the answer for as long as the
        upstream's own cache hint allows."""
        if time.time() < self.expires:
            return
        catalog, ttl = {}, 300_000
        for name, target in self.upstreams.items():
            async with Client(target) as client:
                result = await client.list_tools()
                ttl = min(ttl, result.ttl_ms or 60_000)
                for tool in result.tools:
                    full = f"{name}{SEP}{tool.name}"
                    if full in self.policy:           # deny by default
                        catalog[full] = tool.model_copy(update={"name": full})
        self.catalog, self.expires = catalog, time.time() + ttl / 1000

    async def list_tools(self):
        await self._refresh()
        own = await super().list_tools()      # search_tools and use_tool
        if self.progressive:
            return own                        # the rest are found by searching
        return [t for t in own if t.name != "use_tool"] + list(self.catalog.values())

    async def search_tools(self, query: str, limit: int = 5) -> str:
        """Find company tools by keyword. Returns names, descriptions and input
        schemas; call one with use_tool."""
        await self._refresh()
        words = query.lower().split()
        hits = [t for t in self.catalog.values()
                if any(w in f"{t.name} {t.description}".lower() for w in words)]
        return json.dumps([{"name": t.name, "description": t.description,
                            "input_schema": t.input_schema} for t in hits[:limit]])

    async def use_tool(self, name: str, arguments: dict) -> str:
        """Call a tool found with search_tools."""
        raise ToolError("handled by the gateway")   # never runs: see call_tool

    # -------------------------------------------------------- calls
    async def call_tool(self, name, arguments, context=None):
        """Every call passes here: check the caller, forward, audit."""
        token = _token(context)
        if name == "search_tools":
            return await super().call_tool(name, arguments, context)
        if name == "use_tool":
            name, arguments = arguments.get("name", ""), arguments.get("arguments", {})
        started, outcome = time.time(), "error"
        try:
            self._check(token, name)
            server, _, tool = name.partition(SEP)
            async with Client(self.upstreams[server]) as client:
                result = await client.call_tool(tool, arguments)
            outcome = "error" if result.is_error else "ok"
            return result
        except identity.Denied as exc:
            outcome = f"denied: {exc}"
            raise ToolError(f"Not allowed: {exc}") from None
        finally:
            self._audit(token, name, arguments, outcome, time.time() - started)

    def _check(self, token: str, name: str) -> dict:
        """Is the tool on the list, does the token allow it, is the agent in its
        rate limit? Raises identity.Denied if not."""
        if name not in self.policy:
            raise identity.Denied(f"no tool called {name!r}")
        claims = identity.authorize(token, AUDIENCE, self.policy[name])
        agent = claims["sub"]
        now = time.time()
        recent = [t for t in self.calls[agent] if now - t < RATE["per_s"]]
        if len(recent) >= RATE["calls"]:
            raise identity.Denied(f"rate limit: {RATE['calls']} calls per "
                                  f"{RATE['per_s']} s")
        self.calls[agent] = recent + [now]
        return claims

    def _audit(self, token, name, arguments, outcome, seconds):
        try:
            who = identity.verify(token, AUDIENCE)
            agent, user = who["sub"], who["act_for"]
        except identity.Denied:
            agent = user = "unknown"
        with AUDIT.open("a") as f:
            f.write(json.dumps({"at": time.time(), "agent": agent, "for": user,
                                "tool": name, "args": arguments, "outcome": outcome,
                                "ms": round(seconds * 1000)}) + "\n")

def _token(context) -> str:
    """The caller's token. Over HTTP it comes in the Authorization header; an
    in-process client puts it in the request's _meta; a stdio gateway started
    for one agent gets it in its environment."""
    if context is None:
        return os.environ.get("AGENT_TOKEN", "")
    headers = getattr(context, "headers", None) or {}
    auth = headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:]
    meta = context.request_context.meta or {}
    return meta.get("agent_token") or os.environ.get("AGENT_TOKEN", "")

UPSTREAMS = {"todo": ch13_todo_server.mcp, "shopdb": ch13_sql_server.mcp}

# ------------------------------------------------------------ demo
async def call(gateway, token, name, arguments):
    async with Client(gateway) as client:
        result = await client.call_tool(name, arguments, meta={"agent_token": token})
        text = " ".join(b.text for b in result.content if isinstance(b, TextContent))
        return ("ERROR " if result.is_error else "") + text[:120]

async def main():
    logging.getLogger("mcp").setLevel(logging.WARNING)   # keep the demo output short
    gateway = Gateway(UPSTREAMS, POLICY)
    async with Client(gateway) as client:
        names = [t.name for t in (await client.list_tools()).tools]
    print("agents see:", names)
    planner = identity.mint("planner-agent", "ana", {"todo:read", "todo:write"},
                            AUDIENCE)
    analyst = identity.mint("analyst-agent", "ana", {"shop:read"}, AUDIENCE)
    print(await call(gateway, planner, "todo__add_task", {"title": "Book flights"}))
    print(await call(gateway, analyst, "todo__add_task", {"title": "Sneaky"}))
    print(await call(gateway, analyst, "shopdb__run_query",
                     {"query": "SELECT COUNT(*) AS n FROM orders"}))
    print(await call(gateway, planner, "shopdb__run_query", {"query": "SELECT 1"}))
    print(await call(gateway, planner, "todo__delete_everything", {}))
    print(f"\naudit trail: {AUDIT}")

if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["stdio"]:            # for a host; AGENT_TOKEN names the caller
        Gateway(UPSTREAMS, POLICY, progressive=True).run(transport="stdio")
    else:
        asyncio.run(main())
