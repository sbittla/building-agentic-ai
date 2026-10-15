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
    # The planner writes free-form queries ("Berlin weather forecast tomorrow"), so try the
    # likely city words in turn: after " in ", then capitalized words, then the rest.
    words = [w.strip(" ?.,") for w in query.split()]
    candidates = ([query.split(" in ")[-1].strip(" ?.")] if " in " in query else []) + \
        [w for w in words if w[:1].isupper()] + [w for w in words if w[:1].islower()]
    STOPWORDS = {"weather", "forecast", "rain", "tomorrow", "today", "next", "days", "three",
                 "will", "the", "for", "week", "temperature", "what", "is", "it"}
    p = None
    for city in candidates:
        if not city or city.lower() in STOPWORDS:
            continue
        found = weather.geocode(city)
        if not found.startswith("ERROR"):
            p = json.loads(found)[0]
            break
    if p is None:
        return []
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
