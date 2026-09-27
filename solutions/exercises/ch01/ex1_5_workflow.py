"""Exercise 1.5 (Medium): a fixed three-step workflow (NOT an agent)."""
import json
import os
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()

def llm(prompt: str, max_tokens: int = 2000) -> str:
    r = client.messages.create(model=MODEL, max_tokens=max_tokens,
                               messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in r.content if b.type == "text").strip()

def parse_json(text: str) -> dict:
    """Models sometimes wrap JSON in ``` fences or add a sentence; be forgiving."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in reply")
    return json.loads(text[start:end + 1])

def handle_email(email: str) -> dict:
    # Step 1: extract
    raw = llm("Extract these fields from the email as JSON with keys order_id "
              "(string or null) and complaint (short string). Reply with JSON only.\n\n"
              f"{email}")
    try:
        fields = parse_json(raw)
    except (ValueError, json.JSONDecodeError):
        fields = {"order_id": None, "complaint": email[:200], "parse_error": True}
    # Step 2: classify (a closed set, validated in code)
    category = llm(f"Classify this support request as exactly one word: refund, shipping "
                   f"or other.\n{json.dumps(fields)}").lower().strip(" .")
    if category not in {"refund", "shipping", "other"}:
        category = "other"
    # Step 3: draft
    reply = llm(f"Draft a short, polite reply for a {category} request.\n{json.dumps(fields)}")
    return {"fields": fields, "category": category, "reply": reply}

EMAILS = [
    "Order #A1234 arrived broken. I want my money back.",
    "Where is my package? Order B-5521 was due last Friday.",
    "Can I change the delivery address for order 7788?",
    "Your checkout page is really slow today.",
    "Hi! Do you sponsor local football teams?",       # not a support request at all
]

def main():
    results = []
    for e in EMAILS:
        out = handle_email(e)
        results.append(out)
        print(f"\nEMAIL: {e}\n  -> {out['category']} | {out['fields']}\n  REPLY: {out['reply'][:120]}")
    print("\nNote: the workflow always drafts a reply, even for the sponsorship email "
          "and the address change it has no way to perform. It can't look anything up.")
    return results

if __name__ == "__main__":
    main()
