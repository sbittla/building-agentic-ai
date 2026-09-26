"""Chapter 3 reference solution for exercise 3.3: add get_current_time(timezone)."""
from datetime import datetime
from zoneinfo import ZoneInfo
import ch03_tools as base

ZONES = ["Asia/Tokyo", "Asia/Kolkata", "Europe/Berlin", "America/New_York",
         "America/Los_Angeles"]

def get_current_time(timezone: str) -> str:
    if timezone not in ZONES:
        return f"ERROR: unsupported time zone {timezone}. Use one of: {', '.join(ZONES)}"
    now = datetime.now(ZoneInfo(timezone))
    return now.strftime(f"%Y-%m-%d %H:%M ({timezone}, %A)")

REGISTRY = {**base.REGISTRY, "get_current_time": get_current_time}
TOOLS = base.TOOLS + [{
    "name": "get_current_time",
    "description": "Current local time in a city's time zone. Use for 'what time is it in X'.",
    "input_schema": {"type": "object", "properties": {
        "timezone": {"type": "string", "enum": ZONES,
                     "description": "IANA zone, e.g. Asia/Tokyo for Tokyo"}},
        "required": ["timezone"]}}]

def run_tool(name, args):
    fn = REGISTRY.get(name)
    if fn is None:
        return f"ERROR: unknown tool '{name}'"
    try:
        return str(fn(**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"
