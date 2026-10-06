"""Chapter 24.10: skills as software. Registry, hashes, trust levels, dependency
resolution, composition, the regression gate and rollback. Offline."""
import json
from pathlib import Path

import pytest


@pytest.fixture
def sr(ws):
    import ch24_skill_registry as sr
    return sr


@pytest.fixture
def reg(sr, tmp_path):
    return sr.Registry(tmp_path / "registry")


def skill(sr, root: Path, name: str, desc: str, cases=None, body="Do the thing.") -> Path:
    files = {"SKILL.md": f"---\nname: {name}\ndescription: {desc}\n---\n{body}\n"}
    if cases is not None:
        files["evals/cases.json"] = json.dumps(cases)
    return sr.write_skill(root / name, files)


REPORT_DESC = "Writes a revenue report from the shop database. Use for revenue reports."
CASE = [{"question": "A revenue report by city", "loads": True}]


def test_versions_and_ranges(sr):
    assert sr.satisfies("1.4.2", "^1.2") and not sr.satisfies("2.0.0", "^1.2")
    assert not sr.satisfies("1.1.9", "^1.2")
    assert sr.satisfies("1.4.2", ">=1.0.0,<2.0.0") and not sr.satisfies("2.0.0", ">=1.0.0,<2.0.0")
    assert sr.satisfies("1.4.2", "*") and sr.satisfies("1.4.2", "1.4.2")
    with pytest.raises(ValueError):
        sr.parse_version("1.4")


def test_hash_covers_paths_and_content(sr):
    a = {"SKILL.md": "x", "references/r.md": "y"}
    assert sr.content_hash(a) == sr.content_hash(dict(reversed(list(a.items()))))
    assert sr.content_hash(a) != sr.content_hash({**a, "references/r.md": "y!"})
    assert sr.content_hash(a) != sr.content_hash({"SKILL.md": "x", "references/s.md": "y"})


def test_publish_is_immutable_and_validated(sr, reg, tmp_path):
    folder = skill(sr, tmp_path / "src", "sql-report", REPORT_DESC, CASE)
    m = reg.publish(folder, "1.0.0", author="a@x", trust="verified", permissions=["run_query"])
    assert m["sha256"] == sr.content_hash(sr.read_files(folder)) and m["trust"] == "verified"
    with pytest.raises(sr.SkillError, match="already exists"):
        reg.publish(folder, "1.0.0", author="a@x", trust="verified")
    bad = skill(sr, tmp_path / "src", "Bad_Name", REPORT_DESC)
    with pytest.raises(sr.SkillError):
        reg.publish(bad, "1.0.0", author="a@x", trust="verified")


def test_gate_refuses_regressions_and_untested_skills(sr, reg, tmp_path):
    reg.publish(skill(sr, tmp_path / "v1", "sql-report", REPORT_DESC, CASE), "1.0.0",
                author="a", trust="verified")
    assert sr.promote(reg, "sql-report", "1.0.0")["passed"]
    # a 'tidied' description that no longer triggers on the old case, and no cases of its own
    reg.publish(skill(sr, tmp_path / "v2", "sql-report", "Formats tables. Use for tables."),
                "1.1.0", author="a", trust="verified")
    r = sr.promote(reg, "sql-report", "1.1.0")
    assert not r["passed"] and r["against"] == "1.0.0" and "loads=False" in r["failures"][0]
    assert reg.current("sql-report") == "1.0.0"
    reg.publish(skill(sr, tmp_path / "x", "untested", REPORT_DESC), "1.0.0", author="a",
                trust="verified")
    assert "no eval cases" in sr.promote(reg, "untested", "1.0.0")["failures"][0]
    with pytest.raises(sr.SkillError, match="not newer"):
        sr.promote(reg, "sql-report", "0.9.0")


