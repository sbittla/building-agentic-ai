"""Exercise 10.5 (Medium): add shipping.py with two more bugs (5 failing tests in total)."""
from pathlib import Path

repo = Path("buggy_repo")
(repo / "shipping.py").write_text('''\
def shipping_cost(weight_kg, express=False):
    """Base 5.00 + 1.50 per kg; express doubles the total. Free over 20 kg? No: capped at 40."""
    cost = 5.0 + 1.5 * weight_kg
    if express:
        cost = cost + 2                   # BUG: should double
    return min(cost, 30.0)                # BUG: cap is 40

def delivery_days(express=False):
    return 1 if express else 5
''')
(repo / "test_shipping.py").write_text('''\
from shipping import shipping_cost, delivery_days

def test_standard():
    assert shipping_cost(2) == 8.0

def test_express_doubles():
    assert shipping_cost(2, express=True) == 16.0

def test_cap_is_40():
    assert shipping_cost(100) == 40.0

def test_days():
    assert delivery_days(True) == 1 and delivery_days() == 5
''')
print("added shipping.py: run `pytest buggy_repo` to see 5 failures")
