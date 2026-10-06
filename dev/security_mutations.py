"""Do the security scenario tests actually test the controls? Switch each control off in
the real course code and check that its "mitigated" test now FAILS.

    python dev/security_mutations.py [--out verification/security_mutations.json]

A mutation that no test notices would mean a control could be deleted without anyone
knowing. Run inside the course image or anywhere requirements.lock is installed.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from verify import flatten  # noqa: E402

# control -> (what is switched off, the code that switches it off, scenarios that must notice)
MUTATIONS = {
    "leak scan and egress guard": ("ch25_guards.scan and its URL check",
        "import ch25_guards as g; g.scan = lambda v: []; g.url_problem = lambda *a, **k: None", ["S1", "S12"]),
    "memory read scopes": ("ch17_memory_policy.can_read", "import ch17_memory_policy as m; m.can_read = lambda *a: True", ["S5"]),
    "session ownership": ("the owner check in ch30_service.load_session",
        "import ch30_service as s; s.hmac.compare_digest = lambda a, b: True", ["S6"]),
    "URL rules": ("ch11_web.url_problem", "import ch11_web as w; w.url_problem = lambda *a, **k: None", ["S10", "S11"]),
    "authorization at the tool": ("ch26_identity.authorize", "import ch26_identity as i; i.authorize = lambda *a, **k: {}", ["S9", "S14"]),
    "policy layer": ("ch14 Policy allow-list and decisions",
        "import ch14_policy_agent as p; p.Policy._allowed = lambda self, n: True; "
        "p.Policy.decide = lambda self, n, a: ('allow', '')", ["S2", "S8"]),
    "idempotency keys": ("ch19_durable de-duplication by key",
        "import ch19_durable as d, os; o = d._record; d._record = lambda k, key, v: o(k, key + os.urandom(3).hex(), v)", ["S13"]),
    "approval gate": ("ch09_organizer.NEEDS_APPROVAL", "import ch09_organizer as o; o.NEEDS_APPROVAL = set()", ["S14"]),
    "sender rule": ("the sender check in ch25_quarantine.add_task",
        "import ch25_quarantine as q; q.add_task = lambda title, source_email, due=None: q.TASKS.append({'title': title}) or 'Added'", ["S3"]),
    "memory write gate": ("ch17_memory_policy.gate and can_write",
        "import ch17_memory_policy as m; m.gate = lambda t, s: ('active', 0.9); m.can_write = lambda *a, **k: True", ["S7", "S12"]),
    "safe rendering": ("ch25_guards.sanitize_markdown", "import ch25_guards as g; g.sanitize_markdown = lambda t, h: t", ["S4"]),
    # S15 has two layers: checkpoints skip finished steps, and idempotency keys make a repeated
    # step harmless. Either alone protects it, so this switches both off to show the test notices.
    "checkpoints and idempotency": ("ch19_durable checkpoints (finished steps forgotten) and keys",
        "import ch19_durable as d, os\n"
        "o = d._record; d._record = lambda k, key, v: o(k, key + os.urandom(3).hex(), v)\n"
        "r = d.run_job\n"
        "def run_forgetting(job_id, *a, **k):\n"
        "    with d._db() as c:\n"
        "        c.execute(\"UPDATE steps SET status='pending' WHERE job_id=?\", (job_id,)); c.commit()\n"
        "    return r(job_id, *a, **k)\n"
        "d.run_job = run_forgetting", ["S15"]),
}

PLUGIN = '''
import os
class _Mutate:
    def pytest_sessionstart(self, session):
        exec(os.environ["MUTATION"], {})
def pytest_configure(config):
    config.pluginmanager.register(_Mutate())
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(KIT / "verification/security_mutations.json"))
    args = ap.parse_args()
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        flat = Path(tmp) / "solutions"
        flatten(Path(os.environ.get("COURSE_SOLUTIONS", KIT / "solutions")), flat)   # /solutions in the image
        (flat / "tests" / "mutation_plugin.py").write_text(PLUGIN)
        code = os.environ.get("COURSE_CODE", str(KIT / "course/code"))
        base = dict(os.environ, COURSE_CODE=code, COURSE_DATA=str(Path(code).parent / "data"),
                    COURSE_EXERCISES=str(Path(code).parent / "exercises.json"), COURSE_HOME=str(Path(code).parent),
                    PYTHONDONTWRITEBYTECODE="1",
                    PYTHONPATH=os.pathsep.join([str(flat / "tests"), str(flat / "capstones"), str(flat / "exercises")]))
        for name, (what, patch, expected) in MUTATIONS.items():
            junit = Path(tmp) / "junit.xml"
            subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "mutation_plugin",
                            "--rootdir", tmp, f"--junitxml={junit}", "-k", "mitigated",
                            str(flat / "tests" / "test_security_scenarios.py")],
                           cwd=tmp, env=dict(base, MUTATION=patch), capture_output=True, text=True)
            import xml.etree.ElementTree as ET
            failed = sorted(tc.get("name").split("_")[1] for tc in ET.parse(junit).getroot().iter("testcase")
                            if tc.find("failure") is not None or tc.find("error") is not None)
            caught = set(expected) <= set(failed)
            results.append({"control": name, "switched_off": what, "expected_to_fail": expected,
                            "failed": failed, "caught": caught})
            print(f"{'caught ' if caught else 'MISSED '} {name:28} -> failing: {', '.join(failed) or 'none'}")
    Path(args.out).parent.mkdir(exist_ok=True)
    Path(args.out).write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    missed = [r["control"] for r in results if not r["caught"]]
    print(f"{len(results) - len(missed)} of {len(results)} controls: removing them is caught by a test")
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(main())
