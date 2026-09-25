CUSTOMERS = [{"name": "Asha", "revenue": 1200}, {"name": "Ben", "revenue": 5400},
             {"name": "Chen", "revenue": 300}, {"name": "Dana", "revenue": 2500}]
PRODUCTS = [{"name": "Laptop", "price": 1200}, {"name": "Pen set", "price": 12},
            {"name": "Notebook", "price": 5}]


def top_n(items: list[dict], n: int, field: str) -> list[dict]:
    """The n items with the largest `field`, largest first."""
    raise NotImplementedError


def cheapest(products: list[dict]) -> str:
    """The name of the cheapest product."""
    raise NotImplementedError


if __name__ == "__main__":
    print([c["name"] for c in top_n(CUSTOMERS, 2, "revenue")], cheapest(PRODUCTS))
