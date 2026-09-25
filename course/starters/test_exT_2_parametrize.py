"""Exercise T.2: one parametrized test, many cases. Run: ./course.sh ex T.2"""
import pytest
from i_pricing import apply_discount


@pytest.mark.parametrize("amount, percent, expected", [
    (200, 10, 180.0),
    # TODO: add at least four more cases: 0%, 100%, a fractional percent, ...
])
def test_apply_discount(amount, percent, expected):
    assert apply_discount(amount, percent) == expected
