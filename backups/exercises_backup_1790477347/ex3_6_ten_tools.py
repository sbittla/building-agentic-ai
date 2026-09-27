"""Exercise 3.6 (Complex): ten tools with near-duplicates, then fix by merging."""
from datetime import date, timedelta
import sol_ch03_tools as t3
from ex3_4_routing_eval import CASES as BASE_CASES
from sol_ch02_calculator_agent import client, MODEL

def add_days(start: str, days: int) -> str:
    return (date.fromisoformat(start) + timedelta(days=days)).isoformat()

def multiply(a: float, b: float) -> str:
    return str(a * b)

def is_weekend(day: str) -> str:
    return str(date.fromisoformat(day).weekday() >= 5)

def celsius_to_fahrenheit(c: float) -> str:
    return f"{c * 9 / 5 + 32:.1f} F"

def word_count(text: str) -> str:
    return str(len(text.split()))

def _schema(**props):
    return {"type": "object", "properties": {k: {"type": v} for k, v in props.items()},
            "required": list(props)}

EXTRA = {
    "add_days": (add_days, "Add a number of days to a date.", _schema(start="string", days="integer")),
    "multiply": (multiply, "Multiply two numbers.", _schema(a="number", b="number")),
    "is_weekend": (is_weekend, "Whether an ISO date is a Saturday or Sunday.", _schema(day="string")),
    "celsius_to_fahrenheit": (celsius_to_fahrenheit, "Convert Celsius to Fahrenheit.", _schema(c="number")),
    "word_count": (word_count, "Count words in a text.", _schema(text="string")),
}

# Ten tools: 5 from chapter 3 (incl. get_current_time) + 5 extra, two of them near-duplicates.
TEN_TOOLS = t3.TOOLS + [{"name": n, "description": d, "input_schema": s}
                        for n, (_, d, s) in EXTRA.items()]
REGISTRY = {**t3.REGISTRY, **{n: f for n, (f, _, _) in EXTRA.items()}}

# Fix: merge `multiply` into `calculate`, and make date tools say when to use which.
FIXED_TOOLS = [dict(t) for t in TEN_TOOLS if t["name"] != "multiply"]
for t in FIXED_TOOLS:
    if t["name"] == "calculate":
        t["description"] = ("Exact arithmetic on ANY numeric expression, including simple "
                            "multiplication. Not for dates or unit conversions.")
    if t["name"] == "add_days":
        t["description"] = ("Date N days after a given date. Use when the question gives a "
                            "start date and a number of days. For the gap between two "
                            "dates use days_between.")
    if t["name"] == "days_between":
        t["description"] += " Use when the question gives TWO dates."

NEW_CASES = [
    ("What date is 45 days after 2026-03-01?", "add_days"),
    ("What is 12 times 12?", "calculate"),
    ("Is 2026-10-03 a weekend?", "is_weekend"),
    ("30 C in Fahrenheit?", "celsius_to_fahrenheit"),
    ("How many words in 'the quick brown fox'?", "word_count"),
    ("Multiply 3.5 by 8.", "calculate"),
    ("Date 100 days after 2026-01-01?", "add_days"),
    ("Days from 2026-01-01 to 2026-04-11?", "days_between"),
    ("Is Christmas 2026 on a weekend? (2026-12-25)", "is_weekend"),
    ("What is 7 * 6?", "calculate"),
]
CASES = BASE_CASES + NEW_CASES

def accuracy(tools):
    correct, misses = 0, []
    for q, expected in CASES:
        r = client.messages.create(model=MODEL, max_tokens=2000, tools=tools,
                                   messages=[{"role": "user", "content": q}])
        got = next((b.name for b in r.content if b.type == "tool_use"), None)
        if got == "multiply" and expected == "calculate":
            got = "calculate"          # both are "the arithmetic tool" before the fix
        correct += got == expected
        if got != expected:
            misses.append((q, expected, got))
    return correct / len(CASES), misses

def main():
    before, miss_b = accuracy(TEN_TOOLS)
    after, miss_a = accuracy(FIXED_TOOLS)
    print(f"| version | tools | accuracy |\n| ten tools | {len(TEN_TOOLS)} | {before:.0%} |\n"
          f"| merged + clearer descriptions | {len(FIXED_TOOLS)} | {after:.0%} |")
    for q, e, g in miss_a:
        print(f"  still wrong: expected {e}, got {g}: {q}")
    return before, after

if __name__ == "__main__":
    main()
