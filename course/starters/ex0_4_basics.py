def word_count(text: str) -> int:
    """Number of words. word_count("the cat sat") == 3, word_count("") == 0"""
    # TODO: text.split() gives you the words
    raise NotImplementedError


def most_common_word(text: str) -> str | None:
    """The most frequent word, ignoring case and punctuation around words.
    most_common_word("The cat and the hat") == "the". Return None for empty text.
    If two words tie, return the one that appears first."""
    # TODO: lower-case, split, count with a dictionary (or collections.Counter)
    raise NotImplementedError


def invoice_total(items: list[dict]) -> float:
    """Total of price * qty, rounded to cents.
    invoice_total([{"price": 10, "qty": 3}]) == 30"""
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    print(word_count("the cat sat"))                   # 3
    print(most_common_word("The cat and the hat"))     # the
    print(invoice_total([{"price": 0.1, "qty": 3}]))   # 0.3
