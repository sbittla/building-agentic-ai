"""Exercise 3.8: tool search against loading every tool. Same questions, two setups; the
table shows accuracy (was the right tool used?), searches and first-call input tokens."""
import ch03_tool_search as ts
from ch04_agent import run_agent

QUESTIONS = [  # (question, the tool that should be used)
    ("How many orders are in the shop?", "sql_run_query"),
    ("What tables does the shop database have?", "sql_get_schema"),
    ("Add 'renew passport' to my to-do list for Friday.", "todo_add_task"),
    ("What's on my to-do list?", "todo_list_tasks"),
    ("Which of my notes mention the VPN?", "notes_search_files"),
    ("What's the weather in Pune for the next three days?", "weather_get_forecast"),
    ("How many km is a marathon of 26.2 miles?", "basic_convert_units"),
    ("What is 17.5% of 84,213?", "basic_calculate"),
    ("How many days until 2027-01-01?", "basic_days_between"),
    ("Where is Springfield? Give me its coordinates.", "weather_geocode"),
]

def used_tools(messages):
    return [b.name for m in messages if m["role"] == "assistant" and not isinstance(m["content"], str)
            for b in m["content"] if getattr(b, "type", "") == "tool_use"]

def searches(messages):
    return sum(1 for m in messages if m["role"] == "assistant" and not isinstance(m["content"], str)
               for b in m["content"] if getattr(b, "type", "") == "server_tool_use")

def compare(questions=QUESTIONS):
    setups = {"tool search": ts.with_tool_search(ts.ALL_TOOLS), "all loaded": ts.ALL_TOOLS}
    table = {}
    for label, tools in setups.items():
        right = tokens = n_search = 0
        for q, expected in questions:
            _, messages, stats = run_agent(q, tools, ts.run_tool, verbose=False, max_iterations=6)
            right += expected in used_tools(messages)
            n_search += searches(messages)
            tokens += stats["input_tokens"]
        table[label] = {"accuracy": f"{right}/{len(questions)}", "searches": n_search,
                        "avg_input_tokens": tokens // len(questions)}
    return table

if __name__ == "__main__":
    for label, row in compare().items():
        print(f"{label:<12} {row}")
    print("\nSwitch tool search on when the tool definitions are a large share of input tokens "
          "and accuracy holds up; below ~10 tools, loading everything is simpler.")
