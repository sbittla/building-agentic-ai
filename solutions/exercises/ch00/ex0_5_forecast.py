"""Exercise 0.5 (solution): summarize a forecast given as JSON text."""
import json

EXAMPLE = json.dumps({"city": "Pune", "days": [
    {"date": "2026-10-01", "max_c": 31, "rain": 0.7},
    {"date": "2026-10-02", "max_c": 29, "rain": 0.9},
    {"date": "2026-10-03", "max_c": 33, "rain": 0.2}]})

def summarize_forecast(json_text: str) -> dict | str:
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        return f"ERROR: not valid JSON ({exc.msg} at position {exc.pos})"
    days = data.get("days") if isinstance(data, dict) else None
    if not days:
        return "ERROR: the forecast has no 'days' list"
    hottest = max(days, key=lambda d: d["max_c"])
    return {
        "city": data.get("city"),
        "hottest_day": hottest["date"],
        "hottest_c": hottest["max_c"],
        "average_max_c": round(sum(d["max_c"] for d in days) / len(days), 1),
        "rainy_days": [d["date"] for d in days if d.get("rain", 0) > 0.5],
    }

def main():
    print(summarize_forecast(EXAMPLE))
    print(summarize_forecast("not json"))
    print(summarize_forecast('{"city": "Oslo"}'))

if __name__ == "__main__":
    main()
