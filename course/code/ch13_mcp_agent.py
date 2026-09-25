"""Chapter 13: an agent whose tools come from MCP servers, discovered at run time."""
import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from anthropic import AsyncAnthropic
from mcp import Client, StdioServerParameters
from mcp.client.stdio import get_default_environment, stdio_client
from mcp_types import TextContent
from ch04_agent import next_action        # the same stop-reason rules as chapter 4

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
SEP = "__"                                    # tool names become server__tool

# Servers get a MINIMAL environment, never your whole one: a third-party server has no
# business seeing ANTHROPIC_API_KEY. A server that needs a secret names it in "pass_env".
SAFE_ENV = ("PYTHONPATH", "PYTHONDONTWRITEBYTECODE", "LANG", "LC_ALL", "TZ",
            "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy",
            "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE")

def server_env(spec: dict) -> dict:
    env = get_default_environment()                       # HOME, PATH (and similar)
    for name in (*SAFE_ENV, *spec.get("pass_env", [])):
        if name in os.environ:
            env[name] = os.environ[name]
    return {**env, **spec.get("env", {})}

class MCPHub:
    """Connects to several MCP servers and routes tool calls to the right one."""

    def __init__(self, config: dict):
        self.config = config                  # {"servers": {name: {command, args, env}}}
        self.clients: dict[str, Client] = {}
        self.tools: list[dict] = []           # in Anthropic's tool format
        self.stack = AsyncExitStack()

    async def __aenter__(self):
        await self.stack.__aenter__()
        for name, spec in self.config["servers"].items():
            try:
                await self._connect(name, spec)
            except Exception as exc:          # name the server that failed, and how to debug it
                await self.stack.aclose()
                cmd = " ".join([spec["command"], *spec.get("args", [])])
                raise RuntimeError(f"MCP server '{name}' failed to start ({type(exc).__name__}). "
                                   f"Run it yourself to see its error:  {cmd}") from exc
        return self

    async def _connect(self, name, spec):
        params = StdioServerParameters(command=spec["command"],
                                       args=spec.get("args", []),
                                       env=server_env(spec))
        # "log": "file.log" in the config sends that server's stderr to a file
        # (handy for noisy third-party servers); otherwise it shows in your terminal.
        errlog = sys.stderr
        if spec.get("log"):
            errlog = self.stack.enter_context(open(spec["log"], "a"))
        client = await self.stack.enter_async_context(
            Client(stdio_client(params, errlog=errlog)))
        self.clients[name] = client
        for tool in (await client.list_tools()).tools:
            self.tools.append({
                "name": f"{name}{SEP}{tool.name}",          # namespacing
                "description": f"[{name}] {tool.description or ''}",
                "input_schema": tool.input_schema})

    async def __aexit__(self, *exc):
        await self.stack.__aexit__(*exc)

    async def call(self, full_name: str, args: dict) -> tuple[str, bool]:
        server, _, tool = full_name.partition(SEP)
        if server not in self.clients:
            return f"ERROR: unknown server '{server}'", True
        result = await self.clients[server].call_tool(tool, args)
        text = "\n".join(b.text for b in result.content if isinstance(b, TextContent))
        return text, bool(result.is_error)

async def run_mcp_agent(hub: MCPHub, question: str, system: str = "",
                        messages=None, max_iterations: int = 10, before_call=None,
                        should_stop=None, stats=None, max_tokens: int = 4096):
    """The chapter 4 loop, with tools discovered from MCP servers.
    before_call(name, args) -> None or a refusal string (used for policy in ch14).
    should_stop(stats) and stats work exactly as in run_agent: pass a dict as `stats`
    to get steps, tool calls and tokens back, and should_stop to enforce a budget."""
    llm = AsyncAnthropic()
    stats = stats if stats is not None else {}
    for key in ("steps", "tool_calls", "input_tokens", "output_tokens"):
        stats.setdefault(key, 0)
    messages = list(messages or []) + [{"role": "user", "content": question}]
    for step in range(1, max_iterations + 1):
        r = await llm.messages.create(model=MODEL, max_tokens=max_tokens, tools=hub.tools,
                                      system=system or "You are a helpful assistant.",
                                      messages=messages)
        stats["steps"] += 1
        stats["input_tokens"] += r.usage.input_tokens
        stats["output_tokens"] += r.usage.output_tokens
        stats["stop_reason"] = r.stop_reason
        messages.append({"role": "assistant", "content": r.content})
        action, note = next_action(r)
        text = "".join(b.text for b in r.content if b.type == "text")
        if action == "done":
            return text, messages
        if action == "stop":
            return f"{text}\n\n[Stopped: {note}]".strip(), messages
        if action == "continue":
            continue
        results = []
        for b in r.content:
            if b.type != "tool_use":
                continue
            refusal = before_call(b.name, b.input) if before_call else None
            if refusal:
                text, is_error = refusal, True
            else:
                try:
                    text, is_error = await hub.call(b.name, b.input)
                except Exception as exc:     # a crashed server is an error result, not a crash
                    text, is_error = f"ERROR: {b.name} failed ({type(exc).__name__}: {exc})", True
            stats["tool_calls"] += 1
            print(f"[step {step}] {b.name}({json.dumps(b.input)[:80]}) -> {text[:70]!r}",
                  file=sys.stderr)
            results.append({"type": "tool_result", "tool_use_id": b.id,
                            "content": text, "is_error": is_error})
        messages.append({"role": "user", "content": results})
        if should_stop and (reason := should_stop(stats)):
            return f"Stopped early: {reason}", messages
    return f"Stopped at max_iterations={max_iterations}.", messages

async def main():
    config = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "servers.json"))
    async with MCPHub(config) as hub:
        print("Tools:", [t["name"] for t in hub.tools])
        history = []
        while True:
            q = (await asyncio.to_thread(input, "\nYou: ")).strip()
            if q in ("quit", "exit"):
                break
            answer, history = await run_mcp_agent(hub, q, messages=history)
            print("Agent:", answer)

if __name__ == "__main__":
    asyncio.run(main())
