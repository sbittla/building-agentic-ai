"""Capstone 2: natural-language data analyst with table confirmation."""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from common import server, chat, CapstonePolicy

CONFIG = {"servers": dict([server("warehouse", "c2_analyst/warehouse_server.py"),
                           server("charts", "c2_analyst/charts_server.py")])}
RULES = {"allow": {"warehouse": ["*"], "charts": ["*"]},
         "needs_approval": ["warehouse__run_query"]}
SYSTEM = """You are a data analyst for the shop database (read-only).
1. list_tables, then describe_table with only the columns you need.
2. Write SQLite SQL; on an error, read it and fix the query.
3. Answer with the numbers, then show the final SQL in a ```sql block.
4. If the user asks for a chart, call make_chart with a two-column query.
Revenue excludes cancelled orders."""

class TableConfirmation:
    """QueryGPT-style: the first query touching a new set of tables needs the user's OK."""
    def __init__(self, ask=input):
        self.approved, self.ask = set(), ask

    def __call__(self, name, args):
        tables = set(re.findall(r"\b(?:from|join)\s+(\w+)", args.get("sql", ""), re.I))
        new = tables - self.approved
        if not new:
            return True
        ok = self.ask(f"\nThe query uses tables {sorted(tables)}. OK? [Y/n] ").strip().lower() in ("", "y")
        if ok:
            self.approved |= tables
        return ok

if __name__ == "__main__":
    confirm = TableConfirmation()
    chat(CONFIG, SYSTEM, RULES, approver=confirm)
