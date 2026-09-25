import asyncio
from i_async import fetch


async def fetch_with_timeouts(jobs: dict, timeout=2.0):
    """jobs = {name: seconds}. Fetch all at once, each with its own timeout.
    Return (results, timed_out): results = {name: result} for the ones that finished,
    timed_out = [names] that didn't."""
    # TODO: asyncio.wait_for(fetch(name, s), timeout) inside try/except asyncio.TimeoutError
    raise NotImplementedError


if __name__ == "__main__":
    print(asyncio.run(fetch_with_timeouts({"a": 1, "slow": 10, "b": 0.5})))
