"""Exercise 3.7: tool search against loading every tool. Same questions, two setups; the
table shows accuracy (did the model pick the right tool?), searches and input tokens."""
import ch03_tool_search as ts

QUESTIONS = [  # (question, the tool that should be picked)
    ("Where is my order A1001?", "orders_get_status"),
    ("Cancel order A1002, it hasn't shipped.", "orders_cancel"),
    ("Where is parcel 1Z999 right now?", "shipping_track_parcel"),
    ("Refund $20 on order A1003.", "billing_refund"),
    ("How many vacation days do I have left?", "hr_leave_balance"),
    ("Find a free half hour for Ana and Raj tomorrow.", "calendar_find_free_slot"),
    ("Is the VPN down?", "it_vpn_status"),
    ("What's the weather in Pune for the next three days?", "weather_forecast"),
    ("How many km is a marathon of 26.2 miles?", "basic_convert_units"),
    ("What is 17.5% of 84,213?", "basic_calculate"),
]

def compare(questions=QUESTIONS):
    setups = {"tool search": ts.with_tool_search(ts.ALL_TOOLS), "all loaded": ts.ALL_TOOLS}
    table = {}
    for label, tools in setups.items():
        right = tokens = n_search = 0
        for q, expected in questions:
            name, _, searches, input_tokens = ts.choose(q, tools)
            right += name == expected
            n_search += len(searches)
            tokens += input_tokens
        table[label] = {"accuracy": f"{right}/{len(questions)}", "searches": n_search,
                        "avg_input_tokens": tokens // len(questions)}
    return table

if __name__ == "__main__":
    for label, row in compare().items():
        print(f"{label:<12} {row}")
    print("\nSwitch tool search on when the tool definitions are a large share of input tokens "
          "and accuracy holds up; below ~10 tools, loading everything is simpler.")
