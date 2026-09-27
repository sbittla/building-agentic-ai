"""Exercise P.1 (solution): comprehensions."""
ORDERS = [{"id": "A1", "status": "shipped", "total": 120.0},
          {"id": "A2", "status": "cancelled", "total": 80.0},
          {"id": "A3", "status": "shipped", "total": 45.5},
          {"id": "A4", "status": "pending", "total": 10.0}]
PRODUCTS = [{"name": "Laptop", "price": 1200}, {"name": "Pen set", "price": 12},
            {"name": "Desk", "price": 350}]

def shipped_ids(orders):
    return [o["id"] for o in orders if o["status"] == "shipped"]

def totals_by_status(orders):
    totals = {}
    for o in orders:
        totals[o["status"]] = totals.get(o["status"], 0) + o["total"]
    return totals

def names_over(products, min_price):
    return [p["name"] for p in products if p["price"] > min_price]

if __name__ == "__main__":
    print(shipped_ids(ORDERS), totals_by_status(ORDERS), names_over(PRODUCTS, 100))
