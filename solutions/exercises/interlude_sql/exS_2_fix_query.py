"""Exercise S.2 (solution): the broken revenue query, and the fix.

Bug 1: `JOIN orders o ON o.id = c.id` joins an order to the customer with the SAME
       NUMBER as the order, not its owner. It must be `o.customer_id = c.id`.
Bug 2: `SUM(p.price)` ignores quantity. Revenue is `SUM(oi.quantity * p.price)`.
Bug 3: `GROUP BY c.name` merges different customers who share a name. Group by
       c.id (and show the name). (Also consider excluding cancelled orders.)"""
import sqlite3

BROKEN = """SELECT c.name, SUM(p.price) FROM customers c JOIN orders o ON o.id = c.id
JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id
GROUP BY c.name"""

FIXED = """SELECT c.id, c.name, ROUND(SUM(oi.quantity * p.price), 2) AS revenue
FROM customers c
JOIN orders o       ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p     ON p.id = oi.product_id
WHERE o.status != 'cancelled'
GROUP BY c.id, c.name
ORDER BY revenue DESC"""

def main():
    con = sqlite3.connect("file:shop.db?mode=ro", uri=True)
    print("broken:", con.execute(BROKEN).fetchall()[:3])
    print("fixed: ", con.execute(FIXED).fetchall()[:3])

if __name__ == "__main__":
    main()
