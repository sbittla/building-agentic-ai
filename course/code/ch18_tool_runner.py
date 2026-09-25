"""Chapter 18 (1/3): the Anthropic SDK's tool runner. Your chapter 4 loop, built in."""
import os
from anthropic import Anthropic, beta_tool
import ch03_tools as t3

MODEL = os.environ.get("MODEL", "claude-sonnet-5")

@beta_tool
def get_current_date() -> str:
    """Today's date and weekday. Call this for anything relative to today."""
    return t3.get_current_date()

@beta_tool
def days_between(start: str, end: str) -> str:
    """Number of days between two dates and the weekday of the second one.

    Args:
        start: the first date, YYYY-MM-DD
        end: the second date, YYYY-MM-DD
    """
    return t3.days_between(start, end)

def ask(question: str, client=None) -> str:
    client = client or Anthropic()
    runner = client.beta.messages.tool_runner(
        model=MODEL, max_tokens=4096, max_iterations=8,        # the loop and its cap
        tools=[get_current_date, days_between],                # schemas come from the functions
        messages=[{"role": "user", "content": question}])
    final = None
    for message in runner:                                     # one item per model response
        for block in message.content:
            if block.type == "tool_use":
                print(f"  -> {block.name}({block.input})")
        final = message
    return "".join(b.text for b in final.content if b.type == "text")

if __name__ == "__main__":
    print(ask("How many days until July 4 next year, and what weekday is it?"))
