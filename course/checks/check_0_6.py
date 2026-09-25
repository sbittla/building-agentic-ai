import httpx

class R:
    def __init__(self, code, data=None):
        self.status_code, self._d, self.text = code, data, ""
    def json(self):
        return self._d

def fake_get(url, params=None, timeout=None):
    if "nope" in url:
        return R(404)
    if "geocoding" in url:
        if params["name"] == "Xyzzyqq":
            return R(200, {"generationtime_ms": 0.1})
        return R(200, {"results": [{"name": params["name"], "country": "India",
                                    "latitude": 18.5, "longitude": 73.9}]})
    return R(200, {"daily": {"temperature_2m_max": [30.1]}})

def test_success(ex, monkeypatch):
    monkeypatch.setattr(ex.httpx, "get", fake_get)
    out = ex.city_temperature("Pune")
    assert "30.1" in out and not out.startswith("ERROR"), f"expected the max temperature, got {out!r}"

def test_city_not_found(ex, monkeypatch):
    monkeypatch.setattr(ex.httpx, "get", fake_get)
    assert ex.city_temperature("Xyzzyqq").startswith("ERROR"), "no 'results' -> an ERROR string"

def test_bad_status(ex, monkeypatch):
    monkeypatch.setattr(ex.httpx, "get", fake_get)
    assert ex.city_temperature("Pune", geocode_url="https://x/nope").startswith("ERROR"), "HTTP 404 -> ERROR"

def test_no_network(ex, monkeypatch):
    def offline(*a, **k):
        raise httpx.ConnectError("offline")
    monkeypatch.setattr(ex.httpx, "get", offline)
    assert ex.city_temperature("Pune").startswith("ERROR"), "no network -> an ERROR string, not a crash"
