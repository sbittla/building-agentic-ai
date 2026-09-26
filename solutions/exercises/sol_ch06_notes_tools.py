"""Exercise 6.5 (Medium): find notes by file name and modification date."""
import fnmatch
from datetime import date, datetime
import ch06_notes_tools as base
from ch06_notes_tools import ROOT

def find_files(name_pattern: str = "*", modified_after: str | None = None,
               modified_before: str | None = None) -> str:
    """Glob on the path, plus a date window. Dates are YYYY-MM-DD. A date in the file
    name (YYYY-MM-DD-...) wins over the file system time, since copies reset mtimes."""
    lo = date.fromisoformat(modified_after) if modified_after else date.min
    hi = date.fromisoformat(modified_before) if modified_before else date.max
    hits = []
    for p in sorted(ROOT.rglob("*")):
        rel = str(p.relative_to(ROOT))
        if not p.is_file() or not fnmatch.fnmatch(rel.lower(), f"*{name_pattern.lower()}*"
                                                 if "*" not in name_pattern else name_pattern.lower()):
            continue
        try:
            d = date.fromisoformat(p.name[:10])
        except ValueError:
            d = datetime.fromtimestamp(p.stat().st_mtime).date()
        if lo <= d <= hi:
            hits.append(f"{rel} ({d})")
    return "\n".join(hits[:100]) or "No matching files."

REGISTRY = {**base.REGISTRY, "find_files": find_files}
TOOLS = base.TOOLS + [{
    "name": "find_files",
    "description": "Find notes by name pattern and date window (YYYY-MM-DD). Use for "
                   "'last month', 'in July', 'recent' questions, then search_files/read_file.",
    "input_schema": {"type": "object", "properties": {
        "name_pattern": {"type": "string", "description": "glob like *kafka* or *"},
        "modified_after": {"type": "string"}, "modified_before": {"type": "string"}}}}]
SYSTEM = base.SYSTEM + " For time-bounded questions, call find_files with a date window first."

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"
