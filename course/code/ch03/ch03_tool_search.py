"""Chapter 3: many tools without the confusion. A company agent can easily have forty
tools. Here the model gets this chapter's four real tools plus a catalogue of 36 more,
but most are marked defer_loading: the model sees only their NAMES until it searches for
what it needs. The search runs on Anthropic's servers (a "server tool"), so your code
still runs only YOUR tools.

The catalogue tools are stand-ins: each has a real name, description and schema, but
returns a fixed reply. That's all tool search needs, and it keeps this chapter free of
code you haven't met yet.

Run:  python ch03_tool_search.py"""
import os
from anthropic import Anthropic
import ch03_tools

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()

# (area, name, description, {parameter: description}) for every catalogue tool.
# Namespaced names (orders_get_status, hr_request_leave, ...) help both search and routing.
CATALOGUE = [
    ("orders", "get_status", "Current status and delivery estimate of an order, by order id.", {"order_id": "e.g. A1001"}),
    ("orders", "list_recent", "A customer's most recent orders, newest first.", {"email": "the customer's email"}),
    ("orders", "cancel", "Cancel an order that hasn't shipped yet.", {"order_id": "e.g. A1001"}),
    ("orders", "start_return", "Start a return for a delivered order and email the label.", {"order_id": "e.g. A1001", "reason": "why it's coming back"}),
    ("shipping", "track_parcel", "Where a parcel is now, by carrier tracking number.", {"tracking_number": "the carrier's number"}),
    ("shipping", "quote", "Shipping price and days for a weight and destination country.", {"weight_kg": "parcel weight", "country": "ISO country code"}),
    ("billing", "get_invoice", "The invoice for an order, as a link to a PDF.", {"order_id": "e.g. A1001"}),
    ("billing", "refund", "Refund part or all of a payment to the original card.", {"order_id": "e.g. A1001", "amount": "in the order's currency"}),
    ("billing", "update_card", "Send the customer a secure link to change the card on file.", {"email": "the customer's email"}),
    ("crm", "find_customer", "Look up a customer by email, phone or name.", {"query": "email, phone or name"}),
    ("crm", "add_note", "Add a note to a customer's record.", {"email": "the customer's email", "note": "the note"}),
    ("crm", "loyalty_points", "A customer's loyalty points balance.", {"email": "the customer's email"}),
    ("catalog", "search_products", "Search the product catalog by keyword.", {"query": "what to look for"}),
    ("catalog", "stock_level", "Units in stock for a product, per warehouse.", {"product_id": "e.g. P-2"}),
    ("catalog", "price", "The current price of a product.", {"product_id": "e.g. P-2"}),
    ("hr", "request_leave", "Request days off for an employee.", {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}),
    ("hr", "leave_balance", "How many vacation days an employee has left this year.", {"employee": "name or id"}),
    ("hr", "find_colleague", "Find a colleague's team, manager and office.", {"name": "full or partial name"}),
    ("calendar", "find_free_slot", "Find a meeting time when everyone listed is free.", {"people": "comma-separated names", "minutes": "meeting length"}),
    ("calendar", "book_room", "Book a meeting room for a time slot.", {"room": "room name", "start": "ISO date and time"}),
    ("calendar", "list_events", "Events on someone's calendar for a day.", {"person": "name", "day": "YYYY-MM-DD"}),
    ("it", "reset_password", "Send a password-reset link to an employee.", {"employee": "name or id"}),
    ("it", "open_ticket", "Open an IT support ticket.", {"summary": "one line", "priority": "low, normal or high"}),
    ("it", "vpn_status", "Whether the company VPN is up, and any open incident.", {}),
    ("finance", "exchange_rate", "Today's exchange rate between two currencies.", {"from_currency": "e.g. USD", "to_currency": "e.g. EUR"}),
    ("finance", "submit_expense", "Submit an expense with an amount and a category.", {"amount": "number", "category": "travel, meals or other"}),
    ("finance", "budget_left", "How much of a team's quarterly budget is left.", {"team": "team name"}),
    ("weather", "forecast", "The weather forecast for a city for the next days.", {"city": "city name", "days": "1 to 7"}),
    ("weather", "air_quality", "Today's air quality index for a city.", {"city": "city name"}),
    ("travel", "flight_status", "Departure and arrival times of a flight today.", {"flight": "e.g. LH123"}),
    ("travel", "find_hotel", "Hotels near an address with prices for given dates.", {"near": "address or landmark", "check_in": "YYYY-MM-DD"}),
    ("docs", "search_wiki", "Search the company wiki for a page.", {"query": "what to look for"}),
    ("docs", "summarize_page", "Summarize a wiki page, by its URL.", {"url": "page URL"}),
    ("tasks", "add_task", "Add a task to someone's to-do list.", {"title": "what to do", "due": "YYYY-MM-DD"}),
    ("tasks", "list_tasks", "List someone's open tasks.", {}),
    ("tasks", "complete_task", "Mark a task as done, by task id.", {"task_id": "the task's number"}),
]

ALL_TOOLS, ROUTES = [], {}
for tool in ch03_tools.TOOLS:                          # this chapter's real tools
    name = f"basic_{tool['name']}"
    ALL_TOOLS.append({**tool, "name": name})
    ROUTES[name] = tool["name"]
for area, short, description, params in CATALOGUE:     # the stand-ins
    ALL_TOOLS.append({"name": f"{area}_{short}", "description": description,
                      "input_schema": {"type": "object",
                                       "properties": {p: {"type": "string", "description": d}
                                                      for p, d in params.items()},
                                       "required": list(params)}})

SEARCH_TOOL = {"type": "tool_search_tool_bm25_20251119",
               "name": "tool_search_tool_bm25"}

def with_tool_search(tools, always_loaded=("basic_get_current_date",)):
    """The tool search tool first, then every tool, deferred unless it's needed on
    most turns. Deferred tools cost almost no context until the model finds and
    loads them."""
    return [SEARCH_TOOL] + [t if t["name"] in always_loaded
                            else {**t, "defer_loading": True} for t in tools]

def run_tool(name, args):
    if name in ROUTES:
        return ch03_tools.run_tool(ROUTES[name], args)
    if any(t["name"] == name for t in ALL_TOOLS):
        return f"(stand-in) {name} would run here with {args}"
    return f"ERROR: unknown tool {name}"

def choose(question, tools):
    """One model call: which tool does the model pick (and with which arguments), what did
    it search for, and how many input tokens did the call cost? The search happens inside
    the same response, so one call is enough to see it."""
    r = client.messages.create(model=MODEL, max_tokens=2000, tools=tools,
                               messages=[{"role": "user", "content": question}],
                               system="Search for the tools you need before you use them.")
    picked = [b for b in r.content if b.type == "tool_use"]
    searches = [b.input for b in r.content if b.type == "server_tool_use"]
    name, args = (picked[0].name, picked[0].input) if picked else (None, None)
    return name, args, searches, r.usage.input_tokens

if __name__ == "__main__":
    print(f"{len(ALL_TOOLS)} tools available, 1 loaded up front.\n")
    for q in ("Where is my parcel? The tracking number is 1Z999.",
              "How many vacation days do I have left?",
              "How many km is 26.2 miles?"):
        name, args, searches, tokens = choose(q, with_tool_search(ALL_TOOLS))
        print(f"{q}\n  searched: {searches}\n  picked:   {name}   ({tokens} input tokens)")
        if name:
            print(f"  result:   {run_tool(name, args)}\n")
