"""Open the geocoding URL in your browser first to see what the JSON looks like:
https://geocoding-api.open-meteo.com/v1/search?name=Pune&count=1
The answer is in data["results"][0]["latitude"] and ["longitude"]. When no city is
found, there is no "results" key at all."""
import httpx

GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST = "https://api.open-meteo.com/v1/forecast"


def _get(url: str, params: dict):
    """Returns (data, None) or (None, "ERROR: ...")."""
    try:
        r = httpx.get(url, params=params, timeout=10)
    except httpx.HTTPError as exc:
        return None, f"ERROR: could not reach {url} ({type(exc).__name__})"
    # TODO: return an ERROR for a status that isn't 200, else (r.json(), None)
    raise NotImplementedError


def city_temperature(city: str, geocode_url: str = GEOCODE) -> str:
    """Today's maximum temperature for a city, like "Pune, India: max 31.4 C today",
    or a string starting with "ERROR:" (no network, bad status, city not found)."""
    # TODO: 1) geocode with {"name": city, "count": 1}
    #       2) forecast with latitude, longitude, "daily": "temperature_2m_max",
    #          "forecast_days": 1, "timezone": "auto"
    raise NotImplementedError


if __name__ == "__main__":
    for c in ["Pune", "Oslo", "Xyzzyqq"]:
        print(city_temperature(c))
