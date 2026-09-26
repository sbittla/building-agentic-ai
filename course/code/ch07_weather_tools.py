"""Chapter 7: tools that call a real API (Open-Meteo, free for non-commercial use)."""
import json
import random
import threading
import time
from collections import OrderedDict
import httpx

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_SECONDS = 600
CACHE_MAX_ENTRIES = 500       # bounded: an agent can ask for a LOT of different places
_cache: OrderedDict = OrderedDict()   # (url, params) -> (expires_at, data), oldest first
_cache_lock = threading.Lock()        # tools may run in parallel threads (exercise 7.5)
stats = {"http_calls": 0, "cache_hits": 0}

def _cache_get(key):
    with _cache_lock:
        hit = _cache.get(key)
        if hit and hit[0] > time.time():
            stats["cache_hits"] += 1
            return hit[1]
    return None

def _cache_put(key, data):
    with _cache_lock:
        _cache[key] = (time.time() + CACHE_SECONDS, data)
        _cache.move_to_end(key)
        while len(_cache) > CACHE_MAX_ENTRIES:
            _cache.popitem(last=False)                 # drop the oldest entry

def _wait_before_retry(attempt: int, response=None) -> float:
    """How long to wait: the server's Retry-After if it sent one (seconds), otherwise
    exponential backoff with jitter, so many clients don't all retry at the same moment."""
    retry_after = getattr(response, "headers", {}).get("retry-after") if response is not None else None
    if retry_after:
        try:
            return min(float(retry_after), 30.0)
        except ValueError:
            pass                                 # an HTTP date instead of seconds: back off
    return 0.5 * 2 ** attempt * random.uniform(0.5, 1.5)   # ~0.5 s, ~1 s, ~2 s ...

def _get_json(url: str, params: dict, retries: int = 2, timeout: float = 10.0):
    """GET with a timeout, retries (honoring Retry-After), and a small bounded cache."""
    key = (url, json.dumps(params, sort_keys=True))
    if (data := _cache_get(key)) is not None:
        return data
    last_error = None
    for attempt in range(retries + 1):
        response = None
        try:
            with _cache_lock:
                stats["http_calls"] += 1
            response = httpx.get(url, params=params, timeout=timeout)
            if response.status_code == 429 or response.status_code >= 500:   # worth retrying
                raise httpx.HTTPStatusError(f"HTTP {response.status_code}",
                                            request=response.request, response=response)
            response.raise_for_status()                         # other 4xx: don't retry
            data = response.json()
            _cache_put(key, data)
            return data
        except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as e:
            last_error = e
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500 \
                    and e.response.status_code != 429:
                break
            if attempt < retries:                               # no pointless final wait
                time.sleep(_wait_before_retry(attempt, response))
    raise RuntimeError(f"weather service unavailable after {retries + 1} tries: "
                       f"{last_error}")

def geocode(city: str) -> str:
    """Return up to 5 candidate places so the model can disambiguate."""
    data = _get_json(GEO_URL, {"name": city, "count": 5, "format": "json"})
    places = data.get("results") or []
    if not places:
        return f"ERROR: no place called '{city}'. Check spelling or add a country."
    return json.dumps([{"name": p["name"], "admin1": p.get("admin1"),
                        "country": p.get("country"), "latitude": p["latitude"],
                        "longitude": p["longitude"]} for p in places])

def get_forecast(latitude: float, longitude: float, days: int = 3) -> str:
    """Daily min/max temperature (C) and max precipitation probability (%)."""
    days = max(1, min(days, 16))
    data = _get_json(FORECAST_URL, {
        "latitude": latitude, "longitude": longitude, "timezone": "auto",
        "forecast_days": days,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
    })
    d = data["daily"]
    rows = zip(d["time"], d["temperature_2m_min"], d["temperature_2m_max"],
               d["precipitation_probability_max"])
    return "\n".join(f"{t}: {lo}..{hi} C, rain chance {p}%" for t, lo, hi, p in rows)

REGISTRY = {"geocode": geocode, "get_forecast": get_forecast}
TOOLS = [
    {"name": "geocode", "description": "Find latitude/longitude for a city. Returns "
     "up to 5 candidates. If more than one plausible match exists, ask the user "
     "which one they mean.", "input_schema": {"type": "object", "properties": {
         "city": {"type": "string"}}, "required": ["city"]}},
    {"name": "get_forecast", "description": "Daily forecast for coordinates, up to "
     "16 days. Temperatures in Celsius.", "input_schema": {"type": "object",
         "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"},
                        "days": {"type": "integer"}},
         "required": ["latitude", "longitude"]}},
]
SYSTEM = ("You are a travel packing advisor. Get real forecasts with the tools; "
          "never guess the weather. Give a short, practical packing list.")

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

if __name__ == "__main__":
    from ch04_agent import run_agent
    answer, _, s = run_agent("What should I pack for Seattle for the next 3 days?",
                             TOOLS, run_tool, system=SYSTEM)
    print(answer, s, stats)
