import sqlite3
con = lambda: sqlite3.connect("file:shop.db?mode=ro", uri=True)
TRUTH = ("SELECT c.id, SUM(oi.quantity * p.price) FROM customers c JOIN orders o ON o.customer_id = c.id "
         "JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id "
         "WHERE o.status != 'cancelled' GROUP BY c.id")

def test_fixed_query(ex):
    rows = con().execute(ex.FIXED).fetchall()
    truth = dict(con().execute(TRUTH).fetchall())
    assert len(rows) == len(truth), "one row per customer (group by id, not name)"
    total = sum(r[-1] for r in rows)
    assert abs(total - sum(truth.values())) < 1, ("revenue should be quantity x price over "
                                                  "non-cancelled orders, joined on o.customer_id")
