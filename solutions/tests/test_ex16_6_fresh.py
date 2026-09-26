"""Exercise 16.6: newest per origin, failed refresh reported, max_age enforced."""
import time
from ch16_assemble import ContextItem
from sol_ch16_assemble import assemble

def test_duplicate_origin_keeps_the_newest():
    now = time.time()
    old = ContextItem("orders", "in transit", origin="orders:1", fetched_at=now - 60)
    new = ContextItem("orders", "delivered", origin="orders:1", fetched_at=now - 5)
    chosen, report = assemble([old, new], 500, now=now)
    assert [c.text for c in chosen] == ["delivered"]
    assert any("older duplicate" in r[2] for r in report)

def test_failed_refresh_is_dropped_with_reason():
    now = time.time()
    stale = ContextItem("orders", "old", origin="orders:2", fetched_at=now - 900, ttl=300)
    def broken(item):
        raise TimeoutError
    chosen, report = assemble([stale], 500, refresh=broken, now=now)
    assert chosen == [] and report == [("orders", "orders:2", "dropped: refresh failed (TimeoutError)")]

def test_max_age_drops_old_items_but_not_pinned():
    now = time.time()
    rule = ContextItem("policy", "rule", pinned=True, origin="p", fetched_at=now - 99_999)
    old = ContextItem("crm", "profile", origin="c", fetched_at=now - 9_000)
    chosen, report = assemble([rule, old], 500, now=now, max_age=3_600)
    assert [c.source for c in chosen] == ["policy"]
    assert ("crm", "c", "dropped: older than 3600s") in report
