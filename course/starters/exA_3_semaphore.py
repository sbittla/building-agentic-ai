import asyncio
import time


async def fetch_all(names, limit=3, seconds=1.0):
    """Fetch every name (each takes `seconds`), never more than `limit` at once.
    Return (results, peak, total_seconds): peak = the most that ran at the same time."""
    sem = asyncio.Semaphore(limit)
    running, peak, t0 = 0, 0, time.perf_counter()

    async def one(name):
        nonlocal running, peak
        # TODO: async with sem: count running/peak, await asyncio.sleep(seconds), return a result
        raise NotImplementedError

    results = await asyncio.gather(*(one(n) for n in names))
    return results, peak, time.perf_counter() - t0


if __name__ == "__main__":
    print(asyncio.run(fetch_all([f"page{i}" for i in range(10)])))
