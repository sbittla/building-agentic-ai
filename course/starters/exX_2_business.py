import sqlite3

# (a) revenue per month in 2025 (month as 'YYYY-MM', revenue), excluding cancelled orders
REVENUE_PER_MONTH = """SELECT ... """

# (b) customers (id, name) who have never cancelled an order
NEVER_CANCELLED = """SELECT ... """

# (c) the product (name, times) most often in the same order as a Laptop
BOUGHT_WITH_LAPTOP = """SELECT ... """


def run(sql):
    return sqlite3.connect("file:shop.db?mode=ro", uri=True).execute(sql).fetchall()


if __name__ == "__main__":
    print(run(REVENUE_PER_MONTH)); print(len(run(NEVER_CANCELLED))); print(run(BOUGHT_WITH_LAPTOP))
