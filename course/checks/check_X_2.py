import sqlite3
run = lambda sql: sqlite3.connect("file:shop.db?mode=ro", uri=True).execute(sql).fetchall()
REV = ("SELECT strftime('%Y-%m', o.order_date), ROUND(SUM(oi.quantity * p.price), 2) FROM orders o "
       "JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id "
       "WHERE o.status != 'cancelled' AND o.order_date LIKE '2025-%' GROUP BY 1 ORDER BY 1")

def test_revenue_per_month(ex):
    got = [(m, round(v, 2)) for m, v in run(ex.REVENUE_PER_MONTH)]
    assert got == run(REV), "months in 2025, excluding cancelled orders, quantity x price"

def test_never_cancelled(ex):
    want = run("SELECT COUNT(*) FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o "
               "WHERE o.customer_id = c.id AND o.status = 'cancelled')")[0][0]
    assert len(run(ex.NEVER_CANCELLED)) == want

WITH_LAPTOP = ("SELECT p2.name FROM order_items a JOIN products p1 ON p1.id = a.product_id AND p1.name = 'Laptop' "
               "JOIN order_items b ON b.order_id = a.order_id AND b.product_id != a.product_id "
               "JOIN products p2 ON p2.id = b.product_id GROUP BY p2.name ORDER BY COUNT(*) DESC LIMIT 1")

def test_bought_with_laptop(ex):
    got = run(ex.BOUGHT_WITH_LAPTOP)
    assert got and got[0][0] == run(WITH_LAPTOP)[0][0], "join order_items to itself on order_id"
