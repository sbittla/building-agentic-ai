"""Exercises 9.3, 9.4 and 9.5, run end to end: the agent proposes a plan, a person answers
the approval prompt (typed on stdin), and a directory listing before and after shows what
really happened.

    python run9_approval.py decline    9.3: plan shown, the person says n, nothing moves
    python run9_approval.py undo       9.4: approve (y), then undo (y): the folder is restored
    python run9_approval.py partial    9.5: approve only some moves (e.g. 1,3,5): only those move
"""
import hashlib
import json
import sys
from pathlib import Path

import ch09_organizer as org
from ch04_agent import run_agent

ASK = ("Tidy up my messy folder by file type. Propose a plan, show it to me, then call "
       "apply_plan with its plan_id: I approve or decline in the approval prompt.")

def snapshot() -> tuple[list[str], str]:
    files = sorted(str(p.relative_to(org.ROOT)) for p in org.ROOT.rglob("*") if p.is_file())
    return files, hashlib.sha256("\n".join(files).encode()).hexdigest()[:12]

def show(label: str) -> tuple[list[str], str]:
    files, digest = snapshot()
    folders = sorted({f.split("/")[0] for f in files if "/" in f})
    loose = [f for f in files if "/" not in f]
    print(f"{label}: {len(loose)} loose files, folders {folders or 'none'}, listing hash {digest}")
    return files, digest

def ensure_applied(tools, run_tool, system, history):
    """A small model sometimes stops after showing the plan and asks in prose. Ask once
    more, the way a person would, so the approval prompt is actually reached."""
    called = any(isinstance(m["content"], list) and any(
        getattr(b, "type", None) == "tool_use" and b.name == "apply_plan"
        for b in m["content"]) for m in history if m["role"] == "assistant")
    if called:
        return history
    _, history, _ = run_agent("Yes, go ahead: call apply_plan with that plan_id now.",
                              tools, run_tool, system=system, messages=history)
    return history

def main(mode: str):
    if mode == "partial":
        import sol_ch09_organizer as sol
        tools, run_tool, system = sol.TOOLS, sol.run_tool, sol.SYSTEM
        sol.POLICY_FILE.write_text(json.dumps({**sol.DEFAULT_POLICY, "max_auto_moves": 0}))
    else:
        tools, run_tool, system = org.TOOLS, org.run_tool, "You organize files. Propose before acting."
    before, h_before = show("BEFORE")
    answer, history, _ = run_agent(ASK, tools, run_tool, system=system)
    print("Agent:", answer)
    history = ensure_applied(tools, run_tool, system, history)
    after, h_after = show("AFTER APPROVAL STEP")
    moved = sorted(set(before) - set(after))
    print(f"moved: {len(moved)} files")
    if mode == "decline":
        print("RESULT:", "nothing moved (declined)" if h_after == h_before else "FILES MOVED")
    elif mode == "undo":
        plan = next((json.loads(l)["plan"] for l in org.AUDIT.read_text().splitlines()),
                    None) if org.AUDIT.exists() else None
        print(f"applied plan: {plan}")
        if plan:
            print(org.run_tool("undo_plan", {"plan_id": plan}))     # same approval gate
        _, h_final = show("AFTER UNDO")
        print("RESULT:", "folder restored exactly" if h_final == h_before else "NOT RESTORED")
    elif mode == "partial":
        logged = [Path(json.loads(l)["src"]).name for l in org.AUDIT.read_text().splitlines()] \
            if org.AUDIT.exists() else []
        print(f"logged moves: {len(logged)} {logged}")
        print("RESULT:", "moved exactly the approved files, and logged only those"
              if moved and sorted(logged) == moved and len(moved) < len(before)
              else "MISMATCH")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "decline")
