"""Capstone 1 data: 50 orders for 20 customers + 20 help-center articles."""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB = Path("support.db")
ARTICLES = Path("helpcenter")
TODAY = date(2026, 9, 23)          # fixed "today" so the return window is testable

ARTICLE_TEXT = {
    "return-policy.md": "# Return policy\nItems can be returned within 30 days of delivery for a full refund. "
                        "Refunds over $200 are reviewed by a human before they are issued. "
                        "Opened software and gift cards cannot be returned.",
    "shipping-times.md": "# Shipping times\nStandard shipping takes 3-5 business days. Express takes 1-2. "
                         "Orders placed after 2 pm ship the next business day.",
    "track-order.md": "# Tracking an order\nUse the tracking number in your confirmation email. "
                      "Tracking updates can take 24 hours to appear.",
    "change-address.md": "# Changing the delivery address\nAddresses can be changed until the order ships. "
                         "After shipping, contact the carrier.",
    "damaged-item.md": "# Damaged items\nIf an item arrives damaged, request a return within 30 days; "
                       "we cover return shipping.",
    "payment-methods.md": "# Payment methods\nWe accept cards, UPI and PayPal. We never ask for your card "
                          "number by chat or email.",
    "warranty.md": "# Warranty\nElectronics carry a 1-year limited warranty from the delivery date.",
    "cancel-order.md": "# Cancelling an order\nOrders can be cancelled until they ship.",
    "gift-cards.md": "# Gift cards\nGift cards never expire and cannot be refunded.",
    "contact-human.md": "# Talking to a person\nOur team answers within 4 business hours, 9 am-6 pm.",
}

def build():
    rnd = random.Random(11)
    ARTICLES.mkdir(exist_ok=True)
    for name, text in ARTICLE_TEXT.items():
        (ARTICLES / name).write_text(text + "\n")
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.executescript("""
    CREATE TABLE customers (email TEXT PRIMARY KEY, name TEXT);
    CREATE TABLE orders (order_id TEXT PRIMARY KEY, email TEXT, status TEXT, delivered DATE,
                         total REAL, items TEXT);
    CREATE TABLE returns (order_id TEXT, items TEXT, amount REAL, created DATE);
    """)
    names = ["Asha", "Ben", "Chen", "Divya", "Elena", "Farid", "Grace", "Hiro", "Ines", "Jon",
             "Kavya", "Liam", "Mei", "Nikhil", "Olga", "Priya", "Quinn", "Ravi", "Sara", "Tom"]
    for n in names:
        con.execute("INSERT INTO customers VALUES (?,?)", (f"{n.lower()}@example.com", n))
    catalog = [("Headphones", 150), ("Laptop stand", 45), ("Monitor", 280), ("Keyboard", 90),
               ("Laptop", 1200), ("Mouse", 25)]
    for i in range(1, 51):
        item, price = rnd.choice(catalog)
        status = rnd.choice(["delivered", "delivered", "delivered", "shipped", "processing"])
        delivered = (TODAY - timedelta(days=rnd.randint(1, 60))).isoformat() if status == "delivered" else None
        con.execute("INSERT INTO orders VALUES (?,?,?,?,?,?)",
                    (f"A{1000 + i}", f"{rnd.choice(names).lower()}@example.com", status, delivered,
                     price, item))
    # fixed orders the eval relies on
    con.execute("INSERT INTO orders VALUES ('A2001','asha@example.com','delivered',?,150,'Headphones')",
                ((TODAY - timedelta(days=10)).isoformat(),))
    con.execute("INSERT INTO orders VALUES ('A2002','asha@example.com','delivered',?,90,'Keyboard')",
                ((TODAY - timedelta(days=45)).isoformat(),))
    con.execute("INSERT INTO orders VALUES ('A2003','ben@example.com','delivered',?,1200,'Laptop')",
                ((TODAY - timedelta(days=5)).isoformat(),))
    con.commit()
    return DB

if __name__ == "__main__":
    print("built", build())
