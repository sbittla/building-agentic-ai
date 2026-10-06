"""Check that everything the book and the repository docs refer to actually exists.

    python dev/check_references.py          # report; exit 1 if anything is missing

It reads the manuscript (course/md/*.md) and the top-level docs, and checks:
  - exercise ids (Exercise 4.2, ./course.sh ex 4.2, solution 4.2, check 0.4) against course/exercises.json
  - solution files listed in solutions/index.json exist
  - ./course.sh commands are commands the kit has, with valid arguments
  - file names in `code` exist somewhere in the kit (or are created at run time: RUNTIME below)
  - section, chapter, appendix and capstone references point at something that exists
The single source of truth for exercises is course/exercises.json; the book, EXERCISE_INDEX.md,
README.md and solutions/SOLUTIONS.md are all checked against it.
"""
import json
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
MD = KIT / "course" / "md"
DOCS = [KIT / f for f in ("README.md", "LOCAL_MODEL.md", "EXERCISE_INDEX.md", "solutions/README.md",
                          "solutions/SOLUTIONS.md", "VERSION_MATRIX.md", "CHANGELOG.md", "ERRATA.md", "MIGRATION.md", "CURRICULUM_MAP.md", "COST_MODEL.md",
                          "ARCHITECTURE.md", "AGENT_ENGINEERING_PRINCIPLES.md", "DECISION_GUIDE.md",
                          "AGENT_LIFECYCLE.md", "SECURITY_MODEL.md", "PERFORMANCE_MODEL.md", "EVALUATION_MODEL.md")]
EXERCISES = json.loads((KIT / "course/exercises.json").read_text(encoding="utf-8"))
IDS = {e["id"] for e in EXERCISES}
INDEX = json.loads((KIT / "solutions/index.json").read_text(encoding="utf-8"))
CHECKS = {p.stem[len("check_"):].replace("_", ".") for p in (KIT / "course/checks").glob("check_*.py")}

# ./course.sh commands: the shell script's own, course.py's, and programs run inside the image
SHELL_CMDS = {"setup", "build", "sandbox", "local", "mcp", "inspector", "serve", "serve-api", "serve-mcp",
              "ex", "exercise"}
src = (KIT / "course/course.py").read_text(encoding="utf-8")
PY_CMDS = set(re.findall(r'"([a-z0-9-]+)": (?:cmd_|lambda)', src[src.index("COMMANDS = {"):]))
IMAGE_PROGS = {"help", "init", "shell", "python", "pytest", "bash", "npx", "sqlite3", "pip"}
COMMANDS = SHELL_CMDS | PY_CMDS | IMAGE_PROGS
SUBCMDS = {"local": {"up", "down", "status", "logs"}, "sandbox": {"up", "down", "status", "logs"}}

APPENDICES = set(re.findall(r"^## Appendix ([A-Z]):", (MD / "91_appendix.md").read_text(encoding="utf-8"), re.M))

# every file in the kit, by base name (code, data, starters, solutions, docs)
FILES = {}
for p in KIT.rglob("*"):
    if p.is_file() and not any(part in (".git", "_archive", "node_modules", "outputs") for part in p.parts):
        FILES.setdefault(p.name, p)
# files the reader or the code creates at run time, so they aren't in the repository
RUNTIME = {".env", ".env.tmp", "tasks.json", "tasks.db", "summary.json", "capstone_calls.jsonl", "audit.jsonl",
           "notes.json", "plans.json", "memory.db", "jobs.db", "sessions.db", "progress.md", "ANSWERS.md",
           "report.json", "toc_pages.json", "toc_headings.json", "results.json", "trace.jsonl", "spans.jsonl",
           "calls.jsonl", "approvals.jsonl", "out.docx", "policy_log.jsonl", "cache.json", "weather_cache.json",
           # checked one by one: each is written by the chapter code, the data generator or the reader
           ".env.txt",                       # Chapter 0: the name Windows Notepad gives .env by mistake
           "hello.py", "from_container.txt", "expense_report.json",   # Chapter 0 exercises
           "notes_big_answers.txt", "query_log.jsonl", "audit_log.jsonl", "shipping.py", "plan.md",
           "tool_calls.jsonl", "services.json", "agent-card.json", "refund_policy.json", "secret.md",
           "traces.jsonl", "live_report.md", "live_exercises_report.md", "exN_M.md",
           "shop.db",                         # built by course/data/generate.py, not committed
           "config.json", "raw.jsonl", "summary.md",   # written by ch29_benchmark.py into each run folder
           "release_decisions.json"}           # written by ch30_improvement_loop.py
RUNTIME_PATTERNS = [r"^ex[0-9A-Z]+_\d+(_\w+)?\.(py|md|jsonl?)$",     # a reader's exercise file
                    r"^test_\w+\.py$", r"^(my|your)_\w+\.\w+$", r"^\w+\.(log|png|pdf|docx|csv)$"]

