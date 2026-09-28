"""Exercise 24.4 (solution): the Agent SDK with an in-process server AND a stdio server.

Reads (schema, list_tasks) are auto-approved; run_query must be a SELECT; add_task
needs a human yes/no, asked through can_use_tool."""
import asyncio
from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, PermissionResultAllow,
                              PermissionResultDeny, TextBlock, ToolUseBlock, query)
import ch08_sql_tools as sql
from ch24_agent_sdk import MODEL, SHOP, _prompt

decisions = []

def ask_human(tool_name, tool_input) -> bool:
    return input(f"Allow {tool_name}({tool_input})? [y/N] ").strip().lower() == "y"

APPROVER = ask_human                   # tests replace this with an automatic answer

async def approve(tool_name, tool_input, context):
    if tool_name == "mcp__shop__run_query":
        ok = tool_input.get("sql", "").lstrip().lower().startswith(("select", "with"))
    elif tool_name == "mcp__todo__add_task":
        ok = await asyncio.to_thread(APPROVER, tool_name, tool_input)
    else:
        ok = False                                      # anything unexpected: deny
    decisions.append((tool_name, "allow" if ok else "deny"))
    # say the "no" is final, or a small model retries the same call until max_turns
    return PermissionResultAllow() if ok else PermissionResultDeny(
        message=f"{tool_name} was not approved. The decision is final: don't call it "
                "again; tell the user it wasn't done.")

def options(python="python"):
    return ClaudeAgentOptions(
        model=MODEL,
        system_prompt=sql.SYSTEM + " You also manage the user's to-do list.",
        tools=[],
        mcp_servers={"shop": SHOP,                                       # in-process
                     "todo": {"type": "stdio", "command": python,         # a separate process
                              "args": ["ch13_todo_server.py"]}},
        strict_mcp_config=True,
        setting_sources=[],
        allowed_tools=["mcp__shop__get_schema", "mcp__todo__list_tasks"],
        can_use_tool=approve,
        max_turns=10,
        max_budget_usd=0.50,
    )

async def ask(question: str, python="python") -> str:
    answer = ""
    async for message in query(prompt=_prompt(question), options=options(python)):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"  -> {block.name}({block.input})")
                elif isinstance(block, TextBlock):
                    answer = block.text
    return answer

if __name__ == "__main__":
    print(asyncio.run(ask("Find our best-selling product category, then add a to-do "
                          "'review <category> pricing' due 2026-10-15.")))
    print("Decisions:", decisions)
