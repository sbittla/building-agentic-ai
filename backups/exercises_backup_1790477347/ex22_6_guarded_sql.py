"""Exercise 22.6 (solution): the Chapter 8 analyst as a hybrid. The model writes SQL;
SQLite's authorizer, not the prompt, decides what that SQL may do. Business definitions
come from a file your team maintains."""
import sqlite3
from pathlib import Path

import ch08_sql_tools as base

ALLOWED_TABLES = {"customers", "products", "orders", "order_items"}
ALLOWED_FUNCTIONS = {"count", "sum", "avg", "min", "max", "round", "strftime", "date",
                     "lower", "upper", "coalesce", "abs", "substr", "length", "total"}
MAX_ROWS = 50
DEFINITIONS = Path("definitions.md")
DEFAULT_DEFINITIONS = ("- Revenue: quantity * price over order_items joined to products, "
                       "for orders whose status is not 'cancelled'.\n"
                       "- Active customer: a customer with an order in the last 90 days.\n")

def authorizer(action, arg1, arg2, db_name, trigger):
    """Called by SQLite for every step the statement would take."""
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ:
        return sqlite3.SQLITE_OK if arg1 in ALLOWED_TABLES else sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION:
        return sqlite3.SQLITE_OK if (arg2 or "").lower() in ALLOWED_FUNCTIONS \
            else sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_DENY          # writes, ATTACH, PRAGMA, temp tables...

def run_query(sql: str) -> str:
    con = sqlite3.connect(base.DB_PATH)
    con.set_authorizer(authorizer)
    try:
        rows = con.execute(sql).fetchmany(MAX_ROWS + 1)
    except sqlite3.DatabaseError as exc:
        return f"ERROR: {exc} (only reads of {sorted(ALLOWED_TABLES)} are allowed)"
    finally:
        con.close()
    more = len(rows) > MAX_ROWS
    return "\n".join(map(str, rows[:MAX_ROWS])) + ("\n(more rows cut)" if more else "")

def system_prompt() -> str:
    if not DEFINITIONS.exists():
        DEFINITIONS.write_text(DEFAULT_DEFINITIONS)
    return (base.SYSTEM.split("Revenue =")[0] + "Use these definitions exactly:\n"
            + DEFINITIONS.read_text())

def run_tool(name, args):
    return run_query(args["sql"]) if name == "run_query" else base.run_tool(name, args)

TOOLS = base.TOOLS

if __name__ == "__main__":
    from ch04_agent import run_agent
    print(run_query("DELETE FROM orders"))
    print(run_agent("What was total revenue?", TOOLS, run_tool, system=system_prompt())[0])
