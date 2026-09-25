import asyncio, time

def test_timeouts(ex):
    t0 = time.perf_counter()
    results, timed_out = asyncio.run(ex.fetch_with_timeouts(
        {"a": 0.05, "b": 0.02, "slow": 1.0, "c": 0.07, "d": 0.01}, timeout=0.1))
    took = time.perf_counter() - t0
    assert timed_out == ["slow"] and len(results) == 4
    assert took < 0.5, f"should finish at the timeout (~0.1 s), not wait for the slow one: {took:.2f}s"
