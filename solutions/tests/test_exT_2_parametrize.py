"""Exercise T.2 (solution): one parametrized test, many cases. Run with pytest -v."""
import pytest
from i_pricing import apply_discount

@pytest.mark.parametrize("amount, percent, expected", [
    (200, 10, 180.0),
    (200, 0, 200.0),          # 0%: unchanged
    (200, 100, 0.0),          # 100%: free
    (99.99, 12.5, 87.49),     # fractional percent, rounded to cents
    (0, 50, 0.0),             # nothing to discount
    (1234.56, 33.3, 823.45),
])
def test_apply_discount(amount, percent, expected):
    assert apply_discount(amount, percent) == expected

@pytest.mark.parametrize("percent", [-1, 100.01, 150])
def test_apply_discount_rejects(percent):
    with pytest.raises(ValueError):
        apply_discount(100, percent)
