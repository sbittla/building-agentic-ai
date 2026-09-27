"""Exercise 0.6 (solution): two API calls in a row, with careful error handling."""
import httpx

GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST = "https://api.open-meteo.com/v1/forecast"

def _get(url: str, params: dict):
    """Returns (data, None) or (None, 'ERROR: ...')."""
    try:
        r = httpx.get(url, params=params, timeout=10)
    except httpx.HTTPError as exc:
        return None, f"ERROR: could not reach {url} ({type(exc).__name__})"
    if r.status_code != 200:
        return None, f"ERROR: HTTP {r.status_code} from {url}"
    try:
        return r.json(), None
    except ValueError:
        return None, f"ERROR: {url} did not return JSON"

def city_temperature(city: str, geocode_url: str = GEOCODE) -> str:
    data, err = _get(geocode_url, {"name": city, "count": 1})
    if err:
        return err
    results = data.get("results") or []
    if not results:
        return f"ERROR: no city called '{city}' was found"
    place = results[0]
    data, err = _get(FORECAST, {"latitude": place["latitude"], "longitude": place["longitude"],
                                "daily": "temperature_2m_max", "forecast_days": 1,
                                "timezone": "auto"})
    if err:
        return err
    return (f"{place['name']}, {place.get('country', '?')}: max "
            f"{data['daily']['temperature_2m_max'][0]} C today")

def main():
    for city in ["Pune", "Oslo", "Austin", "Xyzzyqq"]:
        print(city_temperature(city))
    print(city_temperature("Pune", geocode_url="https://geocoding-api.open-meteo.com/v1/nope"))

if __name__ == "__main__":
    main()
