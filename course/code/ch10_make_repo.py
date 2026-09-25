"""Chapter 10: create a tiny project with bugs for the agent to fix."""
from pathlib import Path

repo = Path("buggy_repo")
repo.mkdir(exist_ok=True)
(repo / "pricing.py").write_text('''\
def subtotal(items):
    """items: list of (price, quantity)."""
    return sum(price for price, qty in items)          # BUG: ignores quantity

def apply_discount(amount, percent):
    """Reduce amount by percent (0-100)."""
    return amount - amount * percent                    # BUG: percent not divided by 100

def total(items, percent=0, tax_rate=0.08):
    return round(apply_discount(subtotal(items), percent) * (1 + tax_rate), 2)
''')
(repo / "test_pricing.py").write_text('''\
from pricing import subtotal, apply_discount, total

def test_subtotal_uses_quantity():
    assert subtotal([(10.0, 2), (5.0, 1)]) == 25.0

def test_discount_is_percent():
    assert apply_discount(200, 10) == 180

def test_total():
    assert total([(100.0, 1)], percent=10) == 97.2
''')
print("buggy_repo created: run `pytest buggy_repo` to see 3 failures")
