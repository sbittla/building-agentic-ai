"""Exercise R.2 (solution): hide anything that looks like an API key."""
import re

KEY = re.compile(r"\bsk-[A-Za-z0-9-]{10,}")

def mask(text: str) -> str:
    return KEY.sub("sk-***", text)

def main():
    for t in ["my key is sk-ant-api03-AbC123xyz789 ok?",
              "two keys: sk-1234567890 and sk-abcdefghijKLM",
              "sk- on its own stays", "sk-short stays too", "task-1234567890 is not a key"]:
        print(f"{t!r:50} -> {mask(t)!r}")

if __name__ == "__main__":
    main()
