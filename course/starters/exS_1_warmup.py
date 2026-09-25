import sqlite3


def con():
    return sqlite3.connect("file:shop.db?mode=ro", uri=True)


def berlin_customers() -> list[tuple]:
    """Names of customers in Berlin, as rows: [("Customer 12",), ...]"""
    return con().execute("SELECT ... ").fetchall()        # TODO: finish the query


def cheapest_products(n: int = 3) -> list[tuple]:
    """(name, price) of the n cheapest products, cheapest first."""
    raise NotImplementedError


def pending_orders() -> int:
    """How many orders have status 'pending'."""
    raise NotImplementedError


if __name__ == "__main__":
    print(len(berlin_customers()), cheapest_products(), pending_orders())
