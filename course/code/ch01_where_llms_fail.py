"""Chapter 1: three questions a plain LLM cannot answer reliably."""
import os
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()

QUESTIONS = [
    "What is today's date? Answer with just the date.",
    "What is 48213 * 9771? Answer with just the number.",
    "What is the Wi-Fi password written in my file home_notes.txt?",
]

for q in QUESTIONS:
    r = client.messages.create(model=MODEL, max_tokens=2000,
                               messages=[{"role": "user", "content": q}])
    answer = "".join(b.text for b in r.content if b.type == "text")   # skip thinking blocks
    print(f"Q: {q}\nA: {answer}\n")

print("Correct product:", 48213 * 9771)
