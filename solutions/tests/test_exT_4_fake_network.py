"""Exercise T.4 (solution): test max_temperature with no internet, using monkeypatch."""
import httpx
import pytest
import ch00_http

class FakeResponse:
    def __init__(self, status_code, data=None, text=""):
        self.status_code, self._data, self.text = status_code, data, text
    def json(self):
        return self._data

def test_ok(monkeypatch):
    seen = {}
    def fake_get(url, params=None, timeout=None):
        seen.update(url=url, params=params)
        return FakeResponse(200, {"daily": {"time": ["2026-10-01"], "temperature_2m_max": [31.4]}})
    monkeypatch.setattr(ch00_http.httpx, "get", fake_get)
    assert ch00_http.max_temperature(18.52, 73.86) == "2026-10-01: max 31.4 C"
    assert seen["params"]["latitude"] == 18.52

def test_server_error(monkeypatch):
    monkeypatch.setattr(ch00_http.httpx, "get",
                        lambda *a, **k: FakeResponse(503, text="Service Unavailable"))
    assert ch00_http.max_temperature(0, 0).startswith("ERROR: HTTP 503")

def test_no_network(monkeypatch):
    def boom(*a, **k):
        raise httpx.ConnectError("no network")
    monkeypatch.setattr(ch00_http.httpx, "get", boom)
    assert "could not reach" in ch00_http.max_temperature(0, 0)