SECTIONS = set()
for f in MD.glob("*.md"):
    for m in re.finditer(r"^##+ (\d+\.\d+|[PTRSMA]\.\d+) ", f.read_text(encoding="utf-8"), re.M):
        SECTIONS.add(m.group(1))

problems = []
def report(where, what):
    problems.append(f"{where}: {what}")

def check_id(where, i):
    if i not in IDS:
        report(where, f"exercise {i} doesn't exist")

def check_file(where, name):
    base = name.rstrip("/").split("/")[-1]
    if not base or "<" in name or "*" in name or "{" in name or base in RUNTIME:
        return
    if any(re.match(p, base) for p in RUNTIME_PATTERNS):
        return
    if base not in FILES:
        report(where, f"file `{name}` isn't in the kit")

def check_command(where, cmd):
    parts = cmd.split()
    if not parts:
        return
    c, args = parts[0], parts[1:]
    if c.endswith(".py"):
        return check_file(where, c)
    if c not in COMMANDS:
        return report(where, f"`./course.sh {cmd}`: no such command")
    if c in SUBCMDS and args and not args[0].startswith("-") and args[0] not in SUBCMDS[c]:
        report(where, f"`./course.sh {cmd}`: '{args[0]}' isn't a {c} subcommand")
    if c in ("ex", "exercise", "solution") and args and not args[0].startswith(("<", "-")):
        check_id(where, args[0])
    if c == "check" and args and not args[0].startswith(("<", "-")):
        check_id(where, args[0])
    if c == "list" and args and not args[0].startswith(("<", "[")) and not any(i.split(".")[0] == args[0] for i in IDS):
        report(where, f"`./course.sh list {args[0]}`: no exercises in that chapter")
    if c == "capstone" and args and args[0].isdigit() and not 1 <= int(args[0]) <= 6:
        report(where, f"capstone {args[0]} doesn't exist")
    if c == "python" and args:
        check_file(where, args[0])
    if c == "ask" and args:
        check_file(where, args[0] + ".py")

def scan(path, text, history=False):
    """history=True (CHANGELOG, ERRATA, MIGRATION): old ids and names are the point, so check commands only."""
    in_fence = False
    for n, line in enumerate(text.split("\n"), 1):
        where = f"{path.relative_to(KIT)}:{n}"
        if line.startswith("```"):
            in_fence = not in_fence
        # commands, in code spans, code blocks and Run lines
        for m in re.finditer(r"(?:\./course\.sh|\.\\course\.cmd)\s+([^`#\n|;)]+)", line):
            check_command(where, m.group(1).strip().rstrip(".,"))
        if in_fence or history:
            continue
        # exercise ids in prose and exercise boxes
        for m in re.finditer(r"\b[Ee]xercises? ((?:[0-9]+|[PTRSMA])\.[0-9]+)(?:\s*(?:–|-|to|and|,)\s*((?:[0-9]+|[PTRSMA])\.[0-9]+))?", line):
            for g in m.groups():
                if g:
                    check_id(where, g)
        m = re.match(r"^:::ex \w+ \| ([\w.]+) \|", line)
        if m:
            check_id(where, m.group(1))
        # file names in code spans
        for m in re.finditer(r"`([\w./-]+\.(?:py|jsonl?|md|ya?ml|db|sh|cmd|toml|txt|csv|html))`", line):
            check_file(where, m.group(1))
        for m in re.finditer(r"^@@code ([\w./-]+)", line):
            check_file(where, m.group(1))
        # cross-references
        for m in re.finditer(r"\b[Ss]ections? ((?:\d+|[PTRSMA])\.\d+)((?:,? (?:and |to |or |–)?(?:\d+|[PTRSMA])\.\d+)*)", line):
            for s in [m.group(1)] + re.findall(r"(?:\d+|[PTRSMA])\.\d+", m.group(2)):
                if s not in SECTIONS:
                    report(where, f"section {s} doesn't exist")
        for m in re.finditer(r"\bChapters? (\d+)", line):
            if int(m.group(1)) > 30:
                report(where, f"Chapter {m.group(1)} doesn't exist")
        for m in re.finditer(r"\bAppendix ([A-Z])\b", line):
            if m.group(1) not in APPENDICES:
                report(where, f"Appendix {m.group(1)} doesn't exist")
        for m in re.finditer(r"\bCapstone (\d+)", line):
            if not 1 <= int(m.group(1)) <= 6:
                report(where, f"Capstone {m.group(1)} doesn't exist")

for f in sorted(MD.glob("*.md")) + [d for d in DOCS if d.exists()]:
    scan(f, f.read_text(encoding="utf-8"), history=f.name in ("CHANGELOG.md", "ERRATA.md", "MIGRATION.md"))

