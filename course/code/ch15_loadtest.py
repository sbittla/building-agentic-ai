"""Chapter 15: load-test an agent and report latency percentiles.

Run:  python ch15_loadtest.py [requests_per_second] [max_in_flight] [seconds]
      e.g.  python ch15_loadtest.py 4     (comfortable)
            python ch15_loadtest.py 12    (more than the agent can handle)

OPEN loop: requests arrive on a schedule, like real users who don't wait for each
other, and each latency is measured from when the request was SUPPOSED to be sent.
When the agent falls behind, the queue grows and the numbers show it."""
import asyncio
import random
import statistics
import sys
import time

async def fake_agent(question: str) -> str:
    """Stands in for a real agent run: 2-4 model calls of 0.3-1.2 s each."""
    for _ in range(random.randint(2, 4)):
        await asyncio.sleep(random.uniform(0.3, 1.2))
    return "ok"

def pct(values, p):
    values = sorted(values)
    return values[min(len(values) - 1, int(round(p / 100 * (len(values) - 1))))] if values else 0.0

async def open_loop(agent, rate: float, seconds: float, max_in_flight: int = 20,
                    timeout: float = 60, seed: int = 1):
    """Send about rate*seconds requests at random (Poisson) arrival times.
    max_in_flight models the system's capacity (e.g. your provider's concurrency limit)."""
    rng = random.Random(seed)
    sem = asyncio.Semaphore(max_in_flight)
    latencies, errors = [], []
    start = time.perf_counter()

    async def one(i, scheduled):
        await asyncio.sleep(max(0.0, start + scheduled - time.perf_counter()))
        async with sem:                          # waiting here IS part of the latency
            try:
                await asyncio.wait_for(agent(f"q{i}"), timeout=timeout)
                latencies.append(time.perf_counter() - (start + scheduled))  # from INTENDED send
            except Exception as exc:
                errors.append(type(exc).__name__)

    arrivals, t = [], 0.0
    while True:
        t += rng.expovariate(rate)               # random gaps, average 1/rate seconds
        if t > seconds:
            break
        arrivals.append(t)
    await asyncio.gather(*(one(i, a) for i, a in enumerate(arrivals)))
    wall = time.perf_counter() - start
    return {"offered_rps": rate, "requests": len(arrivals), "errors": len(errors),
            "throughput_rps": round(len(latencies) / wall, 2),
            "p50": pct(latencies, 50), "p95": pct(latencies, 95),
            "max": max(latencies, default=0.0),
            "mean": statistics.mean(latencies) if latencies else 0.0}

# ---- the CLOSED loop, for comparison: N users, each waiting for its previous answer
async def session(agent, questions, latencies, errors, sem):
    for q in questions:
        t0 = time.perf_counter()   # start BEFORE queueing: users feel the wait
        async with sem:
            try:
                await asyncio.wait_for(agent(q), timeout=60)
                latencies.append(time.perf_counter() - t0)
            except Exception as exc:
                errors.append(type(exc).__name__)

async def load_test(agent, users=50, questions_per_user=3, max_in_flight=20):
    """Closed loop. When the agent slows down, these users send LESS, so the test quietly
    reduces the load it's supposed to measure. Fine for a smoke test, not for capacity."""
    latencies, errors = [], []
    sem = asyncio.Semaphore(max_in_flight)
    await asyncio.gather(*(session(agent, [f"q{u}-{i}" for i in range(questions_per_user)],
                                   latencies, errors, sem) for u in range(users)))
    return latencies, errors

def report(r):
    print(f"offered {r['offered_rps']}/s  requests={r['requests']} errors={r['errors']} "
          f"throughput={r['throughput_rps']}/s")
    print(f"latency p50={r['p50']:.2f}s p95={r['p95']:.2f}s max={r['max']:.2f}s")

if __name__ == "__main__":
    rate = float(sys.argv[1]) if len(sys.argv) > 1 else 4
    in_flight = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 20
    report(asyncio.run(open_loop(fake_agent, rate, seconds, in_flight)))
