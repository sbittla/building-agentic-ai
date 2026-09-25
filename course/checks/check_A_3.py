import asyncio

def test_limit(ex):
    results, peak, total = asyncio.run(ex.fetch_all([f"p{i}" for i in range(10)], limit=3, seconds=0.05))
    assert len(results) == 10
    assert peak == 3, f"at most 3 at a time, and 3 should run together; peak was {peak}"
    assert 0.18 < total < 0.35, f"10 items, 3 at a time: 4 rounds x 0.05 s = 0.2 s, got {total:.2f}"
