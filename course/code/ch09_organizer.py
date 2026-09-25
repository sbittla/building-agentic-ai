"""Chapter 9: a file organizer that must get human approval before acting."""
import json
import shutil
import time
from pathlib import Path

ROOT = Path("messy").resolve()               # sandbox, as in chapter 6
AUDIT = Path("audit_log.jsonl")
CATEGORIES = {"images": {".jpg", ".jpeg", ".png", ".gif"},
              "documents": {".pdf", ".docx", ".txt", ".md"},
              "spreadsheets": {".xlsx", ".csv"},
              "archives": {".zip", ".tar", ".gz"}}
_plans: dict = {}                            # plan_id -> list of moves

def _safe(rel: str) -> Path:
    p = (ROOT / rel).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise PermissionError(f"'{rel}' is outside the sandbox")
    return p

def list_files() -> str:
    files = [str(p.relative_to(ROOT)) for p in ROOT.iterdir() if p.is_file()]
    return "\n".join(sorted(files)) or "(no loose files)"

def propose_moves() -> str:
    """READ-ONLY: build a plan grouping loose files by type. Moves nothing."""
    moves = []
    for p in sorted(ROOT.iterdir()):
        if not p.is_file():
            continue
        folder = next((c for c, exts in CATEGORIES.items()
                       if p.suffix.lower() in exts), "other")
        moves.append({"src": p.name, "dst": f"{folder}/{p.name}"})
    plan_id = f"plan-{len(_plans) + 1}"
    _plans[plan_id] = moves
    preview = "\n".join(f"  {m['src']!r} -> {m['dst']!r}" for m in moves[:30])
    more = f"\n  ... and {len(moves) - 30} more" if len(moves) > 30 else ""
    return f"{plan_id}: {len(moves)} moves\n{preview}{more}"

def _unique(dst: Path) -> Path:
    """Never overwrite: add ' (1)', ' (2)' ... when the name is taken."""
    n, candidate = 1, dst
    while candidate.exists():
        candidate = dst.with_name(f"{dst.stem} ({n}){dst.suffix}")
        n += 1
    return candidate

def apply_plan(plan_id: str) -> str:
    """WRITES FILES. Only runs after the human approves (see run_tool)."""
    moves = _plans.get(plan_id)
    if moves is None:
        return f"ERROR: unknown plan {plan_id}. Call propose_moves first."
    done = 0
    with AUDIT.open("a") as log:
        for m in moves:
            src, dst = _safe(m["src"]), _unique(_safe(m["dst"]))
            if not src.exists():
                continue
            new_dirs = [str(d) for d in reversed(dst.parents) if ROOT in d.parents and not d.exists()]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dst)
            log.write(json.dumps({"ts": time.time(), "plan": plan_id, "src": str(src),
                                  "dst": str(dst), "created_dirs": new_dirs}) + "\n")
            done += 1
    return f"Moved {done} files. Undo is available with undo_plan('{plan_id}')."

def undo_plan(plan_id: str) -> str:
    """Reverse a plan using the audit log, newest move first."""
    if not AUDIT.exists():
        return "Nothing to undo."
    entries = [json.loads(l) for l in AUDIT.read_text().splitlines()]
    undone = 0
    for e in reversed([e for e in entries if e["plan"] == plan_id]):
        dst, src = Path(e["dst"]), Path(e["src"])
        if dst.exists() and not src.exists():
            shutil.move(dst, src)
            undone += 1
        for d in reversed(e.get("created_dirs", [])):     # remove folders the plan created,
            d = Path(d)                                    # but only if they're empty again
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
    return f"Restored {undone} files from {plan_id}."

REGISTRY = {"list_files": list_files, "propose_moves": propose_moves,
            "apply_plan": apply_plan, "undo_plan": undo_plan}
NEEDS_APPROVAL = {"apply_plan", "undo_plan"}   # anything that changes the disk

TOOLS = [
    {"name": "list_files", "description": "List loose files in the folder.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "propose_moves", "description": "Create a plan (read-only) that groups "
     "files into folders by type. Always show the plan to the user.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "apply_plan", "description": "Carry out a plan. The user will be asked "
     "to approve it; if they decline, stop and ask what to change.",
     "input_schema": {"type": "object", "properties": {"plan_id": {"type": "string"}},
                      "required": ["plan_id"]}},
    {"name": "undo_plan", "description": "Undo a previously applied plan.",
     "input_schema": {"type": "object", "properties": {"plan_id": {"type": "string"}},
                      "required": ["plan_id"]}},
]

def ask_human(name: str, args: dict) -> bool:
    """The approval gate lives in CODE, not in the prompt. The model can't skip it."""
    if name == "apply_plan":                # show EVERY move; !r escapes odd characters,
        for m in _plans.get(args.get("plan_id"), []):   # so a newline in a name can't hide one
            print(f"   {m['src']!r} -> {m['dst']!r}")
    reply = input(f"\nAPPROVE {name}({args})? [y/N] ").strip().lower()
    return reply == "y"

def run_tool(name, args):
    try:
        if name in NEEDS_APPROVAL and not ask_human(name, args):
            return "DECLINED: the user did not approve this action. Nothing changed."
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

if __name__ == "__main__":
    from ch04_agent import run_agent
    answer, _, _ = run_agent("Tidy up my messy folder by file type.", TOOLS, run_tool,
                             system="You organize files. Propose before acting.")
    print(answer)
