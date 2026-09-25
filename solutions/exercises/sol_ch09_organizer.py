"""Chapter 9 reference solution: 9.5 (partial approval), 9.6 (by date), 9.7 (policy)."""
import json
from datetime import datetime
from pathlib import Path
import ch09_organizer as base
from ch09_organizer import ROOT, _plans, list_files, apply_plan, undo_plan

def propose_by_date() -> str:
    """READ-ONLY: group photos into YYYY/MM folders by modification time."""
    moves = []
    for p in sorted(ROOT.iterdir()):
        if p.is_file() and p.suffix.lower() in base.CATEGORIES["images"]:
            d = datetime.fromtimestamp(p.stat().st_mtime)
            moves.append({"src": p.name, "dst": f"photos/{d:%Y}/{d:%m}/{p.name}"})
    plan_id = f"plan-{len(_plans) + 1}"
    _plans[plan_id] = moves
    return f"{plan_id}: {len(moves)} moves\n" + "\n".join(
        f"  {m['src']} -> {m['dst']}" for m in moves[:30])

def parse_selection(text: str, n: int) -> list[int]:
    """'all' | 'none' | '1,3,5-8' (1-based) -> sorted 0-based indexes."""
    text = text.strip().lower()
    if text in ("all", "y", "yes"):
        return list(range(n))
    if text in ("", "none", "n", "no"):
        return []
    picked = set()
    for part in text.replace(" ", "").split(","):
        if "-" in part:
            a, b = part.split("-")
            picked.update(range(int(a), int(b) + 1))
        else:
            picked.add(int(part))
    return sorted(i - 1 for i in picked if 1 <= i <= n)

POLICY_FILE = Path("policy_organizer.json")
DEFAULT_POLICY = {"max_auto_moves": 20, "auto_categories": ["images"],
                  "forbidden_extensions": [".exe", ".sh", ".bat"]}

def policy_decision(moves: list[dict]) -> str:
    """'auto' (no human needed), 'ask' or 'block', decided by a reviewable file."""
    policy = json.loads(POLICY_FILE.read_text()) if POLICY_FILE.exists() else DEFAULT_POLICY
    if any(Path(m["src"]).suffix.lower() in policy["forbidden_extensions"] for m in moves):
        return "block"
    if len(moves) <= policy["max_auto_moves"] and all(
            m["dst"].split("/")[0] in policy["auto_categories"] for m in moves):
        return "auto"
    return "ask"

def ask_human(prompt: str) -> str:                   # replaced in tests
    return input(prompt)

def gated_apply(plan_id: str) -> str:
    moves = _plans.get(plan_id)
    if moves is None:
        return f"ERROR: unknown plan {plan_id}. Propose a plan first."
    decision = policy_decision(moves)
    if decision == "block":
        return "BLOCKED by policy: the plan touches a forbidden file type. Nothing changed."
    if decision == "ask":
        for i, m in enumerate(moves, 1):
            print(f"  {i:>3}. {m['src']} -> {m['dst']}")
        chosen = parse_selection(ask_human(
            "Approve which moves? all / none / e.g. 1,3,5-8: "), len(moves))
        if not chosen:
            return "DECLINED: the user approved no moves. Nothing changed."
        _plans[plan_id] = [moves[i] for i in chosen]
    return apply_plan(plan_id) + (" (auto-approved by policy)" if decision == "auto" else "")

REGISTRY = {"list_files": list_files, "propose_moves": base.propose_moves,
            "propose_by_date": propose_by_date, "apply_plan": gated_apply,
            "undo_plan": undo_plan}
TOOLS = base.TOOLS[:2] + [{
    "name": "propose_by_date", "description": "Create a plan (read-only) that puts photos "
    "into photos/YYYY/MM by date. Use when the user asks to sort photos by date or month.",
    "input_schema": {"type": "object", "properties": {}}}] + base.TOOLS[2:]
SYSTEM = "You organize files. Always propose a plan and show it before applying it."

def run_tool(name, args):
    try:
        if name == "undo_plan" and ask_human(f"Undo {args}? [y/N] ").lower() != "y":
            return "DECLINED: the user did not approve the undo."
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"
