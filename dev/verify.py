"""Deterministic verification with provenance: what was tested, on which code, and how.

    python dev/verify.py run                       # run the offline suite here, then report
    python dev/verify.py report JUNIT.xml --environment "course image (CI)"

Writes verification/offline.json (machine-readable) and verification/README.md.

Every test in solutions/tests is deterministic: the model is a scripted stand-in
(solutions/tests/fakemodel.py), there is no API key and no call to a model provider, so the
same commit gives the same result on any machine. Results that depend on a real model come
from ./course.sh run-chapter and are reported separately (README.md, "Verified results").

Outcomes are kept apart: passed, failed, error (the test itself broke) and skipped, with
the reason for every skip ("needs mcp-server-git from the course image" is not a failure).
"""
import argparse
import datetime
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
OUT = KIT / "verification"

# which part of the book each test file covers
AREAS = [(r"test_ch00|test_ex_?T|test_ex_t3|test_checkers", "Chapter 0, interludes and checkers"),
         (r"test_ch01_03|test_ch04_05|test_ch06_07|test_ex6|test_ex9|test_ch08_10", "Parts 1–3: tools, loop, state, APIs, SQL, approval"),
         (r"test_ch11_12|test_multiagent|test_ex12|test_ex13|test_ch13_15|test_part5|test_a2a", "Parts 4–5: teams, MCP, A2A"),
         (r"test_ex16|test_part6|test_2026|test_ch17_", "Part 6: context, memory, retrieval"),
         (r"test_part7|test_harness|test_ch16_30|test_ch2[1-4]_", "Parts 6–9: chapter code 16–30"),
         (r"test_security|test_part8|test_ch2[56]_", "Part 8: security and identity"),
         (r"test_part9|test_ch27|test_ch28|test_ch29|test_ch30_", "Part 9: evaluation, observability, performance"),
         (r"test_ch31", "Part 10: customer production"),
         (r"test_capstones", "Capstones (C1–C7)"),
         (r"test_run|test_live|test_local_adapter", "The course kit itself")]


def area(classname):
    for pat, name in AREAS:
        if re.search(pat, classname):
            return name
    return "Other"


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=KIT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def provenance(environment):
    lock = KIT / "requirements.lock"
    dirty = git("status", "--porcelain", "--untracked-files=no", "--", "course", "solutions", "dev")
    try:
        import pytest
        pytest_version = pytest.__version__
    except ImportError:
        pytest_version = None
    return {
        "commit": git("rev-parse", "HEAD"),
        "describe": git("describe", "--tags", "--always", "--dirty"),
        "tracked_changes": bool(dirty),
        "requirements_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest() if lock.exists() else None,
        "environment": environment,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "pytest": pytest_version,
        "model": "scripted stand-in (solutions/tests/fakemodel.py); no API key, no model provider called",
        "date_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": "pytest solutions/tests (as ./course.sh check-solutions runs it)",
    }


def parse(junit):
    cases = []
    for tc in ET.parse(junit).getroot().iter("testcase"):
        outcome, message = "passed", ""
        for tag in ("failure", "error", "skipped"):
            el = tc.find(tag)
            if el is not None:
                outcome = "failed" if tag == "failure" else tag
                message = (el.get("message") or "").strip()
                break
        cls = tc.get("classname", "")
        cases.append({"test": f"{cls.split('.')[-1]}::{tc.get('name')}", "area": area(cls),
                      "outcome": outcome, "seconds": round(float(tc.get("time") or 0), 2),
                      "message": message[:300]})
    return cases


