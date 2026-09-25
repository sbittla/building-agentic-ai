def test_sorting(ex):
    assert [c["name"] for c in ex.top_n(ex.CUSTOMERS, 2, "revenue")] == ["Ben", "Dana"]
    assert ex.top_n(ex.CUSTOMERS, 10, "revenue")[-1]["name"] == "Chen"
    assert ex.cheapest(ex.PRODUCTS) == "Notebook"
    assert ex.CUSTOMERS[0]["name"] == "Asha", "don't change the original list (sorted, not .sort)"
