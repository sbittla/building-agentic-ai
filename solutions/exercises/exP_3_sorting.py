"""Exercise P.3 (solution): sort and pick."""
CUSTOMERS = [{"name": "Asha", "revenue": 1200}, {"name": "Ben", "revenue": 5400},
             {"name": "Chen", "revenue": 300}, {"name": "Dana", "revenue": 2500}]
PRODUCTS = [{"name": "Laptop", "price": 1200}, {"name": "Pen set", "price": 12},
            {"name": "Notebook", "price": 5}]

def top_n(items, n, field):
    return sorted(items, key=lambda x: x[field], reverse=True)[:n]

def cheapest(products):
    return min(products, key=lambda p: p["price"])["name"]

if __name__ == "__main__":
    print([c["name"] for c in top_n(CUSTOMERS, 2, "revenue")], cheapest(PRODUCTS))
