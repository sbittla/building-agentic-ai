"""Chapter 8 reference solution: 8.5 (retry budget + query log) and 8.6 (confirm tables)."""
import json
import re
import time
import ch08_sql_tools as base
from ch08_sql_tools import get_schema

MAX_FAILED = 3
LOG = "query_log.jsonl"
state = {"failed": 0, "approved_tables": None}

def ask_user(prompt: str) -> str:                   # replaced in tests
    return input(prompt)

def propose_tables(tables: list[str], reason: str) -> str:
    """QueryGPT-style: the user confirms (or edits) the tables before any query runs."""
    known = set(re.findall(r"CREATE TABLE (\w+)", get_schema()))
    unknown = [t for t in tables if t not in known]
    if unknown:
        return f"ERROR: unknown tables {unknown}. Known: {sorted(known)}"
    reply = ask_user(f"\nThe agent wants to use tables {tables} ({reason}).\n"
                     "Press Enter to approve, or type the tables to use instead: ").strip()
    chosen = [t.strip() for t in reply.split(",") if t.strip()] if reply else tables
    state["approved_tables"] = set(chosen)
    return f"User approved tables: {chosen}"

def run_query(sql: str) -> str:
    if state["failed"] >= MAX_FAILED:
        return (f"ERROR: {MAX_FAILED} failed queries already. Stop querying and tell the "
                "user what went wrong.")
    if state["approved_tables"] is not None:
        used = set(re.findall(r"\b(?:from|join)\s+(\w+)", sql, re.I))
        extra = used - state["approved_tables"]
        if extra:
            return f"ERROR: tables {sorted(extra)} were not approved. Call propose_tables again."
    result = base.run_query(sql)
    ok = not result.startswith("ERROR")
    state["failed"] += 0 if ok else 1
    with open(LOG, "a") as f:
        f.write(json.dumps({"ts": time.time(), "sql": sql, "ok": ok,
                            "error": None if ok else result}) + "\n")
    return result

def new_question():
    state.update(failed=0, approved_tables=None)

REGISTRY = {"get_schema": get_schema, "propose_tables": propose_tables, "run_query": run_query}
TOOLS = [base.TOOLS[0], {
    "name": "propose_tables", "description": "Before writing SQL, propose the tables you "
    "plan to use and why. The user confirms or changes them.",
    "input_schema": {"type": "object", "properties": {
        "tables": {"type": "array", "items": {"type": "string"}}, "reason": {"type": "string"}},
        "required": ["tables", "reason"]}}, base.TOOLS[1]]
SYSTEM = base.SYSTEM + " Always call propose_tables before your first query."

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"
