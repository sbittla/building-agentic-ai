"""Chapter 0 and the four interludes (regex, SQL, async): reference solutions, offline."""
import asyncio
import json
import httpx
import pytest

# ---------------- chapter 0
def test_0_4_basics():
    from ex0_4_basics import invoice_total, most_common_word, word_count
    assert word_count("a b  c") == 3 and word_count("") == 0
    assert most_common_word("B a b A a") == "a"
    assert invoice_total([{"price": 1.5, "qty": 2}, {"price": 3, "qty": 1}]) == 6.0

def test_0_5_forecast():
    from ex0_5_forecast import EXAMPLE, summarize_forecast
    s = summarize_forecast(EXAMPLE)
    assert s["hottest_day"] == "2026-10-03" and s["average_max_c"] == 31.0
    assert s["rainy_days"] == ["2026-10-01", "2026-10-02"]
    assert summarize_forecast("not json").startswith("ERROR: not valid JSON")

class _R:
    def __init__(self, code, data=None):
        self.status_code, self._d, self.text = code, data, ""
    def json(self):
        return self._d

def test_0_6_city_temperature(monkeypatch):
    import ex0_6_city_temperature as ex
    def fake_get(url, params=None, timeout=None):
        if "nope" in url:
            return _R(404)
        if "geocoding" in url:
            if params["name"] == "Xyzzyqq":
                return _R(200, {"generationtime_ms": 0.1})       # no "results" key
            return _R(200, {"results": [{"name": params["name"], "country": "India",
                                         "latitude": 18.5, "longitude": 73.9}]})
        return _R(200, {"daily": {"temperature_2m_max": [30.1]}})
    monkeypatch.setattr(ex.httpx, "get", fake_get)
    assert ex.city_temperature("Pune") == "Pune, India: max 30.1 C today"
    assert "no city called" in ex.city_temperature("Xyzzyqq")
    assert "HTTP 404" in ex.city_temperature("Pune", geocode_url="https://x/nope")
    def offline(*a, **k):
        raise httpx.ConnectError("offline")
    monkeypatch.setattr(ex.httpx, "get", offline)
    assert ex.city_temperature("Pune").startswith("ERROR: could not reach")

def test_0_7_expenses(ws):
    import ex0_7_expenses as ex
    ex.make_sample("exp.csv", rows=30)
    r = ex.report("exp.csv", "exp.json")
    assert r["skipped_rows"] == 3
    assert round(sum(r["per_category"].values()), 2) == r["total"]
    assert round(sum(r["per_month"].values()), 2) == r["total"]
    assert json.loads((ws / "exp.json").read_text()) == r

# ---------------- regex
def test_r1_logs():
    import exR_1_logs as ex
    assert ex.latencies(ex.LOG) == [800, 812]
    assert len(ex.timestamps(ex.LOG)) == 4
    assert set(ex.services(ex.LOG)) == {"checkout-service", "search-service"}

def test_r2_mask():
    from exR_2_mask import mask
    assert mask("key sk-ant-api03-XYZ1234567 end") == "key sk-*** end"
    assert mask("sk- alone") == "sk- alone" and mask("task-1234567890") == "task-1234567890"

def test_r3_citations():
    from exR_3_citations import citations
    assert citations("(a/b-c.d.md:12) (see page 12) (x.txt:3)") == [("a/b-c.d.md", 12), ("x.txt", 3)]

def test_r4_error_codes():
    import exR_4_error_codes as ex
    for text, expected in ex.EXAMPLES.items():
        assert ex.error_codes(text) == expected

# ---------------- SQL
def test_s1_to_s4(ws):
    import sqlite3
    import exS_1_warmup, exS_2_fix_query, exS_3_business, exS_4_parameters as s4
    con = sqlite3.connect("shop.db")
    assert len(exS_1_warmup.berlin_customers()) == con.execute(
        "SELECT COUNT(*) FROM customers WHERE city='Berlin'").fetchone()[0]
    assert exS_1_warmup.cheapest_products()[0][1] == con.execute(
        "SELECT MIN(price) FROM products").fetchone()[0]
    fixed = exS_3_business.run(exS_2_fix_query.FIXED)
    total = con.execute("SELECT SUM(oi.quantity*p.price) FROM order_items oi JOIN products p "
                        "ON p.id=oi.product_id JOIN orders o ON o.id=oi.order_id "
                        "WHERE o.status!='cancelled'").fetchone()[0]
    assert round(sum(r[2] for r in fixed), 2) == round(total, 2)   # every order counted once
    months = exS_3_business.run(exS_3_business.REVENUE_PER_MONTH)
    assert all(m.startswith("2025-") for m, _ in months)
    assert exS_3_business.run(exS_3_business.BOUGHT_WITH_LAPTOP)[0][0] != "Laptop"
    evil = "Pune' OR '1'='1"
    assert s4.orders_for_city(evil) == 0
    assert s4.orders_for_city_unsafe(evil) == con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

# ---------------- async
def test_a1_measure():
    import exA_1_measure as ex
    s, g = ex.main(scale=0.05)
    assert s == pytest.approx(0.40, abs=0.08) and g == pytest.approx(0.15, abs=0.06)

def test_a2_fixed(capsys):
    import exA_2_fixed as ex
    assert asyncio.run(ex.main(pause=0.05)).startswith("x done")

def test_a3_semaphore():
    import exA_3_semaphore as ex
    results, peak, total = ex.main(seconds=0.05)
    assert len(results) == 10 and peak == 3 and total == pytest.approx(0.20, abs=0.08)

def test_a4_timeouts():
    import exA_4_timeouts as ex
    results, timed_out, took = ex.main(scale=0.05)
    assert timed_out == ["slow"] and len(results) == 4 and took < 0.3
