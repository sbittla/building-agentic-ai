"""The query below is meant to give revenue per customer but has three bugs.
Write the corrected query in FIXED, and name the bugs in a comment."""
import sqlite3

BROKEN = """SELECT c.name, SUM(p.price) FROM customers c JOIN orders o ON o.id = c.id
JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id
GROUP BY c.name"""

# Bugs:
# 1.
# 2.
# 3.
FIXED = """
SELECT ...   -- TODO: return customer id, name and revenue (excluding cancelled orders)
"""


if __name__ == "__main__":
    con = sqlite3.connect("file:shop.db?mode=ro", uri=True)
    print(con.execute(FIXED).fetchall()[:3])
