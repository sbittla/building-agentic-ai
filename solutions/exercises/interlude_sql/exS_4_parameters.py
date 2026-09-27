"""Exercise S.4 (solution): parameters versus string-built SQL."""
import sqlite3

def con():
    return sqlite3.connect("file:shop.db?mode=ro", uri=True)

def orders_for_city(city: str) -> int:
    """Safe: the city is passed as DATA, never as part of the SQL text."""
    return con().execute("SELECT COUNT(*) FROM orders o JOIN customers c "
                         "ON c.id = o.customer_id WHERE c.city = ?", (city,)).fetchone()[0]

def orders_for_city_unsafe(city: str) -> int:
    """UNSAFE: the input becomes part of the SQL. Never do this."""
    sql = ("SELECT COUNT(*) FROM orders o JOIN customers c ON c.id = o.customer_id "
           f"WHERE c.city = '{city}'")
    return con().execute(sql).fetchone()[0]

def main():
    evil = "Pune' OR '1'='1"
    print("Pune (safe):            ", orders_for_city("Pune"))
    print("malicious (safe):       ", orders_for_city(evil))          # 0: no such city
    print("malicious (f-string):   ", orders_for_city_unsafe(evil))   # every order!
    total = con().execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print("all orders:             ", total)
    print("The f-string version ran  WHERE c.city = 'Pune' OR '1'='1' , which is true "
          "for every row.")

if __name__ == "__main__":
    main()
