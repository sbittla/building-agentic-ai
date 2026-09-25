def test_all(ex):
    assert ex.shipped_ids(ex.ORDERS) == ["A1", "A3"]
    assert ex.totals_by_status(ex.ORDERS) == {"shipped": 165.5, "cancelled": 80.0, "pending": 10.0}
    assert ex.names_over(ex.PRODUCTS, 100) == ["Laptop", "Desk"]
    assert ex.names_over(ex.PRODUCTS, 1200) == [], "MORE than the price, not equal"
