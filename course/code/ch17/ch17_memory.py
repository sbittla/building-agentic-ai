"""Chapter 17: a first long-term memory the agent can write to and search
(SQLite FTS5). Section 17.3 starts here; ch17_memory_policy.py adds kinds, scopes,
expiry and a write gate."""
import contextlib
import json
import sqlite3
import time
from pathlib import Path

DB = Path("memory.db")

@contextlib.contextmanager
def _con():
    """Open, commit on success, and always CLOSE. (`with sqlite3.connect(...)` alone
    commits but leaves the connection open, which leaks file handles in a long-running
    agent.)"""
    con = sqlite3.connect(DB)
    try:
        con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS memories USING "
                    "fts5(fact, tags, created UNINDEXED, tokenize='porter')")
        yield con
        con.commit()
    finally:
        con.close()

def remember(fact: str, tags: str = "") -> str:
    with _con() as con:
        dup = con.execute("SELECT rowid FROM memories WHERE fact = ?",
                          (fact,)).fetchone()
        if dup:
            return f"Already remembered (#{dup[0]})."
        cur = con.execute("INSERT INTO memories VALUES (?, ?, ?)",
                          (fact, tags, time.strftime("%Y-%m-%d")))
        return f"Remembered #{cur.lastrowid}."

def recall(query: str, limit: int = 5) -> str:
    """Full-text search, best matches first. Words are ORed so partial matches count."""
    words = [w for w in "".join(ch if ch.isalnum() else " " for ch in query).split()
             if len(w) > 2]
    if not words:
        return "No memories match."
    with _con() as con:
        rows = con.execute("SELECT rowid, fact, tags, created FROM memories "
                           "WHERE memories MATCH ? ORDER BY rank LIMIT ?",
                           (" OR ".join(f'"{w}"' for w in words), limit)).fetchall()
    return json.dumps([{"id": r[0], "fact": r[1], "tags": r[2], "date": r[3]}
                       for r in rows]) if rows else "No memories match."

def forget(memory_id: int) -> str:
    with _con() as con:
        n = con.execute("DELETE FROM memories WHERE rowid = ?", (memory_id,)).rowcount
    return f"Forgot #{memory_id}." if n else f"No memory #{memory_id}."

REGISTRY = {"remember": remember, "recall": recall, "forget": forget}
TOOLS = [
    {"name": "remember", "description": "Save a durable fact about the user or "
     "their work (preferences, decisions, names, deadlines). Not for small talk "
     "or passing details.",
     "input_schema": {"type": "object", "properties": {"fact": {"type": "string"},
                      "tags": {"type": "string"}}, "required": ["fact"]}},
    {"name": "recall", "description": "Search saved facts. Call this at the start of a "
     "conversation and whenever the user refers to something from before.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}},
                      "required": ["query"]}},
    {"name": "forget", "description": "Delete a saved fact by id when the user asks.",
     "input_schema": {"type": "object",
                      "properties": {"memory_id": {"type": "integer"}},
                      "required": ["memory_id"]}},
]
SYSTEM = ("You are a personal assistant with long-term memory. Recall relevant "
          "memories before answering. Remember only durable facts the user states; "
          "never remember passwords, card numbers or health details. If the user asks "
          "you to forget something, do it.")

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

if __name__ == "__main__":
    from ch04_agent import run_agent
    history = []
    while (q := input("You: ").strip()) not in ("", "quit", "exit"):
        answer, history, _ = run_agent(q, TOOLS, run_tool, system=SYSTEM,
                                       messages=history)
        print("Agent:", answer)
