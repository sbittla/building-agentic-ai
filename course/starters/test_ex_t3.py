"""Exercise T.3: tests for your exercise 0.4 functions. Run: ./course.sh ex T.3"""
from ex0_4_basics import invoice_total, most_common_word, word_count   # from workspace/exercises


def test_word_count():
    assert word_count("the cat sat") == 3

# TODO: at least nine tests in total, including an edge case for each function:
# empty text, a tie for the most common word, an empty invoice, float rounding...
