import os
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()


def chat(remember: bool = True):
    """A chat loop. With remember=True, keep ALL messages in `history` and send them
    every time. With remember=False, send only the newest message (the broken version)."""
    history = []
    while (text := input("You: ").strip()) not in ("", "quit"):
        history.append({"role": "user", "content": text})
        messages = history if remember else [history[-1]]
        r = client.messages.create(model=MODEL, max_tokens=2000, messages=messages)
        answer = "".join(b.text for b in r.content if b.type == "text")
        # TODO: add the model's answer to history as {"role": "assistant", "content": answer}
        print("Claude:", answer)


if __name__ == "__main__":
    chat(remember=True)     # tell it your name on turn 1, ask for it on turn 3
