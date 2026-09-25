import json

EXAMPLE = json.dumps({"city": "Pune", "days": [
    {"date": "2026-10-01", "max_c": 31, "rain": 0.7},
    {"date": "2026-10-02", "max_c": 29, "rain": 0.9},
    {"date": "2026-10-03", "max_c": 33, "rain": 0.2}]})


def summarize_forecast(json_text: str) -> dict | str:
    """Return {"city", "hottest_day", "hottest_c", "average_max_c" (1 decimal),
    "rainy_days" (dates with rain > 0.5)}, or a string starting with "ERROR:" if the
    text isn't valid JSON or has no "days" list."""
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        return f"ERROR: not valid JSON ({exc.msg})"
    # TODO: check data has a non-empty "days" list, then compute the fields
    raise NotImplementedError


if __name__ == "__main__":
    print(summarize_forecast(EXAMPLE))
    print(summarize_forecast("not json"))
