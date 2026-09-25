"""Exercise 19.6 (solution): the chapter 13 hub, now able to reach REMOTE MCP servers.

A server entry with "url" is reached over Streamable HTTP with a bearer token;
entries with "command" still start a local stdio server.

Run:  ./course.sh serve-mcp            (in one terminal)
      ./course.sh python exercises/ex19_6_remote_hub.py exercises/servers_remote.json"""
import asyncio
import json
import os
import sys
import httpx
from mcp import Client
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client
from ch13_mcp_agent import SEP, MCPHub, run_mcp_agent

class RemoteMCPHub(MCPHub):
    async def __aenter__(self):
        await self.stack.__aenter__()
        for name, spec in self.config["servers"].items():
            try:
                await self._connect(name, spec)
            except Exception as exc:
                await self.stack.aclose()
                where = spec.get("url") or " ".join([spec["command"], *spec.get("args", [])])
                raise RuntimeError(f"MCP server '{name}' ({where}) failed: "
                                   f"{type(exc).__name__}: {exc}") from exc
        return self

    async def _connect(self, name, spec):
        if "url" not in spec:
            return await super()._connect(name, spec)
        token = spec.get("token") or os.environ.get(spec.get("token_env", "MCP_TOKEN"), "")
        # a quick probe first, so a bad token gives a clear message instead of a stack trace
        async with httpx.AsyncClient(timeout=10) as probe:
            r = await probe.post(spec["url"], headers={"Authorization": f"Bearer {token}",
                                 "Accept": "application/json, text/event-stream"}, json={})
        if r.status_code == 401:
            raise PermissionError(f"remote MCP server '{name}' rejected the token (401). "
                                  f"Check {spec.get('token_env', 'MCP_TOKEN')} in your .env")
        http = await self.stack.enter_async_context(create_mcp_http_client(
            headers={"Authorization": f"Bearer {token}"}))
        client = await self.stack.enter_async_context(
            Client(streamable_http_client(spec["url"], http_client=http)))
        self.clients[name] = client
        for tool in (await client.list_tools()).tools:
            self.tools.append({"name": f"{name}{SEP}{tool.name}",
                               "description": f"[{name}] {tool.description or ''}",
                               "input_schema": tool.input_schema})

async def main(path="servers_remote.json", questions=("Add 'prepare demo' due 2026-10-10, "
                                                       "then list the team's tasks.",)):
    config = json.load(open(path))
    try:
        async with RemoteMCPHub(config) as hub:
            print("Tools:", [t["name"] for t in hub.tools])
            for q in questions:
                answer, _ = await run_mcp_agent(hub, q)
                print("Agent:", answer)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main(*sys.argv[1:2])))
