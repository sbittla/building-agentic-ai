import os, re, subprocess, sys

def test_parametrized_cases():
    r = subprocess.run([sys.executable, "-m", "pytest", "-v", "-p", "no:cacheprovider", "--noconftest",
                        os.environ["EXERCISE_FILE"]], capture_output=True, text=True)
    passed = len(re.findall(r"PASSED", r.stdout))
    assert r.returncode == 0, "your tests should pass:\n" + r.stdout[-1500:]
    assert passed >= 5, f"at least five cases, each its own line with -v; found {passed}"
