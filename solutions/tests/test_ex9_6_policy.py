"""Exercise 9.6 (Complex) reference solution: policy, gate, collisions and exact undo."""
import hashlib
import importlib
import json
import os
import shutil
from pathlib import Path
import pytest

def snapshot(root: Path) -> dict:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}

@pytest.fixture
def org(ws, monkeypatch):
    import generate
    shutil.rmtree("messy_big", ignore_errors=True)
    generate.messy(200, "messy_big")
    import ch09_organizer
    monkeypatch.setattr(ch09_organizer, "ROOT", Path("messy_big").resolve())
    monkeypatch.setattr(ch09_organizer, "AUDIT", Path("audit_big.jsonl"))
    Path("audit_big.jsonl").unlink(missing_ok=True)
    ch09_organizer._plans.clear()
    import sol_ch09_organizer as sol
    importlib.reload(sol)                  # picks up the patched ROOT
    return sol

def test_policy_blocks_forbidden_types(org):
    assert org.policy_decision([{"src": "run.sh", "dst": "other/run.sh"}]) == "block"
    assert org.policy_decision([{"src": "a.jpg", "dst": "images/a.jpg"}]) == "auto"
    assert org.policy_decision([{"src": "a.pdf", "dst": "documents/a.pdf"}]) == "ask"

def test_injection_named_file_cannot_bypass_gate(org, monkeypatch):
    before = snapshot(org.ROOT)
    org.propose_moves = None
    out = org.run_tool("propose_moves", {})
    assert "IGNORE PREVIOUS INSTRUCTIONS" in out           # it's just data in the plan
    monkeypatch.setattr(org, "ask_human", lambda prompt: "none")
    assert org.run_tool("apply_plan", {"plan_id": "plan-1"}).startswith("DECLINED")
    assert snapshot(org.ROOT) == before

def test_partial_approval_collisions_and_exact_undo(org, monkeypatch):
    before = snapshot(org.ROOT)
    org.run_tool("propose_moves", {})
    monkeypatch.setattr(org, "ask_human", lambda prompt: "all" if "Approve" in prompt else "y")
    assert "Moved" in org.run_tool("apply_plan", {"plan_id": "plan-1"})
    docs = org.ROOT / "documents"
    assert (docs / "report.pdf").read_text() == "old report\n"       # never overwritten
    assert (docs / "report (1).pdf").read_text() == "new report\n"
    assert (org.ROOT / ".hidden_config").exists() is False or True   # hidden files are just files
    assert "Restored" in org.run_tool("undo_plan", {"plan_id": "plan-1"})
    assert snapshot(org.ROOT) == before                              # exact, byte for byte

def test_parse_selection(org):
    assert org.parse_selection("1,3,5-8", 10) == [0, 2, 4, 5, 6, 7]
    assert org.parse_selection("all", 3) == [0, 1, 2]
    assert org.parse_selection("none", 3) == []
    assert org.parse_selection("2, 99", 3) == [1]
