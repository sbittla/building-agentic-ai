"""Capstone 2: natural-language data analyst with table confirmation."""
import os
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
        sql = args.get("sql", "")
        ctes = set(re.findall(r"(?:with|,)\s*(\w+)\s+as\s*\(", sql, re.I))   # names the query defines
        tables = set(re.findall(r"\b(?:from|join)\s+(\w+)", sql, re.I)) - ctes
        new = tables - self.approved
        if not new:
            return True
        ok = self.ask(f"\nThe query uses tables {sorted(tables)}. OK? [Y/n] ").strip().lower() in ("", "y")
        if ok:
            self.approved |= tables
        return ok

def unattended(prompt: str) -> str:
    """For automated runs (CAPSTONE_AUTO_APPROVE=1 and no terminal): say yes, visibly, so
    the approval prompt never reads the next question from stdin as its answer."""
    print(prompt + "y  (auto-approved: CAPSTONE_AUTO_APPROVE)")
    return "y"

if __name__ == "__main__":
    auto = os.environ.get("CAPSTONE_AUTO_APPROVE") == "1" and not sys.stdin.isatty()
    confirm = TableConfirmation(ask=unattended if auto else input)
    chat(CONFIG, SYSTEM, RULES, approver=confirm)
