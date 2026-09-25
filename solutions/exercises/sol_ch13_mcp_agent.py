"""Chapter 13 reference solution: 13.5 (resources at start-up) and 13.7 (resilience)."""
import os
import sys
from contextlib import AsyncExitStack
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp_types import TextContent
import ch13_mcp_agent as base
from ch13_mcp_agent import SEP

RESOURCE_BUDGET = 4000        # characters of resources added to the system prompt

class ResilientHub(base.MCPHub):
    """One AsyncExitStack PER SERVER, so one server can be restarted on its own."""

    async def __aenter__(self):
        self.stacks = {}
        for name in self.config["servers"]:
            await self._connect(name)
        return self

    async def __aexit__(self, *exc):
        for stack in self.stacks.values():
            try:
                await stack.aclose()
            except Exception:
                pass

    async def _connect(self, name):
        spec = self.config["servers"][name]
        stack = AsyncExitStack()
        await stack.__aenter__()
        params = StdioServerParameters(command=spec["command"], args=spec.get("args", []),
                                       env=base.server_env(spec))
        errlog = stack.enter_context(open(spec["log"], "a")) if spec.get("log") else sys.stderr
        client = await stack.enter_async_context(Client(stdio_client(params, errlog=errlog)))
        self.stacks[name], self.clients[name] = stack, client
        self.tools = [t for t in self.tools if not t["name"].startswith(name + SEP)]
        for tool in (await client.list_tools()).tools:
            self.tools.append({"name": f"{name}{SEP}{tool.name}",
                               "description": f"[{name}] {tool.description or ''}",
                               "input_schema": tool.input_schema})
        self.restarts = getattr(self, "restarts", 0)

    async def call(self, full_name, args):
        server, _, tool = full_name.partition(SEP)
        if server not in self.clients:
            return f"ERROR: unknown server '{server}'", True
        for attempt in (1, 2):
            try:
                result = await self.clients[server].call_tool(tool, args)
                text = "\n".join(b.text for b in result.content if isinstance(b, TextContent))
                return text, bool(result.is_error)
            except Exception as exc:                    # connection gone: restart once
                if attempt == 2:
                    return f"ERROR: server '{server}' failed after a restart: {exc}", True
                print(f"[hub] {server} failed ({type(exc).__name__}); restarting", file=sys.stderr)
                try:
                    await self.stacks[server].aclose()
                except Exception:
                    pass
                await self._connect(server)
                self.restarts += 1

    async def resource_context(self, budget=RESOURCE_BUDGET) -> str:
        """Exercise 13.5: read every server's resources for the system prompt."""
        parts, used = [], 0
        for name, client in self.clients.items():
            try:
                resources = (await client.list_resources()).resources
            except Exception:
                continue
            for r in resources:
                contents = (await client.read_resource(str(r.uri))).contents
                body = "\n".join(getattr(c, "text", "") for c in contents)
                chunk = f"## {name}: {r.uri}\n{body}\n"
                if used + len(chunk) > budget:
                    return "".join(parts) + "(more resources omitted: size limit)\n"
                parts.append(chunk); used += len(chunk)
        return "".join(parts)

async def run_with_resources(hub, question, messages=None):
    context = await hub.resource_context()
    system = "You are a helpful assistant.\n\nReference information:\n" + context
    return await base.run_mcp_agent(hub, question, system=system, messages=messages)
