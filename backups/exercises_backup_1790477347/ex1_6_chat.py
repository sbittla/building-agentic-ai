"""Exercise 1.6 (Medium): remembering a conversation (and breaking it on purpose)."""
import os
import sys
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()

def chat_turn(history: list, user_text: str, remember: bool = True) -> tuple[str, list]:
    history = history + [{"role": "user", "content": user_text}]
    sent = history if remember else history[-1:]       # broken mode: latest message only
    r = client.messages.create(model=MODEL, max_tokens=2000, messages=sent)
    answer = "".join(b.text for b in r.content if b.type == "text")
    return answer, history + [{"role": "assistant", "content": answer}]

def demo(remember: bool):
    history = []
    for msg in ["Hi, my name is Srini.", "What's the capital of France?", "What's my name?"]:
        answer, history = chat_turn(history, msg, remember)
        print(f"You: {msg}\nModel: {answer}\n")
    return answer

if __name__ == "__main__":
    remember = "--broken" not in sys.argv
    print("=== WITH history ===" if remember else "=== WITHOUT history (broken) ===")
    demo(remember)
