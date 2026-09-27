"""Exercise S.3 (solution): three business questions in SQL."""
import sqlite3

REVENUE_PER_MONTH = """
SELECT strftime('%Y-%m', o.order_date) AS month,
       ROUND(SUM(oi.quantity * p.price), 2) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p     ON p.id = oi.product_id
WHERE o.status != 'cancelled' AND o.order_date LIKE '2025-%'
GROUP BY month ORDER BY month"""

NEVER_CANCELLED = """
SELECT c.id, c.name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o
                  WHERE o.customer_id = c.id AND o.status = 'cancelled')
ORDER BY c.id"""

BOUGHT_WITH_LAPTOP = """
SELECT p2.name, COUNT(*) AS times
FROM order_items a
JOIN products p1    ON p1.id = a.product_id AND p1.name = 'Laptop'
JOIN order_items b  ON b.order_id = a.order_id AND b.product_id != a.product_id
JOIN products p2    ON p2.id = b.product_id
GROUP BY p2.name ORDER BY times DESC LIMIT 1"""

def run(sql):
    return sqlite3.connect("file:shop.db?mode=ro", uri=True).execute(sql).fetchall()

def main():
    print("(a) revenue per month, 2025:", run(REVENUE_PER_MONTH))
    print("(b) customers who never cancelled:", len(run(NEVER_CANCELLED)))
    print("(c) most often bought with a Laptop:", run(BOUGHT_WITH_LAPTOP))

if __name__ == "__main__":
    main()
