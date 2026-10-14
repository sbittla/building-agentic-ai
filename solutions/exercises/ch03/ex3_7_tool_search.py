"""Exercise 3.7: tool search against loading every tool. Same questions, two setups; the
table shows accuracy (did the model reach the right tool?), searches and input tokens."""
import ch03_tool_search as ts

QUESTIONS = [  # (question, the tool that should be picked)
    ("Where is my order A1001?", "orders_get_status"),
    ("Cancel order A1002, it hasn't shipped.", "orders_cancel"),
    ("Where is parcel 1Z999 right now?", "shipping_track_parcel"),
    ("Refund $20 on order A1003.", "billing_refund"),
    ("How many vacation days does Ana Lima have left?", "hr_leave_balance"),
    ("Find a free half hour for Ana and Raj tomorrow.", "calendar_find_free_slot"),
    ("Is the VPN down?", "it_vpn_status"),
    ("What's the weather in Pune for the next three days?", "weather_forecast"),
    ("How many km is a marathon of 26.2 miles?", "basic_convert_units"),
    ("What is 17.5% of 84,213?", "basic_calculate"),
]
# Tools needed on most turns stay loaded: deferred, the model answers small sums from
# memory instead of searching for a calculator.
ALWAYS_LOADED = ("basic_get_current_date", "basic_calculate", "basic_convert_units")
SYSTEM = "Search for the tools you need before you use them."

def tools_reached(question, tools, max_steps=4):
    """Run a short loop and return every tool the model called, the searches it made,
    and the first call's input tokens (what the tool definitions cost). One call isn't
    enough: "tomorrow" needs today's date first, and a careful model checks an order's
    status before cancelling it."""
    messages = [{"role": "user", "content": question}]
    called, searches, first_tokens = [], [], None
    for _ in range(max_steps):
        r = ts.client.messages.create(model=ts.MODEL, max_tokens=2000, tools=tools,
                                      messages=messages, system=SYSTEM)
        first_tokens = first_tokens if first_tokens is not None else r.usage.input_tokens
        searches += [b.input for b in r.content if b.type == "server_tool_use"]
        uses = [b for b in r.content if b.type == "tool_use"]
        called += [b.name for b in uses]
        if not uses:
            break
        messages += [{"role": "assistant", "content": r.content},
                     {"role": "user", "content": [
                         {"type": "tool_result", "tool_use_id": b.id,
                          "content": ts.run_tool(b.name, b.input)} for b in uses]}]
    return called, searches, first_tokens

def compare(questions=QUESTIONS):
    setups = {"tool search": ts.with_tool_search(ts.ALL_TOOLS, ALWAYS_LOADED),
              "all loaded": ts.ALL_TOOLS}
    table = {}
    for label, tools in setups.items():
        right = tokens = n_search = 0
        misses = []
        for q, expected in questions:
            called, searches, input_tokens = tools_reached(q, tools)
            right += expected in called
            if expected not in called:
                misses.append(f"{q} -> {called or 'no tool'}")
            n_search += len(searches)
            tokens += input_tokens
        table[label] = {"accuracy": f"{right}/{len(questions)}", "searches": n_search,
                        "avg_input_tokens": tokens // len(questions), "misses": misses}
    return table

if __name__ == "__main__":
    for label, row in compare().items():
        misses = row.pop("misses")
        print(f"{label:<12} {row}")
        for m in misses:
            print(f"   missed: {m}")
    print("\nSwitch tool search on when the tool definitions are a large share of input tokens "
          "and accuracy holds up; below ~10 tools, loading everything is simpler.")