def report(junit, environment):
    cases = parse(junit)
    counts = Counter(c["outcome"] for c in cases)
    skips = Counter(re.sub(r"^Skipped: ", "", c["message"]) for c in cases if c["outcome"] == "skipped")
    by_area = defaultdict(Counter)
    for c in cases:
        by_area[c["area"]][c["outcome"]] += 1
    result = {"provenance": provenance(environment),
              "totals": {k: counts.get(k, 0) for k in ("passed", "failed", "error", "skipped")} | {"tests": len(cases)},
              "skipped_reasons": dict(skips.most_common()),
              "by_area": {a: dict(c) for a, c in sorted(by_area.items())},
              "not_passed": [c for c in cases if c["outcome"] != "passed"],
              "tests": cases}
    OUT.mkdir(exist_ok=True)
    (OUT / "offline.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    write_markdown(result)
    write_security(cases, result["provenance"])
    t = result["totals"]
    print(f"{t['tests']} tests: {t['passed']} passed, {t['failed']} failed, {t['error']} errors, "
          f"{t['skipped']} skipped -> verification/offline.json, verification/README.md")
    return 0 if not (t["failed"] or t["error"]) else 1


def write_markdown(r):
    p, t = r["provenance"], r["totals"]
    lines = ["# Deterministic verification", "",
             "Generated by `python dev/verify.py`; the machine-readable version is "
             "[offline.json](offline.json). These tests use a scripted stand-in model, so the same "
             "commit gives the same result anywhere. Results with a real model are in README.md, "
             "\"Verified results\".", "",
             "| | |", "| --- | --- |",
             f"| Commit | `{p['commit']}` ({p['describe']}){' with uncommitted changes' if p['tracked_changes'] else ''} |",
             f"| Dependency lock | `requirements.lock`, sha256 `{(p['requirements_lock_sha256'] or '')[:16]}…` |",
             f"| Environment | {p['environment']}; Python {p['python']}, pytest {p['pytest']} |",
             f"| Model | {p['model']} |",
             f"| Run | {p['date_utc']}, `{p['command']}` |", "",
             f"**{t['tests']} tests: {t['passed']} passed, {t['failed']} failed, {t['error']} errors, "
             f"{t['skipped']} skipped.**", "",
             "| Area | Passed | Failed | Errors | Skipped |", "| --- | ---: | ---: | ---: | ---: |"]
    for a, c in r["by_area"].items():
        lines.append(f"| {a} | {c.get('passed', 0)} | {c.get('failed', 0)} | {c.get('error', 0)} | {c.get('skipped', 0)} |")
    if r["skipped_reasons"]:
        lines += ["", "**Why tests were skipped** (not applicable here, not failures):", ""]
        lines += [f"- {n} × {why}" for why, n in r["skipped_reasons"].items()]
    bad = [c for c in r["not_passed"] if c["outcome"] in ("failed", "error")]
    if bad:
        lines += ["", "**Failures:**", ""] + [f"- `{c['test']}`: {c['message']}" for c in bad]
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_security(cases, prov):
    """verification/SECURITY.md: every security scenario, its two tests, and whether removing
    its control is caught (dev/security_mutations.py)."""
    scenarios = json.loads((KIT / "solutions/tests/security_scenarios.json").read_text(encoding="utf-8"))
    outcome = {c["test"].split("::")[-1]: c["outcome"] for c in cases if "test_security_scenarios" in c["test"]}
    if not outcome:
        return
    mut_file = OUT / "security_mutations.json"
    mutations = json.loads(mut_file.read_text(encoding="utf-8")) if mut_file.exists() else []
    caught = defaultdict(list)
    for m in mutations:
        for sid in m["expected_to_fail"]:
            caught[sid].append(("caught" if m["caught"] else "MISSED") + f": {m['control']} switched off")
    mark = {"passed": "✔ attack succeeds", "failed": "✘ test failed", "error": "✘ error", "skipped": "skipped"}
    mark_m = {"passed": "✔ attack stopped", "failed": "✘ NOT STOPPED", "error": "✘ error", "skipped": "skipped"}
    lines = ["# Security regression scenarios", "",
             "Generated by `python dev/verify.py` from `solutions/tests/security_scenarios.json`, the "
             "tests in `solutions/tests/test_security_scenarios.py` and `dev/security_mutations.py`.", "",
             f"Commit `{(prov['commit'] or '')[:12]}`, {prov['environment']}, {prov['date_utc'][:10]}.", "",
             "Every scenario has two tests. **Failure mode** runs the attack against code without the "
             "control, and the attack succeeds: the test can see the attack. **Mitigated** runs it against "
             "the course code, and the control stops it. In both, the model is assumed fully fooled: the "
             "tests make exactly the calls an attacker wants, so a control that holds here holds whatever "
             "the model does (*deterministic*). **Control removed** shows that switching the control off "
             "in the real code makes the mitigated test fail.", "",
             "Run them: `./course.sh check-solutions -k security_scenarios` (seconds, no API key).", ""]
    category = None
    for sc in scenarios:
        if sc["category"] != category:
            category = sc["category"]
            lines += [f"## {category}", ""]
        sid = sc["id"]
        lines += [f"### {sid}. {sc['title']}", "",
                  f"- **Attack:** {sc['attack']}",
                  f"- **Control:** {sc['control']} *Enforcement: {sc['enforcement']}.*",
                  f"- **Failure mode** (`test_{sid}_failure_mode`): {mark.get(outcome.get(f'test_{sid}_failure_mode'), 'not run')}",
                  f"- **Mitigated** (`test_{sid}_mitigated`): {mark_m.get(outcome.get(f'test_{sid}_mitigated'), 'not run')}",
                  f"- **Control removed:** {'; '.join(caught[sid]) or 'not checked in this run'}",
                  f"- **Residual risk:** {sc['residual']}", ""]
    (OUT / "SECURITY.md").write_text("\n".join(lines), encoding="utf-8")


def flatten(solutions, flat):
    """The same flat copy ./course.sh check-solutions makes (course/course.py, flatten_solutions)."""
    shutil.copytree(solutions, flat, ignore=shutil.ignore_patterns("outputs", "exercises", "__pycache__"))
    (flat / "exercises").mkdir()
    grouping = re.compile(r"ch\d+|capstones|interludes?(_\w+)?")
    for d in sorted((solutions / "exercises").iterdir()):
        if d.name in ("_index", "__pycache__"):
            continue
        if d.is_file():
            shutil.copy2(d, flat / "exercises" / d.name)
        elif not grouping.fullmatch(d.name):
            shutil.copytree(d, flat / "exercises" / d.name, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            for src in sorted(d.rglob("*")):
                if src.is_file() and "__pycache__" not in src.parts and src.name not in ("__init__.py", ".gitkeep"):
                    shutil.copy2(src, flat / "exercises" / src.name)


def run(environment):
    with tempfile.TemporaryDirectory() as tmp:
        flat = Path(tmp) / "solutions"
        flatten(KIT / "solutions", flat)
        junit = Path(tmp) / "junit.xml"
        env = dict(os.environ, COURSE_CODE=str(KIT / "course/code"), COURSE_DATA=str(KIT / "course/data"),
                   COURSE_EXERCISES=str(KIT / "course/exercises.json"), COURSE_HOME=str(KIT / "course"),
                   PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=os.pathsep.join([str(flat / "capstones"), str(flat / "exercises")]))
        subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", tmp,
                        f"--junitxml={junit}", str(flat / "tests")], cwd=tmp, env=env)
        subprocess.run([sys.executable, str(KIT / "dev/security_mutations.py")])
        return report(junit, environment)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--environment", default=f"outside the course image ({platform.system()})")
    rp = sub.add_parser("report")
    rp.add_argument("junit")
    rp.add_argument("--environment", default="course image")
    a = ap.parse_args()
    sys.exit(run(a.environment) if a.cmd == "run" else report(a.junit, a.environment))
