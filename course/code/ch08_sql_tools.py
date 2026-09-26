"""Chapter 8: a self-correcting SQL analyst over a READ-ONLY connection."""
import contextlib
import sqlite3
import time

DB_PATH = "shop.db"
MAX_ROWS = 50
# read-only doesn't mean harmless: a bad join can run for hours
QUERY_SECONDS = 5

def _connect(deadline_s: float = QUERY_SECONDS):
    # mode=ro: the database itself refuses writes, whatever the model sends.
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    deadline = time.monotonic() + deadline_s
    # SQLite calls this every 10,000 steps; returning True cancels the query.
    con.set_progress_handler(lambda: time.monotonic() > deadline, 10_000)
    return contextlib.closing(con)         # "with" then CLOSES the connection

def get_schema() -> str:
    with _connect() as con:
        rows = con.execute("SELECT sql FROM sqlite_master "
                           "WHERE type='table'").fetchall()
    return "\n".join(r[0] for r in rows)

def run_query(sql: str) -> str:
    if not sql.lstrip().lower().startswith(("select", "with")):
        return "ERROR: only SELECT queries are allowed."
    try:
        with _connect() as con:
            cur = con.execute(sql)
            cols = [c[0] for c in cur.description]
            rows = cur.fetchmany(MAX_ROWS + 1)
    except sqlite3.OperationalError as e:
        if "interrupted" in str(e):
            return (f"ERROR: the query ran longer than {QUERY_SECONDS} s "
                    "and was stopped. Add filters, join on keys, or aggregate first.")
        return f"ERROR: {e}. Check table/column names with get_schema and retry."
    except sqlite3.Error as e:
        # The exact database error is the most useful thing for self-correction.
        return f"ERROR: {e}. Check table/column names with get_schema and retry."
    lines = [" | ".join(cols)] + [" | ".join(map(str, r)) for r in rows[:MAX_ROWS]]
    if len(rows) > MAX_ROWS:
        lines.append(f"(truncated to {MAX_ROWS} rows; add LIMIT or aggregate)")
    return "\n".join(lines)

REGISTRY = {"get_schema": get_schema, "run_query": run_query}
TOOLS = [
    {"name": "get_schema", "description": "Return CREATE TABLE statements for every "
     "table. Call this before writing any SQL.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "run_query", "description": f"Run one read-only SQLite SELECT. Returns up "
     f"to {MAX_ROWS} rows. If it returns an ERROR, fix the SQL and try again.",
     "input_schema": {"type": "object", "properties": {"sql": {"type": "string"}},
                      "required": ["sql"]}},
]
SYSTEM = ("You are a data analyst. Look at the schema, write SQLite SQL, run it, "
          "and answer with the numbers. Revenue = quantity * price for orders "
          "that are not cancelled. Show the final SQL you used.")

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

if __name__ == "__main__":
    from ch04_agent import run_agent
    answer, _, s = run_agent("Who are the top 5 customers by revenue?",
                             TOOLS, run_tool, system=SYSTEM)
    print(answer, s)
