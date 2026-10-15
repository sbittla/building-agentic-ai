"""Dev tool: write or check RELEASE_MANIFEST.json, the machine-readable record of one book
release: which edition, which tag and commit, which lock file, and what was verified.

    python dev/release_manifest.py            # write RELEASE_MANIFEST.json from the repository
    python dev/release_manifest.py --check    # CI: fail if the manifest or the docs disagree

Every value is computed from files in the repository (verification/offline.json,
solutions/outputs/*/summary.json, requirements.lock, course/exercises.json, the book), never
typed in. --check fails if:
  - the lock file's hash, the exercise or capstone counts, or the test status changed since
    the manifest was written;
  - README.md, VERSION_MATRIX.md, the preface or the copyright page name a different tag;
  - the checked-out commit carries a book-v* tag that isn't this release (or its candidate);
  - code, solutions or the environment changed after the commit the tests were run on, so a
    "passed" in the manifest would be stale.
"""
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
OUT = KIT / "RELEASE_MANIFEST.json"
RELEASE = "1.0.0"
TAG = f"book-v{RELEASE}"
CANDIDATE = f"{TAG}-rc4"   # named after the manuscript it matches (the RC4 PDF)
# Files whose change after the verified commit would make the test results stale.
CODE_PATHS = ["course/code", "course/checks", "course/starters", "course/course.py", "course/data",
              "solutions/exercises", "solutions/capstones", "solutions/tests", "requirements.lock",
              "Dockerfile", "compose.yaml", "course.sh"]


