import json
import os
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()


def llm(prompt: str, max_tokens: int = 2000) -> str:
    """One model call: send a prompt, get the reply's text back."""
    r = client.messages.create(model=MODEL, max_tokens=max_tokens,
                               messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in r.content if b.type == "text")


def parse_json(text: str) -> dict:
    """Models often wrap JSON in ```json ... ``` fences. Take the part between the
    first { and the last }, then json.loads it. Return {"parse_error": text} if that fails."""
    # TODO
    raise NotImplementedError


def handle_email(email: str) -> dict:
    """Three fixed steps: extract fields -> classify -> draft a reply.
    Return {"fields": ..., "category": "refund" | "shipping" | "other", "reply": ...}."""
    fields = parse_json(llm(f"Extract order_id and complaint as JSON only:\n{email}"))
    # TODO: step 2: classify (ask for ONE word; anything else counts as "other")
    # TODO: step 3: draft a polite reply
    raise NotImplementedError


if __name__ == "__main__":
    emails = ["Order #A1234 arrived broken, I want my money back.",
              "Where is my parcel? Order B777 was due Monday.",
              "Do you sponsor local football teams?"]
    for e in emails:
        print(json.dumps(handle_email(e), indent=1))
