"""Exercise 0.4 (solution): three small functions."""
from collections import Counter

def word_count(text: str) -> int:
    return len(text.split())

def most_common_word(text: str) -> str | None:
    """The most frequent word, ignoring case and surrounding punctuation.
    Ties go to the word that appears first. Empty text gives None."""
    words = [w.strip(".,!?;:\"'()").lower() for w in text.split()]
    words = [w for w in words if w]
    if not words:
        return None
    counts = Counter(words)                 # Counter keeps first-seen order for ties
    return counts.most_common(1)[0][0]

def invoice_total(items: list[dict]) -> float:
    return round(sum(item["price"] * item["qty"] for item in items), 2)

def main():
    for text in ["the cat sat", "", "  lots   of   spaces  "]:
        print(f"word_count({text!r}) = {word_count(text)}")
    for text in ["The cat and the hat", "Go, go, GO!", "one two"]:
        print(f"most_common_word({text!r}) = {most_common_word(text)!r}")
    for items in [[{"price": 10, "qty": 3}], [{"price": 0.1, "qty": 3}, {"price": 5, "qty": 1}], []]:
        print(f"invoice_total({items}) = {invoice_total(items)}")

if __name__ == "__main__":
    main()
