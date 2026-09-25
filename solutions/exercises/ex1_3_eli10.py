"""Exercise 1.3 (Simple): Your first call — compare two system prompts."""
import os
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()

# Same text as ch01_summarize.py (importing that file would run its API call).
EMAIL = """
Hi team, I ordered a standing desk (order #4471) on 2 September and paid for
express delivery. It was supposed to arrive last Friday but tracking still says
"label created". I've taken Monday off to assemble it. Can you tell me where it
is, and refund the express fee if it won't arrive by Saturday? Thanks, Priya
"""

def summarize(system: str):
    r = client.messages.create(
        model=MODEL, max_tokens=2000, system=system,
        messages=[{"role": "user", "content": f"Summarize this customer email in one sentence, including what they want:\n{EMAIL}"}])
    return "".join(b.text for b in r.content if b.type == "text"), r.usage.input_tokens, r.usage.output_tokens

def main():
    rows = []
    for system in ["You are a concise technical writer.", "Explain like I am 10 years old."]:
        text, tin, tout = summarize(system)
        rows.append((system, tin, tout, text))
        print(f"\n[{system}]\n{text}")
    print("\n| system prompt | input tokens | output tokens |")
    for system, tin, tout, _ in rows:
        print(f"| {system} | {tin} | {tout} |")
    return rows

if __name__ == "__main__":
    main()
