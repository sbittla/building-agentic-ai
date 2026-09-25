"""Exercise A.4 (solution): a timeout per call, keep what arrived."""
import asyncio
import time
from i_async import fetch

async def fetch_with_timeouts(jobs: dict, timeout=2.0):
    async def one(name, seconds):
        try:
            return name, await asyncio.wait_for(fetch(name, seconds), timeout)
        except asyncio.TimeoutError:
            return name, None
    pairs = await asyncio.gather(*(one(n, s) for n, s in jobs.items()))
    results = {n: r for n, r in pairs if r is not None}
    timed_out = [n for n, r in pairs if r is None]
    return results, timed_out

def main(scale=1.0):
    jobs = {"a": 1 * scale, "b": 0.5 * scale, "slow": 10 * scale, "c": 1.5 * scale, "d": 0.2 * scale}
    t0 = time.perf_counter()
    results, timed_out = asyncio.run(fetch_with_timeouts(jobs, timeout=2.0 * scale))
    took = time.perf_counter() - t0
    print(f"{len(results)} results, timed out: {timed_out}, took {took:.2f}s")
    return results, timed_out, took

if __name__ == "__main__":
    main()
