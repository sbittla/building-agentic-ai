"""./course.sh live-check: runs the book's ORIGINAL chapter files, never the user's edits,
reports each one, and writes live_report.md. Checked here with stand-in files (no API key)."""
import sys
from pathlib import Path
import pytest

COURSE = Path("/opt/course")

@pytest.mark.skipif(not (COURSE / "course.py").exists(), reason="runs in the course image")
def test_live_check_mechanics(tmp_path, monkeypatch, capsys):
    sys.path.insert(0, str(COURSE))
    import course
    ws, pristine = tmp_path / "ws", tmp_path / "pristine"
    ws.mkdir(); pristine.mkdir()
    (ws / "good.py").write_text("raise SystemExit('the user broke this copy')")   # user's edit
    (pristine / "good.py").write_text("print('hello from the book')")
    (pristine / "bad.py").write_text("raise ValueError('boom')")
    (pristine / "echo.py").write_text("print(input())")
    monkeypatch.setattr(course, "WS", ws)
    monkeypatch.setattr(course, "PRISTINE", pristine)
    monkeypatch.setattr(course, "LIVE_RUNS", [("1", "good.py", "", 1), ("2", "bad.py", "", 1),
                                              ("2", "echo.py", "typed\n", 1)])
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-offline")
    assert course.cmd_live_check(["--yes"]) == 1                 # one failure -> non-zero
    report = (ws / "live_report.md").read_text()
    assert "PASS: good.py" in report and "hello from the book" in report
    assert "FAIL: bad.py" in report and "ValueError" in report
    assert "PASS: echo.py" in report and "typed" in report
    assert (ws / "good.py").read_text().startswith("raise SystemExit")   # user's file untouched
    assert course.cmd_live_check(["1", "--yes"]) == 0            # only Part 1

def test_live_runs_exist():
    import os
    code = Path(os.environ["COURSE_CODE_FLAT"])
    if not (COURSE / "course.py").exists():
        pytest.skip("runs in the course image")
    sys.path.insert(0, str(COURSE))
    import course
    for _, cmd, _, _ in course.LIVE_RUNS:
        assert (code / cmd.split()[0]).exists(), cmd
