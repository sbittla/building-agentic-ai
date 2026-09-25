"""Chapters 6-7 reference solutions."""
import time
import httpx
import pytest
from fakemodel import tool, text, last_user_text

def test_6_3_notes_agent_with_citations(model):
    import ch06_notes_tools as n, ch04_agent
    model.reset([[tool("search_files", {"pattern": "kafka"})],
                 [text("Lag spiked (work/2026-06-02-incident-kafka-lag.md:2).")]])
    answer, _, _ = ch04_agent.run_agent("Which notes mention Kafka?", n.TOOLS, n.run_tool,
                                        system=n.SYSTEM, verbose=False)
    first_result = model.calls[1]["messages"][-1]["content"][0]["content"]
    assert "kafka-lag.md" in first_result and "(work/" in answer

def test_6_5_citation_checker_catches_bad_citation():
    import ex6_5_citation_checker as c
    report = c.check_citations(
        "Consumer lag spiked to 2.1M messages (work/2026-06-02-incident-kafka-lag.md:2). "
        "Kafka 4.1 removes ZooKeeper (personal/recipes.md:2). "
        "Also (nope.md:1).")
    assert [r["ok"] for r in report] == [True, False, False]

def test_6_6_find_files_by_date(model):
    import sol_ch06_notes_tools as n
    july = n.find_files("*kafka*", "2026-07-01", "2026-07-31")
    assert "kafka-upgrade-plan" in july and "incident" not in july
    import ch04_agent
    model.reset([[tool("find_files", {"name_pattern": "*kafka*", "modified_after": "2026-07-01",
                                      "modified_before": "2026-07-31"})], [text("The upgrade plan.")]])
    ch04_agent.run_agent("What did I write about Kafka in July 2026?", n.TOOLS, n.run_tool,
                         system=n.SYSTEM, verbose=False)
    assert "find_files" in n.SYSTEM and "upgrade" in model.calls[1]["messages"][-1]["content"][0]["content"]

def test_6_7_scale_test(model, ws):
    import generate, ex6_7_scale_test as ex
    generate.notes(80, "notes_big")
    qs = ex.questions()
    assert len(qs) == 15
    truth = dict(qs)
    def fake(kw):
        q = last_user_text(kw).split("Question: ")[-1]
        if "tools" not in kw:                                  # baseline: one big prompt
            return [text(truth[q] if truth[q] in last_user_text(kw) else "not found")]
        if len(kw["messages"]) == 1:
            return [tool("search_files", {"pattern": "project " + q[-2]})]
        found = kw["messages"][-1]["content"][0]["content"]
        return [text(found)]
    model.reset(default=fake)
    rows = ex.main(limit=5)
    assert all(r[1] for r in rows)                             # agentic search finds them

class _R:
    def __init__(s, code, data): s.status_code, s._d, s.request = code, data, None
    def json(s): return s._d
    def raise_for_status(s):
        if s.status_code >= 400:
            raise httpx.HTTPStatusError("x", request=None, response=s)

@pytest.fixture
def fake_http(monkeypatch):
    import ch07_weather_tools as w
    w._cache.clear(); w.stats.update(http_calls=0, cache_hits=0)
    seen = []
    places = {"Portland": [{"name": "Portland", "admin1": "Oregon", "country": "US", "latitude": 45.5, "longitude": -122.7},
                           {"name": "Portland", "admin1": "Maine", "country": "US", "latitude": 43.7, "longitude": -70.3}],
              "Seattle": [{"name": "Seattle", "country": "US", "latitude": 47.6, "longitude": -122.3}],
              "Austin": [{"name": "Austin", "country": "US", "latitude": 30.3, "longitude": -97.7}],
              "Pune": [{"name": "Pune", "country": "India", "latitude": 18.5, "longitude": 73.9}]}
    def get(url, params, timeout):
        seen.append((url, params))
        time.sleep(0.05)
        if "geocoding" in url:
            return _R(200, {"results": places.get(params["name"], [])})
        unit = params.get("temperature_unit", "celsius")
        hi = 86 if unit == "fahrenheit" else 30
        return _R(200, {"daily": {"time": ["2026-09-24"], "temperature_2m_min": [hi - 10],
                                  "temperature_2m_max": [hi], "precipitation_probability_max": [40]}})
    monkeypatch.setattr(httpx, "get", get)
    monkeypatch.setattr(w.time, "sleep", lambda s: None)
    return seen

def test_7_3_packing_agent(model, fake_http):
    import ch07_weather_tools as w, ch04_agent
    model.reset([[tool("geocode", {"city": "Seattle"})],
                 [tool("get_forecast", {"latitude": 47.6, "longitude": -122.3})],
                 [text("Pack layers and a rain jacket.")]])
    answer, _, s = ch04_agent.run_agent("Pack for Seattle", w.TOOLS, w.run_tool, system=w.SYSTEM, verbose=False)
    assert s["tool_calls"] == 2 and "rain chance 40%" in model.calls[2]["messages"][-1]["content"][0]["content"]

