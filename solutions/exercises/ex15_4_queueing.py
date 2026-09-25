"""Exercise 15.4 (solution): see queueing, and see how the wrong clock hides it.

Same open-loop traffic, two clocks:
  from intended send  -- the right one: includes waiting for a free slot
  after getting a slot -- the wrong one: starts timing only once work begins"""
import asyncio
import random
import time
import ch15_loadtest as lt

async def after_slot(agent, rate, seconds, max_in_flight=20, seed=1):
    """The WRONG clock: identical traffic, but t0 is taken inside the semaphore."""
    rng, sem, latencies = random.Random(seed), asyncio.Semaphore(max_in_flight), []
    start = time.perf_counter()
    async def one(i, scheduled):
        await asyncio.sleep(max(0.0, start + scheduled - time.perf_counter()))
        async with sem:
            t0 = time.perf_counter()
            await agent(f"q{i}")
            latencies.append(time.perf_counter() - t0)
    arrivals, t = [], 0.0
    while (t := t + rng.expovariate(rate)) <= seconds:
        arrivals.append(t)
    await asyncio.gather(*(one(i, a) for i, a in enumerate(arrivals)))
    return lt.pct(latencies, 50), lt.pct(latencies, 95)

def main(rates=(4, 8, 12), seconds=20, max_in_flight=20):
    print("| offered/s | p50 from send | p95 from send | p50 after slot | p95 after slot |")
    rows = []
    for rate in rates:
        r = asyncio.run(lt.open_loop(lt.fake_agent, rate, seconds, max_in_flight))
        s50, s95 = asyncio.run(after_slot(lt.fake_agent, rate, seconds, max_in_flight))
        rows.append((rate, r["p50"], r["p95"], s50, s95))
        print(f"| {rate} | {r['p50']:.1f}s | {r['p95']:.1f}s | {s50:.1f}s | {s95:.1f}s |")
    print("Past capacity, the right clock shows latency climbing while the wrong one stays flat:"
          "\nit leaves out the queue, which is exactly the part users feel.")
    return rows

if __name__ == "__main__":
    main()
