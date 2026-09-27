"""Exercise A.2 (solution): two async bugs, fixed.

    async def main(): r = fetch("x", 1); time.sleep(2); print(r)

Bug 1: `fetch("x", 1)` without `await` only creates a coroutine object; nothing runs,
       `r` prints as <coroutine ...>, and Python warns "coroutine was never awaited".
Bug 2: `time.sleep(2)` blocks the whole event loop: nothing else can run for 2 s.
       Inside async code use `await asyncio.sleep(2)` (or asyncio.to_thread for
       blocking library calls)."""
import asyncio
from i_async import fetch

async def main(pause=2.0):
    r = await fetch("x", 1 * pause / 2)
    await asyncio.sleep(pause)
    print(r)
    return r

if __name__ == "__main__":
    asyncio.run(main())
