"""Security fixes, each proven by an attack that must fail (all offline)."""
import json
import os
import sys
from pathlib import Path
import pytest

# ---------------- chapter 10: what "the tests pass" means can't be rewritten
@pytest.fixture
def repo(ws):
    import shutil, subprocess, ch10_fixer
    shutil.rmtree("buggy_repo", ignore_errors=True)
    subprocess.run([sys.executable, "ch10_make_repo.py"], check=True, capture_output=True)
    ch10_fixer.REPO = Path("buggy_repo").resolve(); ch10_fixer.history.clear()
    return ch10_fixer

@pytest.mark.parametrize("path", ["test_pricing.py", "conftest.py", "CONFTEST.PY", "pytest.ini",
                                  "pyproject.toml", "setup.cfg", "Test_Pricing.py", "pricing_test.py",
                                  "new_module.py", "notes.txt", "../escape.py"])
def test_10_writes_outside_the_allow_list_are_refused(repo, path):
    out = repo.run_tool("write_file", {"path": path, "content": "import pricing\npricing.subtotal = lambda i: 0\n"})
    assert out.startswith("ERROR"), (path, out)
    assert not (repo.REPO / "conftest.py").exists()

def test_10_source_files_can_still_be_fixed(repo):
    src = (repo.REPO / "pricing.py").read_text()
    assert repo.write_file("pricing.py", src).startswith("Wrote")

