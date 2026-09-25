"""Loaded automatically by Python when this folder is on PYTHONPATH (used by the
exercise 12.7 tests): replaces httpx.get with canned Open-Meteo answers."""
import os
if os.environ.get("WEATHER_FAKE") == "1":
    import httpx

    class _R:
        def __init__(self, data):
            self.status_code, self._d, self.request = 200, data, None
        def json(self):
            return self._d
        def raise_for_status(self):
            pass

    def _get(url, params=None, timeout=None, **kw):
        if "geocoding" in url:
            name = (params or {}).get("name", "")
            return _R({"results": [{"name": "Pune", "country": "India", "latitude": 18.5,
                                    "longitude": 73.9}]} if name == "Pune" else {})
        return _R({"daily": {"time": ["2026-09-24"], "temperature_2m_min": [21],
                             "temperature_2m_max": [29], "precipitation_probability_max": [70]}})

    httpx.get = _get
