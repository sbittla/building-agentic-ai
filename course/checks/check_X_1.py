def test_codes(ex):
    assert ex.error_codes("Payment failed with ERR-4471 at 14:05") == ["ERR-4471"]
    assert ex.error_codes("ERR-44 is too short") == []
    assert ex.error_codes("XERR-4471 has a prefix") == []
    assert ex.error_codes("ERR-44710 is too long") == []
    assert ex.error_codes("ERR-4471, then ERR-4417.") == ["ERR-4471", "ERR-4417"]
