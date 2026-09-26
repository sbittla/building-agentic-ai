"""Chapter 3: many tools without the confusion. Every tool from chapters 3 to 8 goes to
the model, but most are marked defer_loading: the model sees only their NAMES until it
searches for what it needs. The search runs on Anthropic's servers (a "server tool"), so
the agent loop from chapter 4 doesn't change: it still runs only YOUR tools.

Run:  python ch03_tool_search.py"""
import ch03_tools, ch05_todo_tools, ch06_notes_tools, ch07_weather_tools, ch08_sql_tools

MODULES = {"basic": ch03_tools, "todo": ch05_todo_tools, "notes": ch06_notes_tools,
           "weather": ch07_weather_tools, "sql": ch08_sql_tools}

# Namespaced names (todo_add_task, sql_run_query, ...) help both search and routing.
ALL_TOOLS, ROUTES = [], {}
for prefix, module in MODULES.items():
    for tool in module.TOOLS:
        name = f"{prefix}_{tool['name']}"
        ALL_TOOLS.append({**tool, "name": name})
        ROUTES[name] = (module, tool["name"])

SEARCH_TOOL = {"type": "tool_search_tool_bm25_20251119",
               "name": "tool_search_tool_bm25"}

def with_tool_search(tools, always_loaded=("basic_get_current_date",)):
    """The tool search tool first, then every tool, deferred unless it's needed on
    most turns. Deferred tools cost almost no context until the model finds and
    loads them."""
    return [SEARCH_TOOL] + [t if t["name"] in always_loaded
                            else {**t, "defer_loading": True} for t in tools]

def run_tool(name, args):
    if name not in ROUTES:
        return f"ERROR: unknown tool {name}"
    module, original = ROUTES[name]
    return module.run_tool(original, args)

if __name__ == "__main__":
    from ch04_agent import run_agent
    print(f"{len(ALL_TOOLS)} tools available, 1 loaded up front.\n")
    answer, messages, stats = run_agent(
        "How many orders are in the shop database, "
        "and what's the weather in Pune tomorrow?",
        with_tool_search(ALL_TOOLS), run_tool,
        system="Search for the tools you need before you use them.")
    searched = [b.input for m in messages
                if m["role"] == "assistant" and not isinstance(m["content"], str)
                for b in m["content"] if getattr(b, "type", "") == "server_tool_use"]
    print("\nSearches the model made:", searched)
    print(answer)