def test_install_checks_release_hash_and_permissions(sr, reg, tmp_path):
    reg.publish(skill(sr, tmp_path / "s", "sql-report", REPORT_DESC, CASE), "1.0.0",
                author="a", trust="community", permissions=["run_query"])
    dest = tmp_path / "skills"
    with pytest.raises(sr.SkillError, match="not released"):
        sr.install(reg, "sql-report", "1.0.0", dest)
    sr.promote(reg, "sql-report", "1.0.0")
    with pytest.raises(sr.SkillError, match="run_query"):           # community: read_skill only
        sr.install(reg, "sql-report", "1.0.0", dest)
    reg.publish(skill(sr, tmp_path / "t", "trusted", REPORT_DESC, CASE), "1.0.0",
                author="a", trust="verified", permissions=["run_query"])
    sr.promote(reg, "trusted", "1.0.0")
    assert sr.install(reg, "trusted", "1.0.0", dest)["name"] == "trusted"
    assert sr.validate(dest / "trusted") == [] and not (dest / "trusted" / "manifest.json").exists()
    (reg.root / "trusted" / "1.0.0" / "SKILL.md").write_text("tampered")
    with pytest.raises(sr.SkillError, match="hash mismatch"):
        sr.install(reg, "trusted", "1.0.0", dest)


def release(sr, reg, root, name, version, requires=None):
    reg.publish(skill(sr, root / f"{name}-{version}", name, REPORT_DESC, CASE), version,
                author="a", trust="verified", requires=requires)
    assert sr.promote(reg, name, version)["passed"]


def test_resolve_picks_newest_fit_and_reports_conflicts(sr, reg, tmp_path):
    for v in ("1.0.0", "1.3.0", "2.0.0"):
        release(sr, reg, tmp_path, "schema", v)
    release(sr, reg, tmp_path, "report", "1.0.0", {"schema": "^1.0"})
    release(sr, reg, tmp_path, "lookup", "1.0.0", {"schema": ">=2.0.0"})
    assert sr.resolve(reg, {"report": "*"}) == {"report": "1.0.0", "schema": "1.3.0"}
    with pytest.raises(sr.SkillError) as exc:
        sr.resolve(reg, {"report": "*", "lookup": "*"})
    assert "conflict on schema" in str(exc.value) and "report@1.0.0 needs ^1.0" in str(exc.value)
    lockfile = sr.lock(reg, {"report": "*"})
    assert lockfile["schema"]["sha256"] == reg.manifest("schema", "1.3.0")["sha256"]
    assert sr.install_locked(reg, lockfile, tmp_path / "out") == ["report@1.0.0", "schema@1.3.0"]


def test_compose_needs_explicit_priority(sr):
    a = {"name": "a", "directives": {"table.order": "largest first", "tone": "plain"}}
    b = {"name": "b", "directives": {"table.order": "alphabetical", "tone": "plain"}}
    with pytest.raises(sr.SkillError, match="no priority"):
        sr.compose([a, b], priority=["a"])
    winners, conflicts = sr.compose([a, b], priority=["b", "a"])
    assert winners["table.order"] == ("b", "alphabetical") and winners["tone"][1] == "plain"
    assert len(conflicts) == 1 and conflicts[0]["overruled"] == [("a", "largest first")]
    assert "follow b (alphabetical)" in sr.conflict_notes(conflicts)


def test_rollback_yanks_current_and_blocks_its_install(sr, reg, tmp_path):
    release(sr, reg, tmp_path, "report", "1.0.0")
    release(sr, reg, tmp_path, "report", "1.1.0")
    assert sr.rollback(reg, "report") == "1.0.0" and reg.current("report") == "1.0.0"
    with pytest.raises(sr.SkillError, match="rolled back"):
        sr.install(reg, "report", "1.1.0", tmp_path / "out")
    assert sr.resolve(reg, {"report": "^1.0"}) == {"report": "1.0.0"}
    with pytest.raises(sr.SkillError, match="nothing to roll back"):
        sr.rollback(reg, "report")


def test_demo_runs_offline(sr, tmp_path, capsys):
    sr.demo(tmp_path)
    out = capsys.readouterr().out
    assert "sql-report@1.1.0: REFUSED" in out and "sql-report@1.2.0: PROMOTED" in out
    assert "conflict on shop-schema" in out and "hash mismatch" in out
    assert "['send_email']" in out and "current is now 1.0.0" in out


def test_exercise_permission_gate(ws, tmp_path, capsys):
    import ex24_10_permission_gate as ex
    results = ex.main(tmp_path)
    assert results == [("1.0.0", True), ("1.1.0", True), ("1.3.0", False),
                       ("2.0.0", False), ("2.0.0", True)]
    out = capsys.readouterr().out
    assert "needs a new major version" in out and "approved by dana@shop.example" in out
