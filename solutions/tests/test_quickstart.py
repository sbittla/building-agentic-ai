"""./course.sh quickstart: the book's first command must work with no key and no model."""
import os
import re
import subprocess
import sys


def test_quickstart_runs_without_a_key(ws):
    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "PROVIDER")}
    env["PYTHONPATH"] = os.pathsep.join([str(ws), env.get("PYTHONPATH", "")])
    r = subprocess.run([sys.executable, "quickstart.py"], cwd=ws, env=env,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    out = r.stdout
    assert "[step 1] get_current_date({})" in out
    assert re.search(r"\[step 2\] days_between\(", out)
    assert re.search(r"ANSWER: It's \d+ days until July 4; \d{4}-07-04 is a \w+day\.", out)
    assert "3 model calls and 2 tool calls" in out          # matches the book's sample output
