"""Capstone 5: local 'pull requests' (branches): read diffs, run tests in an isolated
worktree, and propose fixes on a new branch. Swap in GitHub's MCP server for real PRs."""
import logging, os, re, shutil, subprocess, sys
from pathlib import Path
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from data import REPO, ENV

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
WT = Path("review_worktrees").resolve()
# Pull-request code is UNTRUSTED: its tests run with no secrets in the environment.
CLEAN_ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": "/tmp",
             "PYTHONDONTWRITEBYTECODE": "1", "LANG": "C.UTF-8"}
PROTECTED = {"conftest.py", "pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini"}

mcp = MCPServer("repo")

def _git(*args, cwd=REPO):
    r = subprocess.run(["git", *args], cwd=cwd, env=ENV, capture_output=True, text=True)
    if r.returncode:
        raise ToolError(r.stderr.strip()[:300])
    return r.stdout

def _branch(name):
    if not re.fullmatch(r"[\w.-]+", name) or name not in _git("branch", "--format=%(refname:short)").split():
        raise ToolError(f"No branch {name}. Use list_prs.")
    return name

def _worktree(branch):
    path = WT / branch
    if not path.exists():
        WT.mkdir(exist_ok=True)
        _git("worktree", "add", "-f", str(path), branch)
    return path

@mcp.tool()
def list_prs() -> str:
    """Open pull requests (branches other than main) with their titles."""
    out = []
    for b in _git("branch", "--format=%(refname:short)").split():
        if b != "main" and not b.startswith("fix/"):
            out.append(f"{b}: {_git('log', '-1', '--format=%s', b).strip()}")
    return "\n".join(out)

@mcp.tool()
def get_pr_diff(branch: str) -> str:
    """Unified diff of a PR against main, with line numbers in the hunk headers."""
    return _git("diff", "main..." + _branch(branch))

@mcp.tool()
def read_file(branch: str, path: str) -> str:
    """A file as it is on a branch, with line numbers."""
    text = _git("show", f"{_branch(branch)}:{path}")
    return "\n".join(f"{i}: {l}" for i, l in enumerate(text.splitlines(), 1))

@mcp.tool()
def run_tests(branch: str) -> str:
    """Run pytest for a branch in its own worktree (no bytecode cache, 60 s limit)."""
    wt = _worktree(_branch(branch))
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider"],
                           cwd=wt, capture_output=True, text=True, timeout=60,
                           env=CLEAN_ENV)
    except subprocess.TimeoutExpired:
        raise ToolError("tests timed out")
    return (r.stdout + r.stderr)[-2500:]

@mcp.tool()
def propose_fix(branch: str, path: str, old: str, new: str, message: str) -> str:
    """Create branch fix/<branch> with ONE exact replacement and commit it.
    Test files cannot be changed. Needs human approval."""
    name = Path(path).name.lower()
    if name.startswith("test") or name.endswith("_test.py") or name in PROTECTED:
        raise ToolError("Changing tests or test configuration is not allowed.")
    src = _branch(branch)
    fix = f"fix/{src}"
    wt = WT / fix.replace("/", "_")
    if not wt.exists():
        WT.mkdir(exist_ok=True)
        _git("worktree", "add", "-f", "-B", fix, str(wt), src)
    f = (wt / path).resolve()
    if wt.resolve() not in f.parents or not f.is_file():
        raise ToolError(f"'{path}' is not a file inside the repository.")
    content = f.read_text()
    if content.count(old) != 1:
        raise ToolError(f"The snippet appears {content.count(old)} times; it must appear exactly once.")
    f.write_text(content.replace(old, new, 1))
    _git("commit", "-qam", message, cwd=wt)
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=wt,
                       capture_output=True, text=True, timeout=60,
                       env=CLEAN_ENV)
    return f"Committed on {fix}. Tests: {(r.stdout.strip().splitlines() or ['?'])[-1]}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
