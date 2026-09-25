"""Exercise T.4: test max_temperature with no internet. Run: ./course.sh ex T.4"""
import ch00_http


class FakeResponse:
    """Just enough of an httpx response for max_temperature."""
    def __init__(self, status_code, data=None, text=""):
        self.status_code, self._data, self.text = status_code, data, text

    def json(self):
        return self._data


def test_ok(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return FakeResponse(200, {"daily": {"time": ["2026-10-01"], "temperature_2m_max": [31.4]}})
    monkeypatch.setattr(ch00_http.httpx, "get", fake_get)
    # TODO: call ch00_http.max_temperature(...) and assert on the result


def test_server_error(monkeypatch):
    # TODO: make fake_get return FakeResponse(503, text="Service Unavailable")
    #       and assert the result starts with "ERROR: HTTP 503"
    ...
