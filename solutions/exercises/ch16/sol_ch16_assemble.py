"""Exercise 16.6 (solution): assemble() that keeps only the newest item per origin, drops
items whose refresh fails (with the reason in the report), and enforces a max_age."""
import time

from ch16_assemble import ContextItem, render, route, ROUTES  # noqa: F401  (same API)

def assemble(items, budget: int, refresh=None, now: float | None = None,
             max_age: float | None = None):
    now = now or time.time()
    report, fresh = [], []
    newest = {}                                     # 1. one item per origin: the newest
    for item in items:
        key = item.origin or id(item)
        if key in newest and newest[key].fetched_at >= item.fetched_at:
            report.append((item.source, item.origin, "dropped: older duplicate"))
            continue
        if key in newest:
            old = newest[key]
            report.append((old.source, old.origin, "dropped: older duplicate"))
        newest[key] = item
    for item in newest.values():
        if max_age is not None and item.age(now) > max_age and not item.pinned:
            report.append((item.source, item.origin, f"dropped: older than {max_age:.0f}s"))
            continue
        if item.is_stale(now):
            if not refresh:
                report.append((item.source, item.origin, "dropped: stale"))
                continue
            try:                                     # 2. a failed refresh drops the item
                item = refresh(item)
                report.append((item.source, item.origin, "refreshed (was stale)"))
            except Exception as exc:
                report.append((item.source, item.origin,
                               f"dropped: refresh failed ({type(exc).__name__})"))
                continue
        fresh.append(item)
    fresh.sort(key=lambda i: (not i.pinned, -i.priority, -i.fetched_at))
    chosen, used = [], 0
    for item in fresh:
        if item.pinned or used + item.tokens <= budget:
            chosen.append(item)
            used += item.tokens
            report.append((item.source, item.origin, f"included ({item.tokens} tokens)"))
        else:
            report.append((item.source, item.origin, f"dropped: over budget ({item.tokens} tokens)"))
    return chosen, report

if __name__ == "__main__":
    now = time.time()
    items = [ContextItem("orders", "#4471 in transit", origin="orders_api:4471", fetched_at=now - 60),
             ContextItem("orders", "#4471 out for delivery", origin="orders_api:4471", fetched_at=now - 5),
             ContextItem("crm", "Priya prefers email", origin="crm:19", fetched_at=now - 9_000)]
    chosen, report = assemble(items, 500, max_age=3_600)
    for row in report:
        print(row)
