import asyncio
import time
from i_async import fetch      # fetch(name, seconds) waits `seconds`, then returns

DURATIONS = [1, 2, 1, 3, 1]


async def sequential(durations, scale=1.0) -> float:
    """Await each fetch one after another; return the seconds it took."""
    t0 = time.perf_counter()
    # TODO: for each duration d: await fetch(f"item{i}", d * scale)
    return time.perf_counter() - t0


async def together(durations, scale=1.0) -> float:
    """Run all fetches at once with asyncio.gather; return the seconds it took."""
    t0 = time.perf_counter()
    # TODO: await asyncio.gather(...)
    return time.perf_counter() - t0


if __name__ == "__main__":
    print("my prediction: sequential = ?s, gather = ?s")
    print(asyncio.run(sequential(DURATIONS)), asyncio.run(together(DURATIONS)))
