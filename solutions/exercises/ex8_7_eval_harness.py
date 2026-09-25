"""Exercise 8.7 (Complex): compare the agent's answers with verified gold SQL."""
import re
import sqlite3
import ch08_sql_tools as sql
from ch04_agent import run_agent

REV = ("SUM(oi.quantity * p.price)", "FROM orders o JOIN order_items oi ON oi.order_id = o.id "
       "JOIN products p ON p.id = oi.product_id")
GOLD = [
    ("How many orders are there?", "SELECT COUNT(*) FROM orders"),
    ("How many customers are there?", "SELECT COUNT(*) FROM customers"),
    ("How many orders were cancelled?", "SELECT COUNT(*) FROM orders WHERE status = 'cancelled'"),
    ("How many orders are pending?", "SELECT COUNT(*) FROM orders WHERE status = 'pending'"),
    ("What is total revenue?", f"SELECT ROUND({REV[0]}, 2) {REV[1]} WHERE o.status != 'cancelled'"),
    ("Which customer has the highest revenue?",
     f"SELECT c.name FROM customers c JOIN orders o ON o.customer_id = c.id JOIN order_items oi "
     f"ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id WHERE o.status != 'cancelled' "
     f"GROUP BY c.id ORDER BY {REV[0]} DESC LIMIT 1"),
    ("Which product category earns the most revenue?",
     f"SELECT p.category {REV[1]} WHERE o.status != 'cancelled' GROUP BY p.category "
     f"ORDER BY {REV[0]} DESC LIMIT 1"),
    ("Which city has the most customers?",
     "SELECT city FROM customers GROUP BY city ORDER BY COUNT(*) DESC LIMIT 1"),
    ("What is the most expensive product?", "SELECT name FROM products ORDER BY price DESC LIMIT 1"),
    ("How many products are in the furniture category?",
     "SELECT COUNT(*) FROM products WHERE category = 'furniture'"),
    ("How many laptops were sold in non-cancelled orders?",
     "SELECT SUM(oi.quantity) FROM order_items oi JOIN orders o ON o.id = oi.order_id JOIN "
     "products p ON p.id = oi.product_id WHERE p.name = 'Laptop' AND o.status != 'cancelled'"),
    ("How many distinct customers placed at least one order?",
     "SELECT COUNT(DISTINCT customer_id) FROM orders"),
    ("What was revenue in 2025?",
     f"SELECT ROUND({REV[0]}, 2) {REV[1]} WHERE o.status != 'cancelled' AND o.order_date LIKE '2025%'"),
    ("How many customers joined in 2024?", "SELECT COUNT(*) FROM customers WHERE joined LIKE '2024%'"),
    ("What is the average number of items per order?",
     "SELECT ROUND(AVG(n), 2) FROM (SELECT SUM(quantity) n FROM order_items GROUP BY order_id)"),
]

def rows(query):
    with sqlite3.connect(f"file:{sql.DB_PATH}?mode=ro", uri=True) as con:
        return con.execute(query).fetchall()

def normalize(result):
    """Compare values only: ignore column names and row order; round floats."""
    return sorted(tuple(round(v, 2) if isinstance(v, float) else v for v in r) for r in result)

def final_sql(answer: str):
    blocks = re.findall(r"```(?:sql)?\s*(.+?)```", answer, re.S | re.I)
    return blocks[-1].strip() if blocks else None

def evaluate(system=sql.SYSTEM + " End your answer with the final SQL in a ```sql block."):
    results = []
    for question, gold in GOLD:
        answer, _, _ = run_agent(question, sql.TOOLS, sql.run_tool, system=system, verbose=False)
        q = final_sql(answer)
        if q is None:
            results.append((question, False, "no SQL in answer"))
            continue
        try:
            ok = normalize(rows(q)) == normalize(rows(gold))
            results.append((question, ok, "" if ok else "different result"))
        except sqlite3.Error as e:
            results.append((question, False, f"SQL error: {e}"))
    score = sum(r[1] for r in results) / len(results)
    print(f"accuracy: {score:.0%}")
    for q, ok, why in results:
        if not ok:
            print(f"  FAIL {q}: {why}")
    return score, results

if __name__ == "__main__":
    before, _ = evaluate()
    after, _ = evaluate(sql.SYSTEM + " A 'customer who placed an order' means a row in orders. "
                        "Use the exact product and status names from the data. End your answer "
                        "with the final SQL in a ```sql block.")
    print(f"before {before:.0%} -> after {after:.0%}")
