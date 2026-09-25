def test_example(ex):
    s = ex.summarize_forecast(ex.EXAMPLE)
    assert isinstance(s, dict), "a valid forecast should give a dictionary"
    assert s["hottest_day"] == "2026-10-03" and s["hottest_c"] == 33
    assert s["average_max_c"] == 31.0, "average of 31, 29, 33 is 31.0"
    assert s["rainy_days"] == ["2026-10-01", "2026-10-02"], "rain above 0.5 only"

def test_errors(ex):
    assert str(ex.summarize_forecast("not json")).startswith("ERROR"), "invalid JSON -> an ERROR string"
    assert str(ex.summarize_forecast('{"city": "Oslo"}')).startswith("ERROR"), "no days -> an ERROR string"
