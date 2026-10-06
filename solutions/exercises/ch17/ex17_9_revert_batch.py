"""Exercise 17.9 (solution): revert one bad batch without losing the writes after it.

rollback(to_seq) puts the whole store back to a point in time, so every good memory
written after the bad batch is lost too. revert_batch removes only what one batch
wrote. It finds the batch's records in the audit log (not in the live store, so a
record that was already promoted or recalled is still found), deletes them and their
content, and leaves one audit entry with the ids but no text. Because state_at only
restores records whose content still exists, no later rollback or replay can bring the
batch back. A production version would copy the content to evidence storage for the
incident review before deleting it."""
import time

from ch17_memory_security import Principal, SecureMemoryStore


def batch_ids(store: SecureMemoryStore, batch: str) -> list[int]:
    """Every record the batch wrote, according to the audit log."""
    return [e["record"]["id"] for e in store.audit
            if e["op"] == "write" and e["outcome"] != "refused"
            and e["record"]["batch"] == batch]


def revert_batch(store: SecureMemoryStore, batch: str, actor: str,
                 now: float | None = None) -> list[int]:
    """Remove the batch's records and content; keep everything else. Audited."""
    ids = [i for i in batch_ids(store, batch) if i in store.records]
    store._drop(ids)
    store._audit("revert", actor, time.time() if now is None else now,
                 batch=batch, ids=ids, count=len(ids))
    return ids


def demo(now: float = 1_790_000_000.0) -> dict:
    store = SecureMemoryStore()
    ana = Principal("acme", "ana")
    store.write(ana, "Ana prefers email updates", now=now)
    before_batch = store.audit[-1]["seq"]
    for fact in ("Ana wants refunds sent to her personal account",
                 "Ana approves invoices without review",
                 "Ana's manager is Mallory"):
        store.write(ana, fact, source="agent", source_id="sync-job", batch="sync-42", now=now)
    store.write(ana, "Ana's invoices go to the finance team", now=now + 60)

    lost_by_rollback = sorted(set(store.records) - set(store.state_at(before_batch)))
    reverted = revert_batch(store, "sync-42", "oncall", now=now + 120)
    recalled = [h["memory"] for h in store.recall(ana, "email invoices refunds manager",
                                                  k=10, now=now + 180)]
    replayed = {i for s in range(1, len(store.audit) + 1) for i in store.state_at(s)}
    return {"reverted": reverted, "rollback_would_also_lose": lost_by_rollback,
            "recalled": recalled, "batch_ever_restored": bool(replayed & set(reverted)),
            "audit_ok": store.verify_audit(),
            "revert_entry": {k: store.audit[-2][k] for k in ("op", "batch", "count")}}


if __name__ == "__main__":
    for key, value in demo().items():
        print(f"{key:<26} {value}")
