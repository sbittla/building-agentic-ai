"""Exercise A.3 (solution): run many at once, but never more than `limit`."""
import asyncio
import time

async def fetch_all(names, limit=3, seconds=1.0):
    sem = asyncio.Semaphore(limit)
    running, peak, t0 = 0, 0, time.perf_counter()

    async def one(name):
        nonlocal running, peak
        async with sem:                        # waits here if `limit` are already running
            running += 1
            peak = max(peak, running)
            print(f"{time.perf_counter() - t0:5.2f}s start  {name}  ({running} running)")
            await asyncio.sleep(seconds)
            running -= 1
            print(f"{time.perf_counter() - t0:5.2f}s finish {name}")
            return f"{name} ok"

    results = await asyncio.gather(*(one(n) for n in names))
    return results, peak, time.perf_counter() - t0

def main(seconds=1.0):
    names = [f"page{i}" for i in range(10)]
    print("prediction: 10 items, 3 at a time, 1 s each -> 4 rounds -> about 4 s")
    results, peak, total = asyncio.run(fetch_all(names, 3, seconds))
    print(f"peak concurrency {peak}, total {total:.2f}s, {len(results)} results")
    return results, peak, total

if __name__ == "__main__":
    main()