def test_7_4_fahrenheit(fake_http):
    import sol_ch07_weather_tools as w
    out = w.run_tool("get_forecast", {"latitude": 30.3, "longitude": -97.7, "units": "fahrenheit"})
    assert "86 F" in out and fake_http[-1][1]["temperature_unit"] == "fahrenheit"
    assert w.run_tool("get_forecast", {"latitude": 1, "longitude": 1, "units": "kelvin"}).startswith("ERROR")

def test_7_4_budget(fake_http):
    import sol_ch07_weather_tools as w, ch07_weather_tools as base
    base.stats["http_calls"] = w.MAX_HTTP_CALLS
    assert "budget" in w.run_tool("geocode", {"city": "Pune"})
    base.stats["http_calls"] = 0

def test_7_5_hard_cases(model, fake_http):
    import ex7_5_hard_cases as ex, ch07_weather_tools as w
    model.reset([[tool("geocode", {"city": "Xyzzyqq"})], [text("I couldn't find that place.")],
                 [tool("geocode", {"city": "Portland"})], [text("Portland, Oregon or Maine?")]])
    assert "couldn't" in ex.unknown_city()
    assert "no place called" in model.calls[1]["messages"][-1]["content"][0]["content"]
    assert "Oregon or Maine" in ex.ambiguous_city()

def test_7_5_timeout_retries(monkeypatch):
    import ex7_5_hard_cases as ex, ch07_weather_tools as w
    calls = []
    def boom(url, params, timeout):
        calls.append(url); raise httpx.ConnectTimeout("timed out")
    monkeypatch.setattr(httpx, "get", boom)
    monkeypatch.setattr(w.time, "sleep", lambda s: None)
    out, secs = ex.simulated_timeout()
    assert out.startswith("ERROR") and "after 3 tries" in out and len(calls) == 3
    assert w.FORECAST_URL.startswith("https://api.open-meteo.com")    # restored

def test_7_6_parallel_keeps_order_and_is_faster(model):
    import ex7_6_parallel as ex
    def slow_tool(name, args):
        time.sleep(0.3); return f"{name}:{args['n']}"
    tools = [{"name": "slow", "description": "x", "input_schema": {"type": "object", "properties": {}}}]
    model.reset([[tool("slow", {"n": i}) for i in range(4)], [text("done")]])
    t0 = time.perf_counter()
    answer, stats = ex.run_agent_parallel("q", tools, slow_tool)
    assert time.perf_counter() - t0 < 0.9 and stats["tool_calls"] == 4
    results = model.calls[1]["messages"][-1]["content"]
    assert [r["content"] for r in results] == [f"slow:{i}" for i in range(4)]

def test_7_6_compare_sequential_and_parallel(model):
    import ex7_6_parallel as ex
    def slow_tool(name, args):
        time.sleep(0.2); return "ok"
    tools = [{"name": "slow", "description": "x", "input_schema": {"type": "object", "properties": {}}}]
    model.reset([[tool("slow", {"n": i}) for i in range(4)], [text("done")]] * 2)
    r = ex.compare("q", tools, slow_tool, "sys")
    assert r["sequential"]["tool_seconds"] > 2.5 * r["parallel"]["tool_seconds"]

def test_7_7_trip_benchmark(model, fake_http):
    import ex7_7_trip_benchmark as ex
    def planner(kw):
        n = len(kw["messages"])
        if n == 1:
            return [tool("geocode", {"city": c}) for c in ("Seattle", "Austin", "Pune")]
        if n == 3:
            return [tool("get_forecast", {"latitude": 47.6, "longitude": -122.3}),
                    tool("get_forecast", {"latitude": 30.3, "longitude": -97.7}),
                    tool("get_forecast", {"latitude": 18.5, "longitude": 73.9})]
        return [text("Pack layers.")]
    model.reset(default=planner)
    table = ex.main(runs=2)
    on, off = table["cache on"], table["cache off"]
    assert on[1]["http_calls"] == 0 and on[1]["cache_hits"] == 6
    assert all(r["http_calls"] == 6 for r in off)


def test_7_retry_after_and_jitter():
    from types import SimpleNamespace as S
    import ch07_weather_tools as w
    assert w._wait_before_retry(0, S(headers={"retry-after": "7"})) == 7.0      # the server knows best
    assert w._wait_before_retry(0, S(headers={"retry-after": "999"})) == 30.0   # but capped
    waits = {round(w._wait_before_retry(2, S(headers={})), 3) for _ in range(20)}
    assert len(waits) > 5 and all(1.0 <= x <= 3.0 for x in waits)             # ~2 s, with jitter
    assert w._wait_before_retry(1, object()) > 0                              # no headers at all
