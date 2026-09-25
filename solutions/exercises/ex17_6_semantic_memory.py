"""Exercise 17.6 (solution): chapter 16's memory, found by meaning as well as by words.

Facts live in SQLite with their embedding. recall() ranks by vector similarity AND by
BM25 keywords, fused as in chapter 17, so "temperature units" finds "Srini prefers
Celsius" (meaning) and "ERR-4471" still finds the exact code (keywords)."""
import json
import sqlite3
import time
from pathlib import Path
import numpy as np
from ch17_rag import BM25, get_embedder

DB = Path("semantic_memory.db")
_embedder = None

def embedder():
    global _embedder
    if _embedder is None:
        _embedder = get_embedder()
    return _embedder

def _con():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, fact TEXT UNIQUE, "
                "tags TEXT, created TEXT, embedder TEXT, vector BLOB)")
    return con

def remember(fact: str, tags: str = "") -> str:
    vec = embedder().embed([fact])[0].astype(np.float32)
    with _con() as con:
        dup = con.execute("SELECT id FROM memories WHERE fact = ?", (fact,)).fetchone()
        if dup:
            return f"Already remembered (#{dup[0]})."
        cur = con.execute("INSERT INTO memories (fact, tags, created, embedder, vector) "
                          "VALUES (?, ?, ?, ?, ?)", (fact, tags, time.strftime("%Y-%m-%d"),
                                                     embedder().name, vec.tobytes()))
        return f"Remembered #{cur.lastrowid}."

def recall(query: str, limit: int = 3) -> str:
    with _con() as con:
        rows = con.execute("SELECT id, fact, tags, created, embedder, vector FROM memories").fetchall()
    rows = [r for r in rows if r[4] == embedder().name]      # never mix embedders
    if not rows:
        return "No memories match."
    vectors = np.stack([np.frombuffer(r[5], dtype=np.float32) for r in rows])
    q = embedder().embed([query], input_type="query")[0]
    sims = vectors @ q
    kw = BM25([f"{r[1]} {r[2]}" for r in rows]).scores(query)
    fused = {}
    for ranks in (list(np.argsort(-sims)), list(np.argsort(-kw))):
        for rank, i in enumerate(ranks):
            fused[i] = fused.get(i, 0) + 1 / (60 + rank)
    order = sorted(fused, key=lambda i: -fused[i])
    # drop results that match neither by meaning nor by words
    best = [i for i in order if sims[i] > 0.2 or kw[i] > 0][:limit]
    if not best:
        return "No memories match."
    return json.dumps([{"id": rows[i][0], "fact": rows[i][1], "tags": rows[i][2],
                        "date": rows[i][3]} for i in best])

def forget(memory_id: int) -> str:
    with _con() as con:
        n = con.execute("DELETE FROM memories WHERE id = ?", (memory_id,)).rowcount
    return f"Forgot #{memory_id}." if n else f"No memory #{memory_id}."

import ch16_memory as _m                                     # same tools, same prompt
TOOLS, SYSTEM = _m.TOOLS, _m.SYSTEM
REGISTRY = {"remember": remember, "recall": recall, "forget": forget}

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

def main():
    for fact in ["Srini prefers Celsius", "The payments error to watch is ERR-4471",
                 "Srini's manager is Asha", "Srini runs 5 km on Mondays"]:
        print(remember(fact))
    print(f"embedder = {embedder().name}")
    for q in ["temperature units", "who is my boss", "exercise routine", "ERR-4471", "Celsius"]:
        print(f"{q!r:22} -> {recall(q, limit=1)}")

if __name__ == "__main__":
    main()