# every solution file the index promises is there
for i, files in INDEX.items():
    if i not in IDS and not i.startswith("C"):
        report("solutions/index.json", f"solution listed for unknown exercise {i}")
    for rel in files:
        flat = rel.split("/")[-1]
        if not (KIT / "solutions" / rel).exists() and flat not in FILES:
            report("solutions/index.json", f"{i}: {rel} is missing")
# every exercise has a solution or a written answer
answers = (KIT / "solutions/ANSWERS.md").read_text(encoding="utf-8")
for e in EXERCISES:
    if e["id"] not in INDEX and not re.search(r"\*\*" + re.escape(e["id"]) + r" ", answers):
        report("solutions", f"exercise {e['id']} has neither a solution file nor a written answer")

# VERSION_MATRIX.md's versions match what the kit actually installs
LOCK = dict(re.findall(r"^([A-Za-z0-9_.-]+)==(\S+)", (KIT / "requirements.lock").read_text(), re.M))
LOCK = {k.lower(): v for k, v in LOCK.items()}
DOCKER = (KIT / "Dockerfile").read_text(encoding="utf-8")
PRICES_SRC = (KIT / "course/code/ch20/ch20_router.py").read_text(encoding="utf-8")
for n, line in enumerate((KIT / "VERSION_MATRIX.md").read_text(encoding="utf-8").splitlines(), 1):
    cells = [c.strip() for c in line.strip("|").split("|")] if line.startswith("| `") else []
    if len(cells) < 2:
        continue
    names = re.findall(r"`([^`]+)`", cells[0])
    versions = [v.strip() for v in cells[1].split("/")]
    if all(n.lower() in LOCK for n in names) and len(names) == len(versions):
        for name, ver in zip(names, versions):
            if LOCK[name.lower()] != ver.split()[0]:
                report(f"VERSION_MATRIX.md:{n}", f"{name} is {ver}, but requirements.lock pins {LOCK[name.lower()]}")
    elif names and names[0].startswith("claude-"):
        m = re.search(r"\$([\d.]+) / \$([\d.]+)", cells[2] if len(cells) > 2 else "")
        p = re.search(re.escape(f'"{names[0]}": (') + r"([\d.]+), ([\d.]+)\)", PRICES_SRC)
        if not (m and p and float(m.group(1)) == float(p.group(1)) and float(m.group(2)) == float(p.group(2))):
            report(f"VERSION_MATRIX.md:{n}", f"{names[0]}'s price doesn't match PRICES in ch20_router.py")
for pin in ("pip==26.2.1", "uv==0.12.18", "inspector@2.8.0", "server-filesystem@2026.8.31",
            "server-memory@2026.8.31", "mcp-server-git==2026.8.18", "mcp-server-fetch==2026.8.18",
            "mcp-server-time==2026.8.18", "ubuntu:24.04", "python3.12"):
    ver = re.split(r"==|@|:|python", pin)[-1]
    if pin not in DOCKER:
        report("Dockerfile", f"{pin} isn't pinned there any more; update VERSION_MATRIX.md")
    elif ver not in (KIT / "VERSION_MATRIX.md").read_text(encoding="utf-8"):
        report("VERSION_MATRIX.md", f"{pin} is in the Dockerfile but not in the matrix")

# the release matrix states the exercise count of the current tag
vm = (KIT / "VERSION_MATRIX.md").read_text(encoding="utf-8")
row = re.search(r"^\| [^|]+ \| `(edition-[\d.]+)` \| (\d+) \|", vm.split("## Release matrix")[1].split("How to tell")[0].strip().splitlines()[-1], re.M)
if not row or int(row.group(2)) != len(IDS):
    report("VERSION_MATRIX.md", f"the last release row should say {len(IDS)} exercises")

readme_row = re.findall(r"^\| [^|]+printing[^|]*\| (\d+) \| `edition-[\d.]+` \|", (KIT / "README.md").read_text(encoding="utf-8"), re.M)
if not readme_row or int(readme_row[-1]) != len(IDS):
    report("README.md", f"the last row of 'Book editions and code versions' should say {len(IDS)} exercises")

# every listing of code says what kind of code it is (course/code_maturity.json)
MATURITY = json.loads((KIT / "course/code_maturity.json").read_text(encoding="utf-8"))
for f in sorted(MD.glob("*.md")):
    for name in re.findall(r"^@@code ([\w.]+)", f.read_text(encoding="utf-8"), re.M):
        if name.endswith((".py", "Dockerfile")) and MATURITY["files"].get(name) not in MATURITY["_labels"]:
            report(f"course/md/{f.name}", f"{name} has no maturity label in course/code_maturity.json")

if problems:
    print(f"{len(problems)} problems:")
    for p in problems:
        print("  " + p)
    sys.exit(1)
print(f"OK: {len(IDS)} exercises, {len(INDEX)} solution entries, {len(SECTIONS)} sections; "
      "every exercise id, file, command and cross-reference in the book and docs resolves.")