def test_10_tests_run_without_secrets(repo, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-secret-value")
    (repo.REPO / "test_env_probe.py").write_text(
        "import os\ndef test_no_key():\n    assert 'ANTHROPIC_API_KEY' not in os.environ\n")
    out = repo.run_tests()
    assert "test_env_probe.py ." in out or "test_no_key PASSED" in out or "3 failed" in out
    assert "test_no_key" not in out.split("short test summary")[-1]    # the probe didn't fail

def test_10_sandbox_job_runs_in_a_copy(ws, tmp_path):
    if not Path("/opt/course/course.py").exists():
        pytest.skip("runs in the course image")
    sys.path.insert(0, "/opt/course")
    import course
    course.WS = ws
    job_dir = ws / "sandbox_probe"
    job_dir.mkdir(exist_ok=True)
    (job_dir / "evil.py").write_text(
        "import os, pathlib\n"
        "pathlib.Path('written_by_job.txt').write_text('x')\n"
        "print('KEY' if 'ANTHROPIC_API_KEY' in os.environ else 'NOKEY')\n")
    out, code = course._run_job({"id": "t1", "cmd": [sys.executable, "evil.py"], "cwd": str(job_dir)})
    assert code == 0 and "NOKEY" in out
    assert not (job_dir / "written_by_job.txt").exists()          # the copy was changed, not the workspace
    out, code = course._run_job({"id": "t2", "cmd": ["true"], "cwd": "/etc"})
    assert code == 1 and "inside /workspace" in out

# ---------------- chapter 13: servers get only what they need
def test_13_servers_get_a_minimal_environment(monkeypatch):
    import ch13_mcp_agent as m
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-secret")
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN", "ghp_secret")
    env = m.server_env({"command": "x"})
    assert "ANTHROPIC_API_KEY" not in env and "GITHUB_PERSONAL_ACCESS_TOKEN" not in env
    assert "PATH" in env
    env = m.server_env({"command": "x", "pass_env": ["GITHUB_PERSONAL_ACCESS_TOKEN"], "env": {"A": "1"}})
    assert env["GITHUB_PERSONAL_ACCESS_TOKEN"] == "ghp_secret" and env["A"] == "1"
    assert "ANTHROPIC_API_KEY" not in env
    cfg = json.load(open("servers_github.json"))
    assert cfg["servers"]["github"]["pass_env"] == ["GITHUB_PERSONAL_ACCESS_TOKEN"]

# ---------------- chapters 11 and 14: SSRF and exfiltration
@pytest.mark.parametrize("url", ["http://example.com", "https://localhost/admin", "https://127.0.0.1:8080/",
                                 "https://10.1.2.3/", "https://169.254.169.254/latest/meta-data",
                                 "https://[::1]/", "file:///etc/passwd"])
def test_11_url_problem_refuses_inward_and_plain_urls(url):
    from ch11_web import url_problem
    assert url_problem(url)

def test_11_fetch_checks_every_redirect(monkeypatch):
    import ch11_web as w, httpx
    monkeypatch.setattr(w, "url_problem", lambda u, *a, **k: None if u.startswith("https://ok.example") else "private")
    def fake_get(url, **kw):
        return httpx.Response(302, headers={"location": "https://127.0.0.1/secret"},
                              request=httpx.Request("GET", url))
    monkeypatch.setattr(w.httpx, "get", fake_get)
    assert w.fetch_url("https://ok.example/start") == "ERROR: private"

def test_14_policy_blocks_unknown_sites_and_asks_after_private_reads(ws):
    from ch14_policy_agent import Policy
    asked = []
    rules = {"allow": {"fs": ["read_text_file"], "fetch": ["fetch"]},
             "egress": {"tools": {"fetch__fetch": "url"}, "allow_domains": ["docs.python.org"],
                        "check_dns": False},
             "private_sources": ["fs__*"]}
    p = Policy(rules=rules, log_path="policy_test.jsonl", approver=lambda n, a: asked.append(n) or False)
    assert p.before_call("fetch__fetch", {"url": "https://docs.python.org/3/"}) is None      # fine
    assert "not on the list" in p.before_call("fetch__fetch", {"url": "https://attacker.example/?d=1"})
    assert p.before_call("fs__read_text_file", {"path": "secret.md"}) is None
    out = p.before_call("fetch__fetch", {"url": "https://docs.python.org/?d=secret"})
    assert out.startswith("DECLINED") and asked == ["fetch__fetch"]                          # after a read: ask
    log = [json.loads(l) for l in open("policy_test.jsonl")]
    assert [r["decision"] for r in log] == ["allow", "blocked", "allow", "declined"]

def test_14_approval_shows_the_whole_call(monkeypatch, capsys):
    import builtins, ch14_policy_agent as p
    shown = {}
    monkeypatch.setattr(builtins, "input", lambda prompt: shown.setdefault("p", prompt) and "n")
    p.console_approver("fs__write_file", {"path": "a.txt\nAPPROVE nothing else", "content": "x" * 500})
    assert "\\n" in shown["p"] and "x" * 500 in shown["p"]          # newline escaped, nothing cut

# ---------------- chapter 8: read-only isn't harmless
def test_8_runaway_query_is_stopped(ws, monkeypatch):
    import ch08_sql_tools as s, time
    monkeypatch.setattr(s, "QUERY_SECONDS", 0.5)
    monkeypatch.setattr(s, "_connect", lambda deadline_s=0.5, _orig=s._connect: _orig(0.5))
    t0 = time.time()
    out = s.run_query("SELECT COUNT(*) FROM orders a, orders b, orders c, order_items d")
    assert out.startswith("ERROR") and "stopped" in out and time.time() - t0 < 5

# ---------------- chapter 6: symlinks can't smuggle files in
def test_6_search_skips_symlinks(ws, tmp_path):
    import ch06_notes_tools as n
    outside = tmp_path / "outside.txt"
    outside.write_text("TOPSECRET-VALUE\n")
    link = n.ROOT / "link.md"
    link.unlink(missing_ok=True)
    link.symlink_to(outside)
    try:
        assert "TOPSECRET" not in n.search_files("TOPSECRET")
        assert "link.md" not in n.list_files()
    finally:
        link.unlink()

# ---------------- capstone 5: pull requests are untrusted
def test_c5_fix_cannot_escape_or_touch_test_config(ws):
    import importlib.util
    cap = Path(__file__).parents[1] / "capstones" / "c5_review"
    sys.path.insert(0, str(cap)); sys.modules.pop("data", None)
    try:
        import data
        data.build()
        spec = importlib.util.spec_from_file_location("c5_repo_server", cap / "repo_server.py")
        rs = importlib.util.module_from_spec(spec); spec.loader.exec_module(rs)
        from mcp.server.mcpserver.exceptions import ToolError
        for path in ("conftest.py", "pytest.ini", "../../etc/passwd"):
            with pytest.raises(ToolError):
                rs.propose_fix("pr-1", path, "a", "b", "msg")
        assert "ANTHROPIC_API_KEY" not in rs.CLEAN_ENV
    finally:
        sys.path.remove(str(cap)); sys.modules.pop("data", None)
