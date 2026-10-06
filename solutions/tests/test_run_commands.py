"""Runs the command behind every runnable exercise exactly as `./course.sh ex <id>`
would (in a subprocess, with piped input), using the offline stand-in model."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
import pytest

EX_JSON = Path(os.environ.get("COURSE_EXERCISES", "/opt/course/exercises.json"))
SITE = str(Path(__file__).parent / "fake_model_site")
SLOW = {"29.1"}                        # covered by test_15_4_queueing (takes ~1 minute)
# Need a running server, the Agent SDK runtime or a real SDK client: each has its own
# test in test_ch16_30.py instead.
ELSEWHERE = {"24.3", "24.7", "30.2", "30.3", "30.4"}
HF_MODEL = any(Path(os.environ.get("HF_HOME", "/opt/hf")).glob("hub/models--minishlab--potion-base-8M"))

def _cases():
    if not EX_JSON.exists():
        return []
    out = []
    for e in json.loads(EX_JSON.read_text()):
        if e["id"] == "18.4" and not HF_MODEL:
            continue                   # the local embedding model couldn't be downloaded here
        if e["kind"] == "run" and e.get("needs") != "github" and e["id"] not in SLOW | ELSEWHERE:
            out.append(pytest.param(e["id"], e.get("setup"), e["cmd"], id=f"ex{e['id']}"))
        if e["kind"] == "ask" and e.get("question"):
            code = (f"import {e['module']} as m; from ch04_agent import run_agent; "
                    f"print(run_agent({e['question']!r}, m.TOOLS, m.run_tool, "
                    f"system=getattr(m, 'SYSTEM', 'x'))[0])")
            out.append(pytest.param(e["id"], None, f'python -c "{code}"', id=f"ex{e['id']}-ask"))
    return out

@pytest.mark.parametrize("ex_id,setup,cmd", _cases())
def test_exercise_command_runs(ws, ex_id, setup, cmd):
    if "servers_ecosystem.json" in cmd:   # the reference servers ship only in the course image
        config = json.loads((Path(os.environ.get("COURSE_CODE", "/opt/course/code")) / "servers_ecosystem.json").read_text())
        missing = sorted(s["command"] for s in config.get("servers", config).values() if not shutil.which(s["command"]))
        if missing:
            pytest.skip(f"needs {', '.join(missing)} from the course image")
    env = {**os.environ, "FAKE_MODEL": "1", "PYTHONUNBUFFERED": "1", "HF_HUB_OFFLINE": "1",
           "PYTHONPATH": os.pathsep.join([SITE, str(ws), os.environ.get("PYTHONPATH", "")])}
    if setup:
        setup = setup.replace("course data", f"{sys.executable} -c 'import sys; sys.path.insert(0, \"{os.environ.get('COURSE_DATA', '/opt/course/data')}\"); import generate as g; a=sys.argv[1:]; getattr(g, a[0])(*([int(a[a.index(\"--count\")+1])] if \"--count\" in a else []) + ([a[a.index(\"--out\")+1]] if \"--out\" in a else []))' ")
        if "repo" in setup:
            setup = f"rm -rf buggy_repo && {sys.executable} ch10_make_repo.py"
        subprocess.run(["bash", "-c", setup], cwd=ws, env=env, check=True, capture_output=True)
    cmd = cmd.replace("python ", f"{sys.executable} ")
    r = subprocess.run(["bash", "-c", cmd], cwd=ws, env=env, input="n\nquit\nquit\n",
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, f"exit {r.returncode}\n{r.stdout[-800:]}\n{r.stderr[-1500:]}"
