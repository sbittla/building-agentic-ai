def test_word_count(ex):
    assert ex.word_count("the cat sat") == 3, "word_count('the cat sat') should be 3"
    assert ex.word_count("") == 0, "empty text has 0 words"
    assert ex.word_count("  lots   of   spaces  ") == 3, "extra spaces don't make extra words"

def test_most_common_word(ex):
    assert ex.most_common_word("The cat and the hat") == "the", "ignore upper/lower case"
    assert ex.most_common_word("Go, go, GO!") == "go", "ignore punctuation around words"
    assert ex.most_common_word("one two") == "one", "on a tie, return the word that appears first"
    assert ex.most_common_word("") is None, "empty text should give None"

def test_invoice_total(ex):
    assert ex.invoice_total([{"price": 10, "qty": 3}]) == 30
    assert ex.invoice_total([{"price": 0.1, "qty": 3}]) == 0.3, "round to cents (0.1*3 is 0.30000000000000004)"
    assert ex.invoice_total([]) == 0, "an empty invoice totals 0"
