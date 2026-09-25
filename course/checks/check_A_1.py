import asyncio

def test_timing(ex):
    s = asyncio.run(ex.sequential([1, 2, 1, 3, 1], scale=0.05))
    g = asyncio.run(ex.together([1, 2, 1, 3, 1], scale=0.05))
    assert 0.35 < s < 0.6, f"one after another: 8 x 0.05 = 0.4 s, got {s:.2f}"
    assert 0.12 < g < 0.25, f"with gather: the longest, 3 x 0.05 = 0.15 s, got {g:.2f}"
