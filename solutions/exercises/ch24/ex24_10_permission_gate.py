"""Exercise 24.10 (solution): a skill version that asks for more permissions than the
version before it is a new major version, and it waits for a named reviewer.

The regression gate of section 24.10 checks that a new version still does the job. It
doesn't notice that 1.3.0 can suddenly send email. This adds that check in front of
promote(). Offline; runs in a temporary folder."""
import tempfile
from pathlib import Path

import ch24_skill_registry as sr

def new_permissions(reg: sr.Registry, name: str, version: str) -> list[str]:
    """Permissions this version asks for that the current released version doesn't."""
    current = reg.current(name)
    before = set(reg.manifest(name, current)["permissions"]) if current else set()
    return sorted(set(reg.manifest(name, version)["permissions"]) - before)

def permission_review(reg: sr.Registry, name: str, version: str,
                      approvals: dict) -> str | None:
    """None if the version may go to the regression gate, else why it may not.
    approvals maps (name, version) to the reviewer who signed off."""
    added = new_permissions(reg, name, version)
    current = reg.current(name)
    if not added or current is None:            # a first release is reviewed at publish
        return None
    if sr.parse_version(version)[0] <= sr.parse_version(current)[0]:
        return (f"{name}@{version} adds {added}: a permission change needs a new major "
                f"version (current is {current})")
    if (name, version) not in approvals:
        return f"{name}@{version} adds {added}: waiting for a reviewer's approval"
    return None

def promote_reviewed(reg: sr.Registry, name: str, version: str,
                     approvals: dict | None = None) -> dict:
    """Permission review first, then the usual regression gate."""
    reason = permission_review(reg, name, version, approvals or {})
    if reason:
        return {"skill": f"{name}@{version}", "passed": False, "failures": [reason]}
    report = sr.promote(reg, name, version)
    if report["passed"] and (name, version) in (approvals or {}):
        report["approved_by"] = approvals[(name, version)]
    return report

def main(work: Path) -> list[tuple[str, bool]]:
    reg = sr.Registry(work / "registry")
    folder = sr.report_versions(work)["1.0.0"]          # same files for every version
    perms = {"1.0.0": ["read_skill", "run_query"], "1.1.0": ["read_skill", "run_query"],
             "1.3.0": ["read_skill", "run_query", "send_email"],
             "2.0.0": ["read_skill", "run_query", "send_email"]}
    for ver, p in perms.items():
        reg.publish(folder, ver, author="analytics@shop.example", trust="first-party",
                    permissions=p)
    steps = [("1.0.0", {}), ("1.1.0", {}), ("1.3.0", {}), ("2.0.0", {}),
             ("2.0.0", {("sql-report", "2.0.0"): "dana@shop.example"})]
    results = []
    for ver, approvals in steps:
        r = promote_reviewed(reg, "sql-report", ver, approvals)
        note = f"approved by {r['approved_by']}" if r.get("approved_by") else \
            "; ".join(r["failures"]) or "no new permissions"
        print(f"sql-report@{ver}: {'PROMOTED' if r['passed'] else 'HELD'}  ({note})")
        results.append((ver, r["passed"]))
    print(f"current: sql-report@{reg.current('sql-report')} with "
          f"{reg.manifest('sql-report', reg.current('sql-report'))['permissions']}")
    return results

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        main(Path(tmp))
