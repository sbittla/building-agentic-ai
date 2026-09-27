"""Interlude (async): doing several slow things at the same time."""
import asyncio
import time

async def fetch(name: str, seconds: float) -> str:
    """Pretend to call a slow API. `await` lets other work run while we wait."""
    await asyncio.sleep(seconds)
    return f"{name} done after {seconds}s"

async def one_after_another():
    t0 = time.perf_counter()
    a = await fetch("weather", 1)
    b = await fetch("news", 1)
    return [a, b], time.perf_counter() - t0

async def at_the_same_time():
    t0 = time.perf_counter()
    results = await asyncio.gather(fetch("weather", 1), fetch("news", 1))
    return results, time.perf_counter() - t0

def slow_blocking_call() -> str:          # e.g. a library that isn't async
    time.sleep(1)
    return "blocking call done"

async def with_blocking_code():
    t0 = time.perf_counter()
    results = await asyncio.gather(asyncio.to_thread(slow_blocking_call),
                                   fetch("news", 1))
    return results, time.perf_counter() - t0

async def with_a_timeout():
    try:
        return await asyncio.wait_for(fetch("very slow", 5), timeout=0.5)
    except asyncio.TimeoutError:
        return "gave up after 0.5s"

async def main():
    for label, coro in [("sequential", one_after_another()),
                        ("gather", at_the_same_time()),
                        ("to_thread", with_blocking_code())]:
        results, seconds = await coro
        print(f"{label:<10} {seconds:.1f}s  {results}")
    print("timeout   ", await with_a_timeout())

if __name__ == "__main__":
    asyncio.run(main())        # the one place where async code starts
