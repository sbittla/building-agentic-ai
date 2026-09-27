"""Chapter 6: an agent that explores a folder of notes (sandboxed)."""
import re
from pathlib import Path

ROOT = Path("notes").resolve()          # the ONLY folder the agent may touch
MAX_LINES = 80                          # page size for read_file

def _safe(path: str) -> Path:
    """Resolve a user/model-supplied path and refuse anything outside ROOT."""
    p = (ROOT / path).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise PermissionError(f"'{path}' is outside the notes folder")
    return p

def list_files(subfolder: str = ".") -> str:
    base = _safe(subfolder)
    files = sorted(str(p.relative_to(ROOT)) for p in base.rglob("*")
                   if p.is_file() and not p.is_symlink())
    return "\n".join(files[:200]) or "(empty)"

def search_files(pattern: str, max_hits: int = 20) -> str:
    """Case-insensitive regex search. Returns file:line: text."""
    if len(pattern) > 200:
        return "ERROR: pattern too long (max 200 characters)."
    rx = re.compile(pattern, re.IGNORECASE)
    hits = []
    for p in sorted(ROOT.rglob("*")):
        # A symlink inside notes/ could point anywhere:
        # search only real files inside ROOT.
        if not p.is_file() or p.is_symlink() or ROOT not in p.resolve().parents:
            continue
        for n, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            if rx.search(line):
                hits.append(f"{p.relative_to(ROOT)}:{n}: {line.strip()[:160]}")
                if len(hits) >= max_hits:
                    return "\n".join(hits) + "\n(more hits truncated)"
    return "\n".join(hits) or "No matches."

def read_file(path: str, start_line: int = 1) -> str:
    lines = _safe(path).read_text(errors="ignore").splitlines()
    chunk = lines[start_line - 1: start_line - 1 + MAX_LINES]
    body = "\n".join(f"{i}: {l}" for i, l in enumerate(chunk, start_line))
    end = start_line + len(chunk) - 1
    more = (f"\n(lines {end + 1}-{len(lines)} not shown; call again with "
            f"start_line={end + 1})") if end < len(lines) else ""
    return body + more

REGISTRY = {"list_files": list_files, "search_files": search_files,
            "read_file": read_file}

TOOLS = [
    {"name": "list_files", "description": "List note files (paths relative to the "
     "notes folder).", "input_schema": {"type": "object", "properties": {
         "subfolder": {"type": "string"}}}},
    {"name": "search_files", "description": "Search all notes with a case-insensitive "
     "regex. Returns file:line: text. Start here for 'which note mentions X'.",
     "input_schema": {"type": "object", "properties": {
         "pattern": {"type": "string"}, "max_hits": {"type": "integer"}},
         "required": ["pattern"]}},
    {"name": "read_file", "description": f"Read up to {MAX_LINES} numbered lines of a "
     "note, starting at start_line.", "input_schema": {"type": "object",
         "properties": {"path": {"type": "string"}, "start_line": {"type": "integer"}},
         "required": ["path"]}},
]

SYSTEM = ("Answer questions using ONLY the user's notes. Search before reading. "
          "Cite every fact as (file:line). If the notes don't say, say so.")

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

if __name__ == "__main__":
    from ch04_agent import run_agent
    answer, _, stats = run_agent("Which of my notes mention Kafka, and what do they "
                                 "say about it?", TOOLS, run_tool, system=SYSTEM)
    print(answer, stats)
