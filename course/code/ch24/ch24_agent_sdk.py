"""Chapter 24 (2/3): the Claude Agent SDK. The agent runtime behind Claude Code, with
your own tools, permissions, turn and budget limits."""
import asyncio
import os
from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions,
                              PermissionResultAllow, PermissionResultDeny,
                              ResultMessage, TextBlock, ToolUseBlock,
                              create_sdk_mcp_server, query, tool)
import ch08_sql_tools as sql

MODEL = os.environ.get("MODEL", "claude-sonnet-5")

# Tools are async functions that return MCP-style content. They run in YOUR process.
@tool("get_schema",
      "CREATE TABLE statements for the shop database. Call before writing SQL.", {})
async def get_schema(args: dict) -> dict:
    return {"content": [{"type": "text", "text": sql.get_schema()}]}

@tool("run_query",
      "Run one read-only SQLite SELECT on the shop database (max 50 rows).",
      {"sql": str})
async def run_query(args: dict) -> dict:
    out = sql.run_query(args["sql"])
    return {"content": [{"type": "text", "text": out}],
            "is_error": out.startswith("ERROR")}

# an in-process MCP server
SHOP = create_sdk_mcp_server("shop", tools=[get_schema, run_query])

decisions = []                                      # an audit log, as in chapter 9

async def approve(tool_name: str, tool_input: dict,
                  context) -> PermissionResultAllow | PermissionResultDeny:
    """The approval gate from chapter 9, as a callback the runtime must obey.
    It is only consulted for tools NOT listed in allowed_tools."""
    if (tool_name == "mcp__shop__run_query" and
            tool_input.get("sql", "").lstrip().lower().startswith(("select", "with"))):
        decisions.append((tool_name, "allow"))
        return PermissionResultAllow()
    decisions.append((tool_name, "deny"))
    return PermissionResultDeny(message=f"{tool_name} with this input is not allowed.")

OPTIONS = ClaudeAgentOptions(
    model=MODEL,
    system_prompt=sql.SYSTEM,
    tools=[],                                  # no built-in tools (files, shell, web)
    mcp_servers={"shop": SHOP},
    strict_mcp_config=True,                    # ONLY these servers, none from settings
    setting_sources=[],                        # ignore user/project settings files
    allowed_tools=["mcp__shop__get_schema"],   # auto-approved (read-only, harmless)
    can_use_tool=approve,                      # everything else goes through approve()
    max_turns=8,                               # the iteration cap
    max_budget_usd=0.50,                       # a hard cost limit per run
)

async def _prompt(text: str):
    """can_use_tool needs "streaming input":
    the prompt as an async stream of messages."""
    yield {"type": "user", "message": {"role": "user", "content": text}}

async def ask(question: str) -> str:
    answer = ""
    async for message in query(prompt=_prompt(question), options=OPTIONS):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"  -> {block.name}({block.input})")
                elif isinstance(block, TextBlock):
                    answer = block.text
        elif isinstance(message, ResultMessage):
            print(f"  [{message.num_turns} turns, ${message.total_cost_usd or 0:.4f}]")
    return answer

if __name__ == "__main__":
    import sys
    question = (" ".join(sys.argv[1:])
                or "Which product category earns the most revenue?")
    print(asyncio.run(ask(question)))
    print("Approval decisions:", decisions)
