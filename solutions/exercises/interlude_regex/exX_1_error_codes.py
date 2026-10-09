"""Exercise X.1 (solution): match error codes exactly.

Why embeddings confuse ERR-4471 and ERR-4417: an embedding turns text into a
meaning-vector, and two codes made of the same characters "mean" almost the same
thing to it, so their vectors land close together. A regex compares characters
exactly, so ERR-4471 matches only ERR-4471."""
import re

CODE = re.compile(r"\bERR-\d{4}\b")

def error_codes(text: str) -> list[str]:
    return CODE.findall(text)

EXAMPLES = {
    "Payment failed with ERR-4471 at 14:05": ["ERR-4471"],
    "ERR-44 is too short": [],
    "XERR-4471 has a prefix": [],
    "ERR-44710 is too long": [],
    "Seen twice: ERR-4471, then ERR-4417.": ["ERR-4471", "ERR-4417"],
}

def main():
    for text, expected in EXAMPLES.items():
        got = error_codes(text)
        print(f"{'ok ' if got == expected else 'BAD'} {text!r:42} -> {got}")

if __name__ == "__main__":
    main()
