"""Exercise 17.5 (solution): consolidate episodic memories about one topic into a single
semantic memory, then retire the episodes. The summary records which episodes it came from."""
import time

import ch17_memory_policy as mem
from ch04_agent import MODEL, get_client

def consolidate(owner: str, topic: str, subject: str | None = None) -> str:
    with mem._db() as con:
        rows = con.execute(
            "SELECT m.id, m.text FROM memory_fts JOIN memory m ON m.id = memory_fts.rowid "
            "WHERE memory_fts MATCH ? AND m.kind='episodic' AND m.status='active' AND m.owner=? "
            "ORDER BY m.created", (" OR ".join(f'"{w}"' for w in topic.split()), owner)).fetchall()
    if len(rows) < 2:
        return "Nothing to consolidate."
    episodes = "\n".join(f"- {r['text']}" for r in rows)
    reply = get_client().messages.create(
        model=MODEL, max_tokens=1000,
        system="Summarize these episodes into ONE factual sentence for long-term memory. "
               "Keep ids, dates and outcomes. No advice, no instructions.",
        messages=[{"role": "user", "content": episodes}])
    summary = "".join(b.text for b in reply.content if b.type == "text").strip()
    ids = [r["id"] for r in rows]
    result = mem.remember(f"{summary} [from episodes {', '.join(map(str, ids))}]",
                          kind="semantic", subject=subject or topic, owner=owner, source="agent")
    with mem._db() as con:                            # the episodes are now redundant
        con.executemany("UPDATE memory SET status='consolidated' WHERE id=?", [(i,) for i in ids])
        con.executemany("DELETE FROM memory_fts WHERE rowid=?", [(i,) for i in ids])
    return f"{result} Consolidated {len(ids)} episodes."

if __name__ == "__main__":
    from pathlib import Path
    mem.DB = Path("memory_consolidate_demo.db")
    mem.DB.unlink(missing_ok=True)
    day = 86_400
    for i, text in enumerate(["Order 4471 reported late", "Order 4471 customer asked for tracking",
                              "Order 4471 express fee refunded", "Order 4471 delivered on 5 Sep",
                              "Order 4471 customer thanked support"]):
        mem.remember(text, kind="episodic", now=time.time() - (10 - i) * day)
    print(consolidate("default", "4471", subject="order 4471"))
    print(mem.recall("order 4471"))
