import sqlite3
con = lambda: sqlite3.connect("file:shop.db?mode=ro", uri=True)

def test_berlin(ex):
    want = con().execute("SELECT COUNT(*) FROM customers WHERE city='Berlin'").fetchone()[0]
    assert len(ex.berlin_customers()) == want

def test_cheapest(ex):
    want = con().execute("SELECT name, price FROM products ORDER BY price LIMIT 3").fetchall()
    assert [tuple(r) for r in ex.cheapest_products()] == want

def test_pending(ex):
    assert ex.pending_orders() == con().execute("SELECT COUNT(*) FROM orders WHERE status='pending'").fetchone()[0]
