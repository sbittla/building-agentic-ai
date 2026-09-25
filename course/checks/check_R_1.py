def test_logs(ex):
    assert ex.latencies(ex.LOG) == [800, 812], "latencies as integers"
    assert len(ex.timestamps(ex.LOG)) == 4 and ex.timestamps(ex.LOG)[0] == "2026-09-22 14:05:11"
    assert set(ex.services(ex.LOG)) == {"checkout-service", "search-service"}
    assert len(ex.services(ex.LOG)) == 4, "one service per line (watch the extra space after INFO)"
