"""Exercise 30.6 (solution): load-test the agent API over HTTP.

20 users, 5 API keys, for a fixed time. Start the API with a per-key limit of 30/min:
    AGENT_API_KEYS=k1,k2,k3,k4,k5  AGENT_RATE_PER_MINUTE=30   (in .env), then ./course.sh serve-api
    ./course.sh python exercises/ex30_6_drill.py

Report: p50/p95 latency of successful requests, 429 and 502 counts, and cost per request
from the token counts the API returns. Run it, change ONE thing, and run it again."""
import os
import statistics
import threading
import time
import httpx
from ch16_context import cost

API = os.environ.get("AGENT_API_URL") or __import__("ch30_client").API
KEYS = os.environ.get("DRILL_KEYS", "k1,k2,k3,k4,k5").split(",")
QUESTIONS = ["How many orders are there?", "Which city has the most customers?",
             "What is the most expensive product?", "How many orders were cancelled?"]

def pct(values, p):
    values = sorted(values)
    return values[min(len(values) - 1, int(round(p / 100 * (len(values) - 1))))] if values else 0

def user(n, until, results, lock, api=API):
    key = KEYS[n % len(KEYS)]
    with httpx.Client(timeout=120) as http:
        i = 0
        while i == 0 or time.monotonic() < until:        # every user sends at least one request
            t0 = time.perf_counter()
            try:
                r = http.post(f"{api}/v1/chat", json={"message": QUESTIONS[i % len(QUESTIONS)]},
                              headers={"Authorization": f"Bearer {key}"})
                row = {"status": r.status_code, "s": time.perf_counter() - t0}
                if r.status_code == 200:
                    row.update(r.json())
                elif r.status_code == 429:                  # respect Retry-After, like a good client
                    time.sleep(min(float(r.headers.get("retry-after", 1)), max(0, until - time.monotonic())))
            except httpx.HTTPError as exc:
                row = {"status": type(exc).__name__, "s": time.perf_counter() - t0}
            with lock:
                results.append(row)
            i += 1

def drill(users=20, seconds=120, api=API):
    results, lock = [], threading.Lock()
    until = time.monotonic() + seconds
    threads = [threading.Thread(target=user, args=(n, until, results, lock, api)) for n in range(users)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    ok = [r for r in results if r["status"] == 200]
    costs = [cost(r["input_tokens"], r["output_tokens"]) for r in ok]
    summary = {
        "requests": len(results), "ok": len(ok),
        "429": sum(r["status"] == 429 for r in results),
        "502": sum(r["status"] == 502 for r in results),
        "other_errors": sum(r["status"] not in (200, 429, 502) for r in results),
        "p50_s": round(pct([r["s"] for r in ok], 50), 2),
        "p95_s": round(pct([r["s"] for r in ok], 95), 2),
        "cost_per_request_usd": round(statistics.mean(costs), 5) if costs else 0,
    }
    return summary

def main(users=20, seconds=120):
    s = drill(users, seconds)
    print(" | ".join(f"{k} {v}" for k, v in s.items()))
    print("\nIdeas for the 'one change': cap history length per session; use a smaller model "
          "for simple questions; cache the system prompt and tools (chapter 16); raise the rate "
          "limit only if the model API's own limits allow it.")
    return s

if __name__ == "__main__":
    main()
