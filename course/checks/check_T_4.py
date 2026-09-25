import os, subprocess, sys

BLOCK = "import socket\ndef _no(*a, **k):\n    raise OSError('network disabled by the checker')\nsocket.socket.connect = _no\n"

def test_passes_without_network(tmp_path):
    (tmp_path / "sitecustomize.py").write_text(BLOCK)
    env = {**os.environ, "PYTHONPATH": f"{tmp_path}:{os.environ.get('PYTHONPATH', '')}"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--noconftest",
                        os.environ["EXERCISE_FILE"]], capture_output=True, text=True, env=env)
    assert r.returncode == 0, "your tests must pass with the network switched off:\n" + r.stdout[-1500:]
    assert "2 passed" in r.stdout or "3 passed" in r.stdout or "4 passed" in r.stdout, \
        "test at least the 200 and the 503 answers"

MUTANT = "import httpx\ndef max_temperature(latitude, longitude):\n    return 'OK'\n"

def test_tests_really_check_the_result(tmp_path):
    """Run your tests against a broken ch00_http that ignores the response: they must fail."""
    (tmp_path / "ch00_http.py").write_text(MUTANT)
    env = {**os.environ, "PYTHONPATH": f"{tmp_path}:{os.environ.get('PYTHONPATH', '')}"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--noconftest",
                        os.environ["EXERCISE_FILE"]], capture_output=True, text=True, env=env,
                       cwd=tmp_path)                  # python -m puts the CURRENT folder first
    assert r.returncode != 0, "your tests pass even when max_temperature is broken: assert on its result"