def git(*args):
    r = subprocess.run(["git", *args], cwd=KIT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


EXCEPTIONS = KIT / "verification/exceptions.json"   # {"3.7": {"reason": ..., "approved_by": ..., "date": ...}}


def run_inputs(i, x, names, index):
    """The files a recorded run depended on: its solution files, the script its log names,
    the chapter's code and, for a capstone, its own folder. Tests don't affect a live run."""
    paths = {names[Path(f).name] for f in index.get(i, []) if Path(f).name in names}
    log = KIT / "solutions/outputs" / x.get("log", "")
    if log.is_file():
        m = re.search(r"^# Command:\s*(.*)$", log.read_text(encoding="utf-8", errors="replace"), re.M)
        paths |= {names[Path(t).name] for t in (m.group(1).split() if m else []) if Path(t).name in names}
    ch = re.match(r"(\d+)\.", i)
    if ch:
        paths.add(f"course/code/ch{int(ch.group(1)):02d}")
    if i.startswith("C"):
        paths |= {d.relative_to(KIT).as_posix() for d in (KIT / "solutions/capstones").glob(f"c{i[1:]}_*")}
    return sorted(paths)


def stale_runs(runs, verified):
    """Runs whose inputs changed between the run's commit and the verified commit, so the
    evidence may not hold for the release code. A '-modified' run is compared from its base."""
    names = {p.name: p.relative_to(KIT).as_posix() for p in (KIT / "solutions").rglob("*") if p.is_file()
             and not {"outputs", "tests", "__pycache__", "_index"} & set(p.parts)}
    index = json.loads((KIT / "solutions/index.json").read_text(encoding="utf-8"))
    stale = {}
    for i, x in runs.items():
        if x["status"] not in ("passed", "failed") or not x.get("commit") or not verified:
            continue
        paths = run_inputs(i, x, names, index)
        changed = git("diff", "--name-only", x["commit"].replace("-modified", ""), verified, "--", *paths) if paths else None
        if changed:
            stale[i] = changed.splitlines()
    return dict(sorted(stale.items(), key=lambda kv: [int(n) if n.isdigit() else n for n in re.split(r"(\d+)", kv[0])]))


def live_runs(verified=None):
    """Book exercises and capstones -> latest recorded run, grouped by outcome and provider."""
    ex = json.loads((KIT / "course/exercises.json").read_text(encoding="utf-8"))
    runs = {}
    for summary in (KIT / "solutions/outputs").glob("*/summary.json"):
        data = json.loads(summary.read_text(encoding="utf-8"))
        for x in data["exercises"]:
            runs[x["id"]] = dict(x, model=x.get("model") or data.get("model", ""), date=x.get("date") or data.get("date", ""))
    ids = [e["id"] for e in ex] + [f"C{n}" for n in range(1, 8)]
    outcome, provider, not_run, dates, commits = Counter(), Counter(), [], [], set()
    for i in ids:
        x = runs.get(i)
        if not x:
            not_run.append(i)
            continue
        reason = x.get("reason") or ""
        if x["status"] in ("passed", "failed"):
            outcome[x["status"]] += 1
            label = x["model"].lower()
            provider["no model" if label.startswith("none") else
                     "local (qwen3.5:9b)" if "local" in label or "qwen" in label else "Claude API"] += 1
            dates.append(x["date"][:10])
            if x.get("commit"):
                commits.add(x["commit"])
        elif reason.startswith("concept"):
            outcome["written answer"] += 1
        elif reason.startswith("needs a model"):
            not_run.append(i)
        else:
            outcome["needs a person or service"] += 1
    return {"exercises_and_capstones": len(ids), "by_outcome": dict(outcome),
            "runs_by_provider": dict(provider), "not_run_yet": not_run,
            "dates": f"{min(dates)} to {max(dates)}" if dates else None,
            "commits": sorted(commits),
            "runs_older_than_their_code": stale_runs({i: runs[i] for i in ids if i in runs}, verified),
            "evidence": "solutions/outputs/*/summary.json (each records its own commit and lock hash)"}


def build():
    off = json.loads((KIT / "verification/offline.json").read_text(encoding="utf-8"))
    prov, tot = off["provenance"], off["totals"]
    ex = json.loads((KIT / "course/exercises.json").read_text(encoding="utf-8"))
    capstones = len(re.findall(r"^## Capstone \d+:", (KIT / "course/md/90_capstones.md").read_text(encoding="utf-8"), re.M))
    lock = hashlib.sha256((KIT / "requirements.lock").read_bytes()).hexdigest()
    vm = (KIT / "VERSION_MATRIX.md").read_text(encoding="utf-8")
    mcp = re.search(r"Specification \*\*(\d{4}-\d{2}-\d{2})\*\*", vm)
    live = live_runs(prov["commit"])
    limitations = []
    if "outside the course image" in prov["environment"]:
        limitations.append("The deterministic suite was run outside the course image; "
                           f"{tot['skipped']} tests that need the image's MCP servers were skipped. "
                           "CI reruns the suite inside the image when a book-v* tag is pushed.")
    if live["not_run_yet"]:
        limitations.append(f"{len(live['not_run_yet'])} model-dependent exercises have no recorded "
                           "live-model run yet: " + ", ".join(live["not_run_yet"]) +
                           ". Record them with ./course.sh run-chapter <ids> --model claude.")
    limitations.append("Live-model runs were recorded on earlier commits than the verified one; "
                       "each summary.json names its own commit.")
    limitations.append("Two runtime images come from other publishers and are pinned by digest: the "
                       "GitHub MCP server v1.12.2 (exercises 14.3, 14.4, Capstone 4) and Ollama 0.34.4 "
                       "(the free local model). If a registry stops serving them, see VERSION_MATRIX.md.")
    limitations.append("Production readiness is not claimed: the course kit is not production-hardened "
                       "(Appendix M of the book, SECURITY_MODEL.md).")
    gates = open_gates(live, prov)
    return {
        "book_title": "Building Agentic AI Systems: From First Agent to MCP, Multi-Agent Orchestration, and Production",
        "author": "Srinivasa Rao Bittla",
        "book_edition": "First edition",
        "book_release": RELEASE,
        "repository_tag": TAG,
        "release_candidate_tag": CANDIDATE,
        "release_status": (f"candidate: {TAG} is not published until every open_gates entry is closed"
                           if gates else f"released as {TAG}"),
        "isbn": {"paperback": "979-8177506326", "hardcover": "979-8177514734"},
        "exercises": len(ex),
        "capstones": capstones,
        "git_commit": prov["commit"],
        "python_version": prov["python"],
        "dependency_lock_sha256": lock,
        "mcp_specification": mcp.group(1) if mcp else None,
        "verification_date": prov["date_utc"][:10],
        "offline_test_status": {"passed": tot["passed"], "failed": tot["failed"], "errors": tot["error"],
                                "skipped": tot["skipped"], "tests": tot["tests"],
                                "environment": prov["environment"], "model": prov["model"],
                                "evidence": "verification/offline.json"},
        "model_test_status": live,
        "known_limitations": limitations,
        "open_gates": gates,
        "commit_note": ("git_commit is the commit the tests ran on. The release tag may sit on a later "
                        "commit that adds only verification artifacts and docs; release_manifest.py --check "
                        "fails if any code, solution, test or environment file changed in between."),
    }


def open_gates(live, prov):
    """What must still happen before book-v1.0.0 replaces the release candidate."""
    gates = []
    if "outside the course image" in prov["environment"]:
        gates.append("Run the deterministic suite inside the course image (CI does this on a book-v* tag) "
                     "and record it with python dev/verify.py report.")
    if live["not_run_yet"]:
        gates.append("Record live-model runs for " + ", ".join(live["not_run_yet"]) +
                     " (./course.sh run-chapter <ids> --model claude), or approve them as exceptions here.")
    approved = json.loads(EXCEPTIONS.read_text(encoding="utf-8")) if EXCEPTIONS.exists() else {}
    approved = {i for i, e in approved.items() if isinstance(e, dict) and e.get("approved_by") and e.get("reason")}
    pending = [i for i in live.get("runs_older_than_their_code", {}) if i not in approved]
    if pending:
        gates.append("Code changed after the recorded run of " + ", ".join(pending) + ": rerun each "
                     "(./course.sh run-chapter <ids>), or approve it in verification/exceptions.json "
                     "with a reason and your name.")
    gates += ["Clean setup from a fresh checkout on Windows, macOS and Linux "
              "(./course.sh setup, build, selftest, quickstart).",
              "Independent technical review and a beginner-reader pilot (PILOT.md), with findings recorded.",
              "Final proof of the print files, and KDP preview of paperback and hardcover "
              "(trim, gutter, spine, cover, ISBN and metadata).",
              "Confirm the ISBN registrations match the title, subtitle, author and imprint.",
              "Run dev/check_links.py with network access on the release commit, and open by hand any "
              "link a site blocks for automated checks (403) or rejects for its user agent.",
              f"Publish the {TAG} tag on the verified commit (or a docs-only commit after it), then check that "
              "a clean checkout of the tag follows How to Use This Book's setup exactly."]
    return gates


def is_candidate(tag):
    """book-v1.0.0-rc1, -rc2, ...: this release's candidates (the verified commit may carry an earlier one)."""
    return bool(re.fullmatch(re.escape(TAG) + r"-rc\d+", tag))


def is_future_patch(tag):
    """book-v1.0.1, book-v1.0.2, ...: named as examples of later patch releases, allowed."""
    m = re.fullmatch(r"book-v(\d+)\.(\d+)\.(\d+)", tag)
    base = RELEASE.split(".")
    return bool(m) and m.group(1, 2) == tuple(base[:2]) and int(m.group(3)) > int(base[2])


def check():
    problems = []
    if not OUT.exists():
        print("RELEASE_MANIFEST.json is missing: run python dev/release_manifest.py")
        return 1
    have, want = json.loads(OUT.read_text(encoding="utf-8")), build()
    for k in want:
        if have.get(k) != want[k]:
            problems.append(f"RELEASE_MANIFEST.json: '{k}' is out of date (run python dev/release_manifest.py)")
    docs = {"README.md": KIT / "README.md", "VERSION_MATRIX.md": KIT / "VERSION_MATRIX.md",
            "the preface": KIT / "course/md/fm_preface.md", "the copyright page": KIT / "course/build.js",
            "How to Use This Book": KIT / "course/md/00_front.md"}
    for name, path in docs.items():
        text = path.read_text(encoding="utf-8")
        tags = {x for x in re.findall(r"book-v\d+\.\d+\.\d+(?:-rc\d+)?", text)
                if x not in (TAG, CANDIDATE) and not is_candidate(x) and not is_future_patch(x)}
        if TAG not in text:
            problems.append(f"{name} doesn't name the release tag {TAG}")
        if tags:
            problems.append(f"{name} names other book tags: {sorted(tags)}")
        if re.search(r"\b(second|third|fourth) printing\b|this printing", text, re.I):
            problems.append(f"{name} still describes printings")
    exact = git("describe", "--tags", "--exact-match", "HEAD")
    if exact and exact.startswith("book-v") and exact not in (TAG, CANDIDATE) and not is_candidate(exact):
        problems.append(f"HEAD is tagged {exact}, but the manifest describes {TAG}")
    verified = have.get("git_commit")
    if git("cat-file", "-e", f"{verified}^{{commit}}") is None:
        problems.append(f"the verified commit {verified} isn't in this repository's history "
                        "(CI needs fetch-depth: 0)")
    else:
        changed = git("diff", "--name-only", verified, "HEAD", "--", *CODE_PATHS)
        if changed:
            problems.append("code changed after the verified commit, so the test status is stale: "
                            + ", ".join(changed.splitlines()[:8]))
    for p in problems:
        print("  " + p)
    if problems:
        print(f"{len(problems)} release-manifest problem(s)")
        return 1
    print(f"OK: release manifest current for {TAG} (verified commit {verified[:12]})")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    OUT.write_text(json.dumps(build(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}")
