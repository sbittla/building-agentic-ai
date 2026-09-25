import os, re, subprocess, sys, textwrap
from pathlib import Path

BUGGY = textwrap.dedent('''
    def word_count(text): return len(text.split(" "))          # wrong for extra spaces and ""
    def most_common_word(text):
        words = text.lower().split()
        return max(set(words), key=words.count) if words else None   # ignores punctuation, ties
    def invoice_total(items): return sum(i["price"] * i["qty"] for i in items)   # no rounding
''')

def _run(extra_path=None):
    env = dict(os.environ)
    if extra_path:
        env["PYTHONPATH"] = f"{extra_path}:{env.get('PYTHONPATH', '')}"
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--noconftest",
                           os.environ["EXERCISE_FILE"]], capture_output=True, text=True, env=env,
                          cwd=extra_path or os.getcwd())   # python -m puts the current folder first

def test_enough_passing_tests():
    r = _run()
    m = re.search(r"(\d+) passed", r.stdout)
    assert r.returncode == 0 and m and int(m.group(1)) >= 9, "at least nine passing tests:\n" + r.stdout[-1500:]

def test_tests_catch_bugs(tmp_path):
    (tmp_path / "ex0_4_basics.py").write_text(BUGGY)
    r = _run(tmp_path)
    assert r.returncode != 0, "your tests should FAIL on a buggy version of 0.4 (edge cases catch bugs)"
