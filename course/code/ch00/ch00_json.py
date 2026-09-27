"""Chapter 0: JSON, the format every API and every agent tool speaks."""
import json

# A Python dict ...
forecast = {"city": "Pune", "days": [{"date": "2026-10-01", "max_c": 31, "rain": 0.7},
                                     {"date": "2026-10-02", "max_c": 29, "rain": 0.9}]}

# ... becomes JSON text with json.dumps, and back with json.loads.
text = json.dumps(forecast, indent=2)
print(text)
again = json.loads(text)
print(again["days"][1]["max_c"])               # 29

# JSON Schema describes what valid JSON looks like. Tools (chapter 2) use it
# to tell the model which arguments to send.
schema = {
    "type": "object",
    "properties": {"city": {"type": "string"},
                   "days": {"type": "integer", "minimum": 1, "maximum": 16}},
    "required": ["city"],
}

def check(data: dict, schema: dict) -> list[str]:
    """A tiny validator for the parts of JSON Schema this course uses."""
    problems = []
    for field in schema.get("required", []):
        if field not in data:
            problems.append(f"missing required field '{field}'")
    types = {"string": str, "integer": int, "number": (int, float), "boolean": bool,
             "object": dict, "array": list}
    for field, rules in schema.get("properties", {}).items():
        if field in data:
            if not isinstance(data[field], types[rules["type"]]):
                problems.append(f"'{field}' should be {rules['type']}")
            elif "minimum" in rules and data[field] < rules["minimum"]:
                problems.append(f"'{field}' is below {rules['minimum']}")
            elif "maximum" in rules and data[field] > rules["maximum"]:
                problems.append(f"'{field}' is above {rules['maximum']}")
    return problems

print(check({"city": "Pune", "days": 3}, schema))       # []
print(check({"days": 40}, schema))                      # two problems
