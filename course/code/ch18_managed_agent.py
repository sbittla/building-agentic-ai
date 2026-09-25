"""Chapter 18: Claude Managed Agents. Anthropic runs the agent loop, the sandbox and the
built-in tools (bash, read, write, edit, glob, grep, web fetch and search) for you. You
define an agent once, give it an environment to work in, and start sessions; your code
watches a stream of events and answers when the agent needs something from you.

Two things still happen in YOUR code, on purpose:
  * run_query: a "custom tool", so the shop database never leaves your machine.
  * approvals: bash is set to always_ask, so every shell command waits for your OK.
A budget caps what one session may spend.

Run:  python ch18_managed_agent.py     (uses the real API: creates an agent, environment
                                         and session, then archives the session)"""
import os
import ch08_sql_tools as sql
from ch04_agent import get_client

MODEL = os.environ.get("MODEL", "claude-sonnet-5")

RUN_QUERY = {
    "type": "custom", "name": "run_query",
    "description": "Run one read-only SQL SELECT on the shop database (tables: customers, "
                   "products, orders, order_items). Returns up to 50 rows as a text table.",
    "input_schema": {"type": "object", "properties": {"sql": {"type": "string"}},
                     "required": ["sql"]},
}

AGENT = {
    "name": "shop-analyst",
    "model": MODEL,
    "system": "You analyze the shop's sales. Use run_query for data. You may write files and "
              "charts in your sandbox. Never guess a number.",
    "tools": [
        {"type": "agent_toolset_20260401",
         "default_config": {"permission_policy": {"type": "always_allow"}},
         "configs": [{"name": "bash", "permission_policy": {"type": "always_ask"}},
                     {"name": "web_search", "enabled": False},
                     {"name": "web_fetch", "enabled": False}]},
        RUN_QUERY,
    ],
}

ENVIRONMENT = {"name": "shop-analyst-env",
               "config": {"type": "cloud",
                          "networking": {"type": "limited", "allowed_hosts": []}}}   # no internet

BUDGET = {"type": "limit", "max_list_cost": {"amount": "100", "currency": "USD"}}   # $1.00

def console_approve(event) -> bool:
    print(f"\n[approval] {event.name}: {event.input}")
    return input("Allow? [y/N] ").strip().lower() == "y"

def handle(event, approve=console_approve) -> list[dict]:
    """Turn one event into the events we send back (usually none)."""
    if event.type == "agent.message":
        for block in event.content:
            if block.type == "text":
                print(block.text, end="", flush=True)
    elif event.type == "agent.custom_tool_use" and event.name == "run_query":
        result = sql.run_tool("run_query", event.input)          # runs HERE, not in the cloud
        print(f"\n[run_query] {event.input.get('sql', '')[:70]}")
        return [{"type": "user.custom_tool_result", "custom_tool_use_id": event.id,
                 "content": [{"type": "text", "text": result}],
                 "is_error": result.startswith("ERROR")}]
    elif event.type in ("agent.tool_use", "agent.mcp_tool_use"):
        if getattr(event, "evaluated_permission", None) == "ask":
            ok = approve(event)
            return [{"type": "user.tool_confirmation", "tool_use_id": event.id,
                     "result": "allow" if ok else "deny",
                     **({} if ok else {"deny_message": "The user declined this command."})}]
        print(f"\n[{event.name}]", end="")
    return []

def run(question: str, client=None, approve=console_approve) -> str:
    """Create everything, run one question to the end, archive the session. Returns why it ended."""
    client = client or get_client()
    agent = client.beta.agents.create(**AGENT)
    env = client.beta.environments.create(**ENVIRONMENT)
    session = client.beta.sessions.create(agent=agent.id, environment_id=env.id,
                                          title=question[:60], budget=BUDGET)
    ended = "stream closed"
    try:
        with client.beta.sessions.events.stream(session.id) as stream:
            client.beta.sessions.events.send(session.id, events=[
                {"type": "user.message", "content": [{"type": "text", "text": question}]}])
            for event in stream:
                replies = handle(event, approve)
                if replies:
                    client.beta.sessions.events.send(session.id, events=replies)
                if event.type == "session.status_idle" and event.stop_reason.type != "requires_action":
                    ended = event.stop_reason.type           # end_turn, budget_reached, ...
                    break
                if event.type == "session.error":
                    ended = "error"
                    break
    finally:
        client.beta.sessions.archive(session.id)
    print(f"\n\n[session ended: {ended}]")
    return ended

if __name__ == "__main__":
    run("Which product category earns the most revenue? Then save a CSV of revenue by "
        "category in your sandbox and show me the command you used.")
