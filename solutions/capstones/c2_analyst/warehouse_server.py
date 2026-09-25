"""Capstone 2: read-only warehouse over shop.db (the chapter 8 database)."""
import logging, re, sqlite3, sys
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
DB, MAX_ROWS = "shop.db", 100
mcp = MCPServer("warehouse")

def _con(seconds: float = 5):
    """Read-only at the source, closed after use, and stopped after `seconds`."""
    import contextlib, time
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    deadline = time.monotonic() + seconds
    con.set_progress_handler(lambda: time.monotonic() > deadline, 10_000)
    return contextlib.closing(con)

@mcp.tool()
def list_tables() -> str:
    """Table names with row counts."""
    with _con() as con:
        names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        return "\n".join(f"{n} ({con.execute(f'SELECT COUNT(*) FROM {n}').fetchone()[0]} rows)"
                         for n in names)

@mcp.tool()
def describe_table(table: str, columns: list[str] | None = None) -> str:
    """Columns of one table, optionally only the listed ones (column pruning), plus 3 sample rows."""
    if not re.fullmatch(r"\w+", table):
        raise ToolError("Invalid table name.")
    with _con() as con:
        cols = [(r[1], r[2]) for r in con.execute(f"PRAGMA table_info({table})")]
        if not cols:
            raise ToolError(f"No table {table}. Use list_tables.")
        if columns:
            cols = [c for c in cols if c[0] in columns]
        names = ", ".join(c[0] for c in cols)
        sample = con.execute(f"SELECT {names} FROM {table} LIMIT 3").fetchall()
    return "columns: " + ", ".join(f"{n} {t}" for n, t in cols) + "\nsample: " + repr(sample)

@mcp.tool()
def run_query(sql: str) -> str:
    """Run one read-only SQLite query (max 100 rows). On error, fix the SQL and retry."""
    try:
        with _con() as con:
            cur = con.execute(sql)
            cols = [c[0] for c in cur.description]
            rows = cur.fetchmany(MAX_ROWS + 1)
    except sqlite3.Error as e:
        raise ToolError(f"{e}. Check names with describe_table and retry.")
    out = [" | ".join(cols)] + [" | ".join(map(str, r)) for r in rows[:MAX_ROWS]]
    if len(rows) > MAX_ROWS:
        out.append(f"(truncated to {MAX_ROWS} rows)")
    return "\n".join(out)

@mcp.resource("warehouse://definitions")
def definitions() -> str:
    """Business definitions."""
    return ("Revenue = SUM(order_items.quantity * products.price) over orders with status != 'cancelled'.\n"
            "Active customer = at least one non-cancelled order in the last 90 days.")

if __name__ == "__main__":
    mcp.run(transport="stdio")
