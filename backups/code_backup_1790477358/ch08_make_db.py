"""Chapter 8: create a small sample shop database (shop.db)."""
import random
import sqlite3
from datetime import date, timedelta

random.seed(7)
con = sqlite3.connect("shop.db")
con.executescript("""
DROP TABLE IF EXISTS order_items; DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;    DROP TABLE IF EXISTS customers;
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT, joined DATE);
CREATE TABLE products  (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
CREATE TABLE orders    (id INTEGER PRIMARY KEY,
                        customer_id INTEGER REFERENCES customers(id),
                        order_date DATE, status TEXT);
CREATE TABLE order_items (order_id INTEGER REFERENCES orders(id),
                          product_id INTEGER REFERENCES products(id), quantity INTEGER);
""")
cities = ["Pune", "Seattle", "Austin", "Hyderabad", "Berlin"]
con.executemany("INSERT INTO customers VALUES (?,?,?,?)",
    [(i, f"Customer {i}", random.choice(cities),
      (date(2024, 1, 1) + timedelta(days=random.randint(0, 600))).isoformat())
     for i in range(1, 51)])
products = [("Laptop", "electronics", 1200), ("Headphones", "electronics", 150),
            ("Desk", "furniture", 300), ("Chair", "furniture", 180),
            ("Notebook", "stationery", 5), ("Pen set", "stationery", 12),
            ("Monitor", "electronics", 280), ("Lamp", "furniture", 45)]
con.executemany("INSERT INTO products VALUES (?,?,?,?)",
                [(i, *p) for i, p in enumerate(products, 1)])
for oid in range(1, 401):
    con.execute("INSERT INTO orders VALUES (?,?,?,?)", (
        oid, random.randint(1, 50),
        (date(2025, 1, 1) + timedelta(days=random.randint(0, 600))).isoformat(),
        random.choice(["shipped", "shipped", "shipped", "cancelled", "pending"])))
    for pid in random.sample(range(1, 9), random.randint(1, 3)):
        con.execute("INSERT INTO order_items VALUES (?,?,?)",
                    (oid, pid, random.randint(1, 4)))
con.commit()
print("shop.db created")
