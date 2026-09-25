"""Exercise T.3 (solution): tests for exercise 0.4, edge cases included."""
import pytest
from ex0_4_basics import invoice_total, most_common_word, word_count

@pytest.mark.parametrize("text, n", [("the cat sat", 3), ("", 0), ("  a   b  ", 2),
                                     ("line one\nline two", 4)])
def test_word_count(text, n):
    assert word_count(text) == n

def test_most_common_word_ignores_case():
    assert most_common_word("The cat and the hat") == "the"

def test_most_common_word_ignores_punctuation():
    assert most_common_word("Go, go, GO!") == "go"

def test_most_common_word_tie_goes_to_first():
    # This test caught a real bug in a first draft that used max(set(words), key=...):
    # sets have no order, so ties gave a different answer on different runs.
    assert most_common_word("one two") == "one"

def test_most_common_word_empty():
    assert most_common_word("") is None and most_common_word("  ... ") is None

def test_invoice_total():
    assert invoice_total([{"price": 10, "qty": 3}, {"price": 2.5, "qty": 2}]) == 35.0

def test_invoice_total_floats_are_rounded():
    assert invoice_total([{"price": 0.1, "qty": 3}]) == 0.3     # not 0.30000000000000004

def test_invoice_total_empty():
    assert invoice_total([]) == 0
