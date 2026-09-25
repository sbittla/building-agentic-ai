"""The buggy version:   async def main(): r = fetch("x", 1); time.sleep(2); print(r)
Fix both bugs below, and explain each in a comment."""
import asyncio
import time
from i_async import fetch


async def main(pause=2.0):
    r = fetch("x", 1 * pause / 2)     # bug 1?
    time.sleep(pause)                 # bug 2?
    print(r)
    return r


if __name__ == "__main__":
    asyncio.run(main())
