"""Interlude (SQL): querying shop.db from Python. Each query builds on the last."""
import sqlite3

con = sqlite3.connect("file:shop.db?mode=ro", uri=True)   # read-only, as in chapter 8

def show(title, sql, params=()):
    rows = con.execute(sql, params).fetchall()
    print(f"\n-- {title}\n{sql}\n{rows[:5]}{' ...' if len(rows) > 5 else ''}")

show("1. pick columns and rows", "SELECT name, price FROM products WHERE price > 100")
show("2. sort and limit", "SELECT name, price FROM products ORDER BY price DESC LIMIT 3")
show("3. count and sum", "SELECT COUNT(*), SUM(price) FROM products")
show("4. group", "SELECT status, COUNT(*) FROM orders GROUP BY status")
show("5. join two tables",
     "SELECT o.id, c.name, o.status FROM orders o JOIN customers c ON c.id = o.customer_id LIMIT 5")
show("6. join + group: revenue per category",
     "SELECT p.category, ROUND(SUM(oi.quantity * p.price), 2) AS revenue "
     "FROM order_items oi JOIN products p ON p.id = oi.product_id "
     "JOIN orders o ON o.id = oi.order_id WHERE o.status != 'cancelled' "
     "GROUP BY p.category ORDER BY revenue DESC")
show("7. parameters (never paste user text into SQL!)",
     "SELECT name, city FROM customers WHERE city = ?", ("Pune",))
show("8. a CTE: name a step, then use it",
     "WITH per_customer AS (SELECT customer_id, COUNT(*) AS n FROM orders GROUP BY customer_id) "
     "SELECT COUNT(*) FROM per_customer WHERE n >= 10")
