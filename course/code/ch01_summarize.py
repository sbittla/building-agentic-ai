"""Chapter 1: a single LLM call. This is NOT an agent: no tools, no loop."""
import os
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment

EMAIL = """
Hi team, I ordered a standing desk (order #4471) on 2 September and paid for
express delivery. It was supposed to arrive last Friday but tracking still says
"label created". I've taken Monday off to assemble it. Can you tell me where it
is, and refund the express fee if it won't arrive by Saturday? Thanks, Priya
"""

response = client.messages.create(
    model=MODEL,
    max_tokens=2000,
    system="You are a concise technical writer.",
    messages=[{"role": "user", "content":
               f"Summarize this customer email in one sentence, including what they want:\n{EMAIL}"}],
)

# The reply is a LIST of content blocks. Claude Sonnet 5 thinks before it answers, so the list
# can start with a (hidden) "thinking" block: always pick the text blocks by their type.
answer = "".join(block.text for block in response.content if block.type == "text")
print(answer)
print(f"input tokens={response.usage.input_tokens} "
      f"output tokens={response.usage.output_tokens} "
      f"stop_reason={response.stop_reason}")
