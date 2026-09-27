"""Chapter 7 reference solution: 7.4 (Fahrenheit) and the per-run API budget (7.6 text)."""
import ch07_weather_tools as base
from ch07_weather_tools import geocode, stats, _get_json, FORECAST_URL

MAX_HTTP_CALLS = 20

def get_forecast(latitude: float, longitude: float, days: int = 3,
                 units: str = "celsius") -> str:
    if units not in ("celsius", "fahrenheit"):
        return "ERROR: units must be celsius or fahrenheit"
    days = max(1, min(days, 16))
    data = _get_json(base.FORECAST_URL, {
        "latitude": latitude, "longitude": longitude, "timezone": "auto",
        "forecast_days": days, "temperature_unit": units,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max"})
    d = data["daily"]
    sym = "F" if units == "fahrenheit" else "C"
    return "\n".join(f"{t}: {lo}..{hi} {sym}, rain chance {p}%" for t, lo, hi, p in zip(
        d["time"], d["temperature_2m_min"], d["temperature_2m_max"],
        d["precipitation_probability_max"]))

REGISTRY = {"geocode": geocode, "get_forecast": get_forecast}
TOOLS = [base.TOOLS[0], {
    "name": "get_forecast", "description": "Daily forecast for coordinates, up to 16 days. "
    "Use units='fahrenheit' if the user asks for Fahrenheit.",
    "input_schema": {"type": "object", "properties": {
        "latitude": {"type": "number"}, "longitude": {"type": "number"},
        "days": {"type": "integer"}, "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}},
        "required": ["latitude", "longitude"]}}]
SYSTEM = base.SYSTEM

def run_tool(name, args):
    if stats["http_calls"] >= MAX_HTTP_CALLS:
        return "ERROR: API budget for this run is used up. Answer with what you have."
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"
