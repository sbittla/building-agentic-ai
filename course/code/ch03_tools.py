"""Chapter 3: several tools, one registry. The model chooses."""
from datetime import date, datetime
from ch02_calculator_agent import calculate

def get_current_date() -> str:
    """Return today's date and weekday, e.g. '2026-09-23 (Wednesday)'."""
    today = date.today()
    return f"{today.isoformat()} ({today.strftime('%A')})"

_FACTORS = {  # everything converted through a base unit
    ("km", "m"): 1000, ("mi", "m"): 1609.344, ("m", "m"): 1,
    ("kg", "g"): 1000, ("lb", "g"): 453.59237, ("g", "g"): 1,
}
_BASE = {"km": "m", "mi": "m", "m": "m", "kg": "g", "lb": "g", "g": "g"}

def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between km, mi, m, kg, lb, g."""
    f, t = from_unit.lower(), to_unit.lower()
    if f not in _BASE or t not in _BASE or _BASE[f] != _BASE[t]:
        return f"ERROR: cannot convert {from_unit} to {to_unit}"
    base = _BASE[f]
    result = value * _FACTORS[(f, base)] / _FACTORS[(t, base)]
    return f"{value} {from_unit} = {round(result, 4)} {to_unit}"

def days_between(start: str, end: str) -> str:
    """Days from start to end (ISO dates) plus the weekday of end."""
    s, e = datetime.fromisoformat(start).date(), datetime.fromisoformat(end).date()
    return f"{(e - s).days} days; {end} is a {e.strftime('%A')}"

# The registry maps tool names to Python functions ...
REGISTRY = {
    "calculate": calculate,
    "get_current_date": get_current_date,
    "convert_units": convert_units,
    "days_between": days_between,
}

# ... and TOOLS describes them to the model. Descriptions do the routing!
TOOLS = [
    {"name": "calculate",
     "description": "Exact arithmetic on a numeric expression. Not for dates or units.",
     "input_schema": {"type": "object",
                      "properties": {"expression": {"type": "string"}},
                      "required": ["expression"]}},
    {"name": "get_current_date",
     "description": "Today's date and weekday. Call this whenever the question "
                    "depends on 'today', 'now', 'this week' or a relative date.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "convert_units",
     "description": "Convert a distance or weight between km, mi, m, kg, lb, g.",
     "input_schema": {"type": "object",
                      "properties": {"value": {"type": "number"},
                                     "from_unit": {"type": "string",
                                                   "enum": list(_BASE)},
                                     "to_unit": {"type": "string",
                                                 "enum": list(_BASE)}},
                      "required": ["value", "from_unit", "to_unit"]}},
    {"name": "days_between",
     "description": "Number of days between two ISO dates (YYYY-MM-DD) and the "
                    "weekday of the second date.",
     "input_schema": {"type": "object",
                      "properties": {"start": {"type": "string"},
                                     "end": {"type": "string"}},
                      "required": ["start", "end"]}},
]

def run_tool(name: str, args: dict) -> str:
    """Look up and run a tool. Errors come back as text the model can read."""
    fn = REGISTRY.get(name)
    if fn is None:
        return f"ERROR: unknown tool '{name}'"
    try:
        return str(fn(**args))
    except Exception as exc:  # the model should see failures, not crash on them
        return f"ERROR: {type(exc).__name__}: {exc}"
