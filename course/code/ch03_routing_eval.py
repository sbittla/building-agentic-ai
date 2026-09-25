"""Chapter 3: measure which tool the model picks for each question."""
import os
from anthropic import Anthropic
from ch03_tools import TOOLS

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()

CASES = [  # (question, expected first tool or None for 'no tool')
    ("What day is it today?", "get_current_date"),
    ("How many km is 26.2 miles?", "convert_units"),
    ("What is 1234 * 5678?", "calculate"),
    ("How many days from 2026-01-01 to 2026-07-04?", "days_between"),
    ("What is a prime number?", None),
    # ... grow this list to 20 cases in the exercises
]

def first_tool(question: str):
    r = client.messages.create(model=MODEL, max_tokens=2000, tools=TOOLS,
                               messages=[{"role": "user", "content": question}])
    calls = [b.name for b in r.content if b.type == "tool_use"]
    return calls[0] if calls else None

correct = 0
for question, expected in CASES:
    got = first_tool(question)
    ok = got == expected
    correct += ok
    print(f"{'PASS' if ok else 'FAIL'}  expected={expected!s:17} got={got!s:17} {question}")
print(f"Routing accuracy: {correct}/{len(CASES)} = {correct/len(CASES):.0%}")
