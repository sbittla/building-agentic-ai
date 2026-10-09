import sqlite3

def test_parameters(ex):
    want = sqlite3.connect("file:shop.db?mode=ro", uri=True).execute(
        "SELECT COUNT(*) FROM orders o JOIN customers c ON c.id = o.customer_id WHERE c.city='Pune'").fetchone()[0]
    assert ex.orders_for_city("Pune") == want
    assert ex.orders_for_city("Pune' OR '1'='1") == 0, "with a ? parameter, the attack is just a strange city name"

def test_you_saw_the_attack(ex):
    total = sqlite3.connect("file:shop.db?mode=ro", uri=True).execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    assert ex.orders_for_city_unsafe("Pune' OR '1'='1") == total, "the f-string version should count EVERY order"
