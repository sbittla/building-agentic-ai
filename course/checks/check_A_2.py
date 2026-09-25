import asyncio, time

def test_fixed(ex, monkeypatch):
    def forbidden(*a):
        raise AssertionError("time.sleep blocks the event loop: use await asyncio.sleep")
    monkeypatch.setattr(time, "sleep", forbidden)
    r = asyncio.run(ex.main(pause=0.05))
    assert isinstance(r, str) and "done" in r, "await the fetch to get its result, not a coroutine"
