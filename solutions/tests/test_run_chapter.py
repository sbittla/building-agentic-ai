"""./course.sh run-chapter: model switch, chapter selection, the log/summary layout and the
skip reasons. Offline: only exercises that need no model actually run."""
import json
import os
import sys
from pathlib import Path
import pytest

COURSE = Path("/opt/course")
pytestmark = pytest.mark.skipif(not (COURSE / "course.py").exists(),
                                reason="runs in the course image")

@pytest.fixture
def course(monkeypatch, tmp_path, ws):
    """The course module, writing to a temporary outputs folder. run-chapter changes
    os.environ (PROVIDER and the local-model settings): put it back afterwards."""
    sys.path.insert(0, str(COURSE))
    import course as mod
    saved = dict(os.environ)
    for var in ("RUN_MODEL", "GITHUB_PERSONAL_ACCESS_TOKEN"):
        monkeypatch.delenv(var, raising=False)
    (tmp_path / "out").mkdir()
    monkeypatch.setattr(mod, "OUTPUTS", tmp_path / "out")
    monkeypatch.setattr(mod, "WS", ws)
    # main() normally flattens the solutions (exercises/ch04/... -> exercises/); these tests
    # run from that flat copy already, so point the runner at it.
    monkeypatch.setattr(mod, "SOLUTIONS", Path(__file__).resolve().parent.parent)
    yield mod
    os.environ.clear()
    os.environ.update(saved)

def test_model_selection(course, monkeypatch, capsys):
    assert course._run_model([]) == "local"                       # the default
    assert course._run_model(["7", "--model", "claude"]) == "claude"
    assert course._run_model(["7", "--model=local"]) == "local"
    assert course._run_model(["7", "--model", "gpt"]) is None
    monkeypatch.setenv("RUN_MODEL", "claude")
    assert course._run_model(["7"]) == "claude"
    assert course._run_model(["7", "--model", "local"]) == "local"  # the flag wins
    monkeypatch.delenv("RUN_MODEL")
    # Claude without a key: a clear message, nothing runs
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    assert course.cmd_run_chapter(["1", "--model", "claude", "--yes"]) == 1
    assert "needs ANTHROPIC_API_KEY" in capsys.readouterr().err
    assert not (course.OUTPUTS / "ch01").exists()
    # The local model (the default) must be running
    monkeypatch.setattr(course, "_local_model_ready", lambda: False)
    assert course.cmd_run_chapter(["1", "--yes"]) == 1
    assert "local up" in capsys.readouterr().err
    assert os.environ["PROVIDER"] == "local"
    assert os.environ["ANTHROPIC_BASE_URL"] == course.ADAPTER_URL    # apply_provider's switch
    assert os.environ["MODEL"] == (os.environ.get("LOCAL_MODEL") or "qwen3.5:9b")
    assert course.cmd_run_chapter(["1", "--model", "gpt"]) == 2

def test_chapter_selection(course):
    keys = course._chapter_keys()
    assert keys[:5] == ["0", "P", "1", "T", "2"]
    assert keys[-7:] == ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
    assert keys.index("A") == keys.index("10") + 1
    assert [course._chapter_key(k) for k in ("ch07", "07", "p", "c1", "capstone2")] == \
        ["7", "7", "P", "C1", "C2"]
    assert [course._chapter_dir(k) for k in ("0", "7", "12", "P", "C3")] == \
        ["ch00", "ch07", "ch12", "P", "C3"]
    ids = [e["id"] for e in course._chapter_exercises("P")]
    assert ids == sorted(ids) and ids[0] == "P.1"
    assert course.cmd_run_chapter(["99", "--yes"]) == 2
    assert course.cmd_run_chapter(["--yes"]) == 2                   # no chapter given

def test_free_chapter_layout(course):
    assert course.cmd_run_chapter(["p", "--free-only"]) == 0        # no question asked
    out = course.OUTPUTS
    summary = json.loads((out / "P" / "summary.json").read_text())
    assert summary["chapter"] == "P" and summary["model"] == "none (--free-only)"
    assert [x["status"] for x in summary["exercises"]] == ["passed"] * 5
    for x in summary["exercises"]:
        log = (out / x["log"]).read_text()
        assert x["log"] == f"P/{x['id']}.log"
        for field in ("# Exercise: " + x["id"], "/exercises/exP_",
                      "# Model:    none", "# Date:", "# Exit code: 0", "# Seconds:"):
            assert field in log, (field, log[:300])
    assert "Known tools: add, greet" in (out / "P" / "P.2.log").read_text()          # the program's real output
    index = (out / "README.md").read_text()
    assert "| [P](P/) |" in index and "| 5 | 0 | 0 |" in index

def test_skip_reasons(course, monkeypatch):
    ch = "Chapter 0: Foundations"
    fake = [dict(id="0.1", kind="concept", model="none"),                 # written answer
            dict(id="0.2", kind="inspector", model="none", server="x.py"),
            dict(id="0.3", kind="desktop", model="desktop", server="x.py"),
            dict(id="0.4", kind="run", model="claude", cmd="echo claude"),
            dict(id="0.5", kind="run", model="any", needs="github", cmd="echo gh"),
            dict(id="0.6", kind="run", model="any", needs="sandbox", cmd="echo sb"),
            dict(id="0.7", kind="run", model="none", cmd="echo hello; exit 3"),
            dict(id="0.8", kind="concept", model="none")]                # not in ANSWERS.md
    fake = [dict(e, title=f"Fake {e['id']}", chapter=ch) for e in fake]
    fake[-1]["id"] = "0.99"
    monkeypatch.setattr(course, "EXERCISES", fake)
    # other tests may leave a sandbox worker running; this test wants it absent
    monkeypatch.setattr(course, "sandbox_alive", lambda: False)
    assert course.cmd_run_chapter(["0", "--yes"]) == 1                  # 0.7 fails
    rows = {x["id"]: x for x in
            json.loads((course.OUTPUTS / "ch00" / "summary.json").read_text())["exercises"]}
    assert rows["0.1"]["reason"].endswith("copied from ANSWERS.md")
    assert "What happens when you press Enter" in (course.OUTPUTS / "ch00/0.1.log").read_text()
    assert rows["0.99"]["reason"].endswith("see ANSWERS.md") and rows["0.99"]["log"] is None
    assert rows["0.2"]["reason"].startswith("needs a person: MCP Inspector")
    assert rows["0.3"]["reason"] == "needs a person: the Claude Desktop app"
    assert rows["0.4"]["reason"] == "Claude only"
    assert "GITHUB_PERSONAL_ACCESS_TOKEN" in rows["0.5"]["reason"]
    assert "sandbox up" in rows["0.6"]["reason"]
    assert rows["0.7"]["status"] == "failed" and rows["0.7"]["reason"] == "exit code 3"
    log = (course.OUTPUTS / "ch00" / "0.7.log").read_text()
    assert "# Exit code: 3" in log and "hello" in log
    assert all(rows[i]["status"] == "skipped" for i in ("0.1", "0.2", "0.3", "0.4", "0.5"))
    # --free-only skips everything that needs a model; with Claude, 'Claude only' can run
    assert course._skip_reason(fake[3], False, True) == \
        "needs a model (--free-only): Claude only"
    assert course._skip_reason(fake[3], False, False) is None
