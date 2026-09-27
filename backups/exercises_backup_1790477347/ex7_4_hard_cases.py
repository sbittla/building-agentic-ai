"""Exercise 7.4 (Medium): unknown city, ambiguous city, and a simulated timeout."""
import time
import ch07_weather_tools as w
from ch04_agent import run_agent

def unknown_city():
    return run_agent("What should I pack for Xyzzyqq?", w.TOOLS, w.run_tool, system=w.SYSTEM)[0]

def ambiguous_city():
    return run_agent("What should I pack for Portland?", w.TOOLS, w.run_tool, system=w.SYSTEM)[0]

def simulated_timeout():
    """Point the forecast at an unroutable address with a short timeout."""
    real_url, real_get = w.FORECAST_URL, w._get_json
    w.FORECAST_URL = "https://10.255.255.1/v1/forecast"
    w._get_json = lambda url, params, retries=2, timeout=2.0: real_get(url, params, retries, timeout)
    w._cache.clear()
    t0 = time.perf_counter()
    try:
        out = w.run_tool("get_forecast", {"latitude": 47.6, "longitude": -122.3})
    finally:
        w.FORECAST_URL, w._get_json = real_url, real_get
    return out, time.perf_counter() - t0

if __name__ == "__main__":
    print("(a)", unknown_city(), "\n")
    print("(b)", ambiguous_city(), "\n")
    out, secs = simulated_timeout()
    print(f"(c) tool returned after {secs:.1f}s with 3 tries: {out}")
