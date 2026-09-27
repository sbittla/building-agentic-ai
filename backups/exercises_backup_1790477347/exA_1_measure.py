"""Exercise A.1 (solution): predict, then measure, sequential vs gather."""
import asyncio
import time
from i_async import fetch

DURATIONS = [1, 2, 1, 3, 1]

async def sequential(durations, scale=1.0):
    t0 = time.perf_counter()
    for i, d in enumerate(durations):
        await fetch(f"item{i}", d * scale)
    return time.perf_counter() - t0

async def together(durations, scale=1.0):
    t0 = time.perf_counter()
    await asyncio.gather(*(fetch(f"item{i}", d * scale) for i, d in enumerate(durations)))
    return time.perf_counter() - t0

def main(scale=1.0):
    print(f"prediction: sequential = sum = {sum(DURATIONS)}s, gather = max = {max(DURATIONS)}s")
    s = asyncio.run(sequential(DURATIONS, scale))
    g = asyncio.run(together(DURATIONS, scale))
    print(f"measured:   sequential = {s:.2f}s, gather = {g:.2f}s")
    return s, g

if __name__ == "__main__":
    main()
