ORDERS = [{"id": "A1", "status": "shipped", "total": 120.0},
          {"id": "A2", "status": "cancelled", "total": 80.0},
          {"id": "A3", "status": "shipped", "total": 45.5},
          {"id": "A4", "status": "pending", "total": 10.0}]
PRODUCTS = [{"name": "Laptop", "price": 1200}, {"name": "Pen set", "price": 12},
            {"name": "Desk", "price": 350}]


def shipped_ids(orders) -> list[str]:
    """["A1", "A3"] for ORDERS."""
    raise NotImplementedError


def totals_by_status(orders) -> dict:
    """{"shipped": 165.5, "cancelled": 80.0, "pending": 10.0} for ORDERS."""
    raise NotImplementedError


def names_over(products, min_price) -> list[str]:
    """Names of products that cost MORE than min_price, in the original order."""
    raise NotImplementedError


if __name__ == "__main__":
    print(shipped_ids(ORDERS), totals_by_status(ORDERS), names_over(PRODUCTS, 100))
