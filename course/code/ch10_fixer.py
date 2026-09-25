"""Chapter 10: a code-fixing agent driven by test results."""
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("buggy_repo").resolve()
history = []                       # number of failing tests after each run_tests call

def _safe(rel: str) -> Path:
    p = (REPO / rel).resolve()
    if p != REPO and REPO not in p.parents:
        raise PermissionError(f"'{rel}' is outside the repo")
    return p

def list_files() -> str:
    return "\n".join(str(p.relative_to(REPO)) for p in sorted(REPO.rglob("*.py")))

def read_file(path: str) -> str:
    return "\n".join(f"{i}: {l}" for i, l in
                     enumerate(_safe(path).read_text().splitlines(), 1))

# Files that decide what "the tests pass" means. Blocking only test_*.py isn't enough:
# a conftest.py or a pytest config can make failing tests "pass" without fixing anything.
PROTECTED = {"conftest.py", "pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini", ".pytest.ini"}

def writable(path: str) -> str | None:
    """An ALLOW-list: return None if the agent may write this file, else the reason."""
    name = Path(path).name.lower()            # lower(): macOS/Windows file names ignore case
    if name.startswith("test") or name.endswith("_test.py") or name in PROTECTED:
        return "editing tests or test configuration is not allowed. Fix the code under test."
    if not name.endswith(".py"):
        return "only Python source files can be edited."
    if not _safe(path).exists():
        return "only existing files can be edited; don't create new modules."
    return None

def write_file(path: str, content: str) -> str:
    if reason := writable(path):
        return f"ERROR: {reason}"
    _safe(path).write_text(content)
    return f"Wrote {len(content)} characters to {path}."

def clean_env() -> dict:
    """Model-written code runs with NO secrets: just enough environment to run Python."""
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": "/tmp",
            "PYTHONDONTWRITEBYTECODE": "1", "LANG": "C.UTF-8"}

def run_tests() -> str:
    """Run pytest in a subprocess with a timeout; return a SHORT summary."""
    try:
        # No bytecode cache: an edit that keeps the file size the same (e.g. "+" -> "*")
        # within the same second would otherwise run the OLD cached code.
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short",
                            "-p", "no:cacheprovider"],
                           cwd=REPO, capture_output=True, text=True, timeout=60,
                           env=clean_env())                # never pass your API key along
    except subprocess.TimeoutExpired:
        return "ERROR: tests timed out after 60s (infinite loop?)"
    out = r.stdout + r.stderr
    if not re.search(r"\d+ (passed|failed)", out):
        return f"ERROR: could not run tests:\n{out[-1500:]}"
    m = re.search(r"(\d+) failed", out)
    history.append(int(m.group(1)) if m else 0)
    return out[-3000:]             # the end has the summary and the failures

REGISTRY = {"list_files": list_files, "read_file": read_file,
            "write_file": write_file, "run_tests": run_tests}
TOOLS = [
    {"name": "list_files", "description": "List Python files in the repo.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "read_file", "description": "Read a file with line numbers.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}},
                      "required": ["path"]}},
    {"name": "write_file", "description": "Replace an existing source file's ENTIRE "
     "content. Tests and test configuration (test_*.py, conftest.py, pytest.ini) cannot be edited.", "input_schema": {"type": "object",
         "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
         "required": ["path", "content"]}},
    {"name": "run_tests", "description": "Run the test suite and return the result "
     "summary and failure details.", "input_schema": {"type": "object", "properties": {}}},
]
SYSTEM = ("You fix bugs. Run the tests first, read the failing code, make the "
          "smallest correct fix, and run the tests again. Never change tests. "
          "Stop when all tests pass and summarize what you changed.")

MAX_TOKENS_BUDGET = 60_000

def should_stop(stats):
    if stats["input_tokens"] + stats["output_tokens"] > MAX_TOKENS_BUDGET:
        return f"token budget of {MAX_TOKENS_BUDGET} exceeded"
    if len(history) >= 3 and history[-1] >= history[-2] >= history[-3] > 0:
        return "no progress in the last 3 test runs"
    return None

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

if __name__ == "__main__":
    from ch04_agent import run_agent
    before = {p: p.read_text() for p in REPO.glob("*.py")}
    answer, _, stats = run_agent("Make all tests pass.", TOOLS, run_tool,
                                 system=SYSTEM, max_iterations=15,
                                 should_stop=should_stop)
    print(answer, "\n", stats, "\nfailing tests per run:", history)
    import difflib                                  # show a reviewable diff
    for p, old in before.items():
        new = p.read_text()
        if new != old:
            print("".join(difflib.unified_diff(old.splitlines(True),
                  new.splitlines(True), f"a/{p.name}", f"b/{p.name}")))
