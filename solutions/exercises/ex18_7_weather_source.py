"""Exercise 18.7 (solution): the Chapter 7 weather tools as a fourth source. The planner
sees the description and uses it only for forecasts; the evidence cites the city and date."""
import json
import sys

import ch07_weather_tools as weather
import ch18_agentic as ka
import ch18_rag as rag

ka.SOURCES["weather"] = ("Weather forecasts for a named city, up to 7 days ahead. Only for "
                         "questions about future weather; not for anything in the notes.")
ka.NEEDS["properties"]["needs"]["items"]["properties"]["source"]["enum"] = list(ka.SOURCES)
_search = ka.search

def search(source: str, query: str) -> list[dict]:
    if source != "weather":
        return _search(source, query)
    city = query.split(" in ")[-1].strip(" ?.") if " in " in query else query.strip(" ?.")
    found = weather.geocode(city)
    if found.startswith("ERROR"):
        return []
    places = json.loads(found)
    p = places[0]
    forecast = weather.get_forecast(p["latitude"], p["longitude"], days=3)
    return [{"source": "weather", "origin": f"open-meteo:{p['name']}", "text": forecast}]

ka.search = search

QUESTIONS = ["What caused the Kafka consumer lag incident?",
             "Will it rain in Pune in the next three days?",
             "What was the fix in the Kafka lag incident, and will it rain in Berlin tomorrow "
             "for the on-site review?"]

if __name__ == "__main__":
    rag.build()
    for q in QUESTIONS[int(sys.argv[1]):int(sys.argv[1]) + 1] if len(sys.argv) > 1 else QUESTIONS:
        print(f"\nQ: {q}")
        print("plan:", [(n["source"], n["query"]) for n in ka.plan_needs(q)])
        print(ka.answer(q, verbose=False)["answer"])
