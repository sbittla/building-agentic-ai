import sqlite3


def con():
    return sqlite3.connect("file:shop.db?mode=ro", uri=True)


def orders_for_city(city: str) -> int:
    """How many orders came from customers in `city`. Pass the city as a ? PARAMETER."""
    # TODO: con().execute("SELECT COUNT(*) FROM ... WHERE c.city = ?", (city,)).fetchone()[0]
    raise NotImplementedError


def orders_for_city_unsafe(city: str) -> int:
    """The SAME query built with an f-string. Only to see what goes wrong!"""
    raise NotImplementedError


if __name__ == "__main__":
    evil = "Pune' OR '1'='1"
    print(orders_for_city("Pune"), orders_for_city(evil), orders_for_city_unsafe(evil))
