"""Exercise S.1 (solution): warm-up queries, each checked a second way."""
import sqlite3

def con():
    return sqlite3.connect("file:shop.db?mode=ro", uri=True)

def berlin_customers():
    return con().execute("SELECT name FROM customers WHERE city = 'Berlin' ORDER BY name").fetchall()

def cheapest_products(n=3):
    return con().execute("SELECT name, price FROM products ORDER BY price ASC LIMIT ?", (n,)).fetchall()

def pending_orders():
    return con().execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'").fetchone()[0]

def main():
    c = con()
    berlin = berlin_customers()
    check = sum(1 for (city,) in c.execute("SELECT city FROM customers") if city == "Berlin")
    print(f"(a) {len(berlin)} customers in Berlin (check: {check}): {berlin[:5]}")
    cheap = cheapest_products()
    check = sorted(c.execute("SELECT name, price FROM products").fetchall(), key=lambda r: r[1])[:3]
    print(f"(b) cheapest: {cheap}  (check: {check == cheap})")
    pending = pending_orders()
    check = sum(1 for (s,) in c.execute("SELECT status FROM orders") if s == "pending")
    print(f"(c) pending orders: {pending} (check: {check})")

if __name__ == "__main__":
    main()
