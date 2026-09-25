"""Interlude (testing): tests for i_pricing.py.   Run:  ./course.sh pytest -q test_i_pricing.py"""
import pytest
from i_pricing import apply_discount, parse_price, save_receipt

def test_ten_percent_off():                       # 1. a plain test: arrange, act, assert
    assert apply_discount(200, 10) == 180

@pytest.mark.parametrize("text, expected", [       # 2. one test, many examples
    ("$10", 10.0), ("1,299.50", 1299.5), (" $0.99 ", 0.99)])
def test_parse_price(text, expected):
    assert parse_price(text) == expected

def test_rejects_bad_percent():                    # 3. testing that errors happen
    with pytest.raises(ValueError, match="between 0 and 100"):
        apply_discount(100, 150)

def test_save_receipt(tmp_path):                   # 4. a fixture: a fresh temp folder
    path = tmp_path / "receipt.txt"
    assert save_receipt(path, ["Laptop 1200", "Mouse 25"]) == 2
    assert path.read_text().splitlines() == ["Laptop 1200", "Mouse 25"]

def test_replace_a_function(monkeypatch):         # 5. monkeypatch: swap in a stand-in
    import i_pricing                               #    (undone automatically after the test)
    monkeypatch.setattr(i_pricing, "parse_price", lambda text: 42.0)
    assert i_pricing.parse_price("anything") == 42.0
    # The same trick replaces httpx.get with a fake that returns a canned response,
    # so a test of code that calls a web API needs no internet: exercise T.4.
