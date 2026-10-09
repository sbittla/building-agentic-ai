"""Also write, in two sentences, why an embedding search might confuse ERR-4471 with
ERR-4417 while your pattern can't. (Put it here as a comment.)"""
import re


def error_codes(text: str) -> list[str]:
    """Every error code like "ERR-4471" (exactly four digits). Not "ERR-44",
    not "XERR-4471", not "ERR-44710"."""
    # TODO: \\b marks a word boundary
    raise NotImplementedError


if __name__ == "__main__":
    for t in ["Payment failed with ERR-4471", "ERR-44", "XERR-4471", "ERR-4471 and ERR-4417"]:
        print(t, "->", error_codes(t))
