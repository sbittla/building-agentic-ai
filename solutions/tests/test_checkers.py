"""./course.sh check <id>: every checker must PASS on the reference solution and FAIL on
the untouched starter; otherwise it isn't checking anything."""
import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

CODE = Path(os.environ.get("COURSE_CODE", "/opt/course/code"))
COURSE = CODE.parent
CHECKS, STARTERS = COURSE / "checks", COURSE / "starters"
SOL = Path(__file__).parents[1]
INDEX = json.loads((SOL / "index.json").read_text())
IN_PLACE = {"3.3": ("sol_ch03_tools.py", "ch03_tools.py")}

def _ids():
    return sorted(p.stem.removeprefix("check_").replace("_", ".", 1) for p in CHECKS.glob("check_*.py"))

def _reference(ex_id):
    if ex_id in IN_PLACE:
        return SOL / "exercises" / IN_PLACE[ex_id][0]
    f = next(f for f in INDEX[ex_id] if f.endswith(".py"))
    return SOL / f

def _starter(ex_id, ws):
    if ex_id in IN_PLACE:
        return ws / IN_PLACE[ex_id][1]                      # the original chapter file
    return STARTERS / Path(_reference(ex_id)).name

def _check(ex_id, target, ws):
    env = {**os.environ, "EXERCISE_FILE": str(target), "PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONPATH": os.pathsep.join([str(ws), str(SOL / "exercises"), os.environ.get("PYTHONPATH", "")])}
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider",
                           "--rootdir", str(CHECKS), str(CHECKS / f"check_{ex_id.replace('.', '_')}.py")],
                          cwd=ws, env=env, capture_output=True, text=True, timeout=120)

@pytest.mark.parametrize("ex_id", _ids())
def test_checker_passes_on_the_solution(ws, ex_id):
    r = _check(ex_id, _reference(ex_id), ws)
    assert r.returncode == 0, r.stdout[-2000:]

@pytest.mark.parametrize("ex_id", _ids())
def test_checker_fails_on_the_starter(ws, ex_id):
    starter = _starter(ex_id, ws)
    assert starter.exists(), f"no starter for {ex_id}"
    r = _check(ex_id, starter, ws)
    assert r.returncode != 0, f"the checker for {ex_id} passes on an unfinished starter"

def test_every_starter_becomes_valid_python():
    if not (COURSE / "course.py").exists():
        pytest.skip("runs in the course image")
    sys.path.insert(0, str(COURSE))
    import course
    by_file = {Path(e.get("file", "")).name: e for e in course.EXERCISES if e.get("file")}
    starters = sorted(STARTERS.glob("*.py"))
    assert len(starters) >= 25
    for s in starters:
        e = by_file.get(s.name)
        assert e, f"starter {s.name} matches no exercise"
        compile(course._starter_text(e, s.read_text()), s.name, "exec")
