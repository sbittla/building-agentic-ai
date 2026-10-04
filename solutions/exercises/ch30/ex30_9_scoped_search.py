"""Exercise 30.9: search results that match the caller's rights.

An agent shouldn't learn that tools it may never call exist: their names and
descriptions are information too, and they cost tokens.
"""
import asyncio
import json
from mcp import Client
from mcp.server.mcpserver import Context
import ch26_identity as identity
from ch30_gateway import AUDIENCE, POLICY, UPSTREAMS, Gateway, _token

class ScopedGateway(Gateway):
    async def search_tools(self, query: str, limit: int = 5,
                           ctx: Context | None = None) -> str:
        """Find company tools by keyword. Returns names, descriptions and input
        schemas; call one with use_tool."""
        try:
            scopes = set(identity.verify(_token(ctx), AUDIENCE)["scope"].split())
        except identity.Denied:
            scopes = set()                     # no valid token: nothing to find
        hits = json.loads(await super().search_tools(query, limit=100))
        mine = [h for h in hits if self.policy[h["name"]] in scopes]
        return json.dumps(mine[:limit])

async def search(gateway, token, query):
    async with Client(gateway) as client:
        result = await client.call_tool("search_tools", {"query": query},
                                        meta={"agent_token": token})
        return [h["name"] for h in json.loads(result.content[0].text)]

async def main() -> dict:
    gateway = ScopedGateway(UPSTREAMS, POLICY, progressive=True)
    reader = identity.mint("planner-agent", "ana", {"todo:read"}, AUDIENCE)
    analyst = identity.mint("analyst-agent", "ana", {"shop:read"}, AUDIENCE)
    found = {"reader, 'task'": await search(gateway, reader, "task"),
             "analyst, 'task'": await search(gateway, analyst, "task"),
             "analyst, 'query schema'": await search(gateway, analyst, "query schema"),
             "no token, 'task'": await search(gateway, "", "task")}
    for who, names in found.items():
        print(f"{who:<26} {names}")
    return found

if __name__ == "__main__":
    asyncio.run(main())
