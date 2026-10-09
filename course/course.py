#!/opt/venv/bin/python
"""course: run every exercise of "Building Agentic AI Systems" inside the course container.

You normally call this through the wrapper on your computer:
    ./course.sh <command>        (macOS / Linux)
    .\\course.cmd <command>       (Windows)
"""
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path

COURSE = Path(os.environ.get("COURSE_HOME", "/opt/course"))   # the image path; tests may point elsewhere
PRISTINE = COURSE / "code"
WS = Path(os.environ.get("COURSE_WORKSPACE", "/workspace"))
EXERCISES = json.loads((COURSE / "exercises.json").read_text())
# Extra practice beyond the book (EXTRA_PRACTICE.md): same commands, ids X.1, X.2, ...
_EXTRAS = COURSE / "extras.json"
EXERCISES += json.loads(_EXTRAS.read_text()) if _EXTRAS.exists() else []
STARTERS = COURSE / "starters"          # starter files with signatures and examples
CHECKS = COURSE / "checks"              # ./course.sh check <id>
CHECK_TARGET = {"3.3": "ch03_tools.py"}   # checked in place
BY_ID = {e["id"]: e for e in EXERCISES}
# Which model each exercise needs: none | any (qwen3.5:9b or Claude) | claude-rec | claude | desktop
_NEEDS = COURSE / "model_needs.json"
for _id_, _need in (json.loads(_NEEDS.read_text()) if _NEEDS.exists() else {}).items():
    if _id_ in BY_ID:
        BY_ID[_id_].update(model=_need["model"], model_note=_need.get("note"))
MODEL_LABEL = {"none": "no model", "any": "qwen3.5:9b or Claude", "claude-rec": "Claude recommended",
               "claude": "Claude only", "desktop": "Claude Desktop app"}

# ---------------------------------------------------------------- model provider
# PROVIDER=claude (default) uses the Claude API with your key. PROVIDER=local uses a free
# model (qwen3.5:9b) served by Ollama, through the local adapter (./course.sh local up).
LOCAL_DEFAULT_MODEL = "qwen3.5:9b"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://local-model:11434").rstrip("/")
ADAPTER_URL = os.environ.get("LOCAL_ADAPTER_URL", "http://local-adapter:8787").rstrip("/")

def is_local():
    return os.environ.get("PROVIDER", "claude").strip().lower() in ("local", "ollama")

def apply_provider():
    """Point every program this command starts at the local model, if PROVIDER=local."""
    if not is_local():
        return
    model = os.environ.get("LOCAL_MODEL") or LOCAL_DEFAULT_MODEL
    os.environ.update({
        "ANTHROPIC_BASE_URL": ADAPTER_URL, "ANTHROPIC_API_URL": ADAPTER_URL,   # SDK, LangChain
        "ANTHROPIC_API_KEY": "sk-local-ollama",        # any value: the local model ignores it
        "MODEL": model, "JUDGE_MODEL": model, "SMALL_MODEL": model,
        # the Agent SDK runs the Claude Code CLI: keep it on the local model and offline
        "ANTHROPIC_DEFAULT_OPUS_MODEL": model, "ANTHROPIC_DEFAULT_SONNET_MODEL": model,
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": model, "ANTHROPIC_SMALL_FAST_MODEL": model,
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        # one reply from a local model on a CPU can take minutes once the context grows
        "MODEL_TIMEOUT": os.environ.get("MODEL_TIMEOUT", "600"),
    })
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
    for var in ("NO_PROXY", "no_proxy"):              # never send local traffic to a proxy
        hosts = [h for h in os.environ.get(var, "").split(",") if h]
        os.environ[var] = ",".join(hosts + ["local-adapter", "local-model", "host.docker.internal"])

def _id(text: str) -> str:
    """'t.2' -> 'T.2', so ids work in any case."""
    return text.upper() if text.upper() in BY_ID else text
TTY = sys.stderr.isatty()

# ---------------------------------------------------------------- output helpers
# Status messages go to STDERR so stdout stays clean (MCP stdio servers need that).
def _c(code, s): return f"\033[{code}m{s}\033[0m" if TTY else s
def say(msg=""): print(msg, file=sys.stderr)
def head(msg): say(_c("1;36", msg))
def ok(msg): say(_c("32", "✔ ") + msg)
def warn(msg): say(_c("33", "! ") + msg)
def fail(msg): say(_c("31", "✘ ") + msg)

def env_for_runs():
    env = dict(os.environ)
    # Include chapter subdirectories in PYTHONPATH so exercises can import modules directly
    # e.g., import ch03_tools from course/code/ch03/ch03_tools.py
    chapter_paths = [str(PRISTINE / f"ch{i:02d}") for i in range(31)]
    interlude_paths = [str(PRISTINE / d) for d in ["interlude_python", "interlude_regex", "interlude_sql", "interlude_testing", "interlude_measure"]]
    all_code_paths = ":".join(chapter_paths + interlude_paths)
    env["PYTHONPATH"] = f"{all_code_paths}:{PRISTINE}:{WS}:{WS / 'exercises'}:{env.get('PYTHONPATH', '')}".rstrip(":")
    return env

def host_path(p: Path) -> str:
    """How a workspace path looks on your computer."""
    rel = Path(p).resolve().relative_to(WS)
    return str(Path("workspace") / rel)

# ---------------------------------------------------------------- workspace setup
def pristine_files():
    """Every course source/data file. The code is organised into chapter subfolders
    (ch04/, ch08/, ...), but the workspace is flat, so we gather files at any depth and
    key them by basename (course filenames are unique)."""
    return [p for p in sorted(PRISTINE.rglob("*"))
            if p.is_file() and not {"__pycache__", "_index"} & set(p.parts)
            and p.suffix != ".pyc" and p.name not in ("__init__.py", ".gitkeep")]

def copy_pristine(dst):
    """Copy the book's code into dst, flat (the workspace layout)."""
    for src in pristine_files():
        shutil.copy2(src, dst / src.name)

def init(force=False, quiet=True):
    marker = WS / ".course" / "initialized"
    if marker.exists() and not force:
        # A newer kit may bring new chapter files: add those, never touch existing ones.
        new = [src for src in pristine_files() if not (WS / src.name).exists()]
        try:
            for src in new:
                shutil.copy2(src, WS / src.name)
        except OSError as exc:
            warn(f"Couldn't add new course files to your workspace ({exc.strerror}); "
                 "check the folder's permissions.")
            return
        if new:
            ok(f"Added {len(new)} new course file(s) to your workspace: "
               + ", ".join(sorted(p.name for p in new)[:6]) + (" ..." if len(new) > 6 else ""))
        return
    WS.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src in pristine_files():
        dst = WS / src.name
        if force or not dst.exists():
            if dst.exists():
                shutil.copy2(dst, dst.with_suffix(dst.suffix + ".bak"))
            shutil.copy2(src, dst)
            copied += 1
    for d in ("exercises", "tests", "answers", ".course"):
        (WS / d).mkdir(exist_ok=True)
    if not (WS / "tests" / "conftest.py").exists():
        (WS / "tests" / "conftest.py").write_text(
            "import sys\nsys.path.insert(0, '/workspace')\n")
    sys.path.insert(0, str(COURSE / "data"))
    import generate
    cwd = os.getcwd()
    generate.all_data(WS)
    os.chdir(cwd)
    if not (WS / ".git").exists():        # chapter 14's Git server needs a repository
        subprocess.run(["git", "init", "-q"], cwd=WS)
        (WS / ".gitignore").write_text(".env\n.course/\n.sandbox/\n__pycache__/\n*.bak\n")
        subprocess.run(["git", "add", "-A"], cwd=WS, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-qm", "Course starting point"], cwd=WS,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    marker.write_text(time.ctime())
    if not quiet or copied:
        ok(f"Workspace ready: {copied} course files copied into your 'workspace' folder.")

# ---------------------------------------------------------------- listing
LEVEL_COLOR = {"Concept": "34", "Simple": "32", "Medium": "33", "Complex": "31"}

def cmd_list(args):
    chapter = args[0].upper() if args else None
    current = None
    for e in EXERCISES:
        ch = e["id"].split(".")[0]
        if chapter and ch != chapter:
            continue
        if e["chapter"] != current:
            current = e["chapter"]
            head(f"\n{current}")
        done = _status(e)
        lvl = _c(LEVEL_COLOR[e["level"]], f"{e['level']:<8}")
        need = e.get("model", "any")
        tag = {"none": "", "any": "", "claude-rec": _c("33", "Claude recommended"),
               "claude": _c("31", "Claude only"), "desktop": _c("33", "Claude Desktop")}[need]
        say(f"  {e['id']:<5} {lvl} {e['title']:<42} {tag} {done}".rstrip())
    say("\nRun one with:  ./course.sh ex <id>      e.g.  ./course.sh ex 4.2")

def _status(e):
    f = _my_file(e)
    if f and f.exists():
        return _c("2", f"[{host_path(f)}]")
    return ""

def _my_file(e):
    if e["kind"] == "concept":
        return WS / "answers" / f"ex{e['id'].replace('.', '_')}.md"
    if e.get("file"):
        return WS / e["file"]
    if e["kind"] == "inspector" and e.get("stub"):
        return WS / e["server"]
    return None

# ---------------------------------------------------------------- exercise brief
def brief(e):
    lvl = _c(LEVEL_COLOR[e["level"]], e["level"].upper())
    head(f"\nExercise {e['id']} · {e['title']}")
    say(f"{lvl}  ·  {e['chapter']}")
    need = e.get("model", "any")
    say(_c("1", "Model: ") + MODEL_LABEL[need] + (f". {e['model_note']}" if e.get("model_note") else ""))
    if is_local() and need in ("claude", "claude-rec"):
        warn("You're using the local model (PROVIDER=local). "
             + ("This exercise needs Claude: set PROVIDER=claude in .env to run it."
                if need == "claude" else "It runs, but works much better with Claude."))
    say("")
    for para in [e["task"]]:
        say(textwrap.fill(para, 88))
    if e.get("hint"):
        say("\n" + _c("1", "Hint: ") + textwrap.fill(e["hint"], 82))
    if e.get("done_when"):
        say(_c("1", "Done when: ") + textwrap.fill(e["done_when"], 78))
    if e.get("edit"):
        say(_c("1", "Files to edit: ") + ", ".join(f"workspace/{f}" for f in e["edit"]))
    if has_check(e):
        say(_c("2", f"Check your answer automatically:   ./course.sh check {e['id']}"))
    say(_c("2", f"Stuck, or finished and want to compare? ./course.sh solution {e['id']}"))
    say("")

STUB_PY = '''"""Exercise {id} ({level}): {title}

{task}

Hint: {hint}
Done when: {done}

Edit this file on your computer (workspace/{file}), then run:
    ./course.sh ex {id}
"""
{imports}

def main():
    # TODO: write your solution here.
    raise NotImplementedError("Exercise {id} is not written yet. Edit workspace/{file}")


if __name__ == "__main__":
    main()
'''

STUB_TEST = '''"""Exercise {id} ({level}): {title}

{task}

Done when: {done}

Write your tests below, then run:   ./course.sh ex {id}
"""
import pytest


def test_todo():
    pytest.fail("Exercise {id}: write your tests in workspace/{file}")
'''

STUB_SERVER = '''"""Exercise {id} ({level}): {title}

{task}

Edit this file, then run:   ./course.sh ex {id}   (opens MCP Inspector)
"""
import logging
import sys
from mcp.server import MCPServer

logging.basicConfig(stream=sys.stderr, level=logging.INFO)   # never print() to stdout
mcp = MCPServer("my-server")


@mcp.tool()
def example(text: str) -> str:
    """Replace this example tool with your own tools."""
    return text.upper()


if __name__ == "__main__":
    mcp.run(transport="stdio")
'''

CONCEPT_MD = '''# Exercise {id} ({level}): {title}

{task}

{hint_line}**Done when:** {done}

## My answer

'''

def _fill(tmpl, e, **extra):
    wrap = lambda s: textwrap.fill(s or "", 80)
    head_ = e["id"].split(".")[0]
    chapter = int(head_) if head_.isdigit() else 0
    imports = "import os\nfrom anthropic import Anthropic\n\nMODEL = os.environ.get(\"MODEL\", \"claude-sonnet-5\")"
    if chapter >= 4:
        imports += "\nfrom ch04_agent import run_agent   # the agent loop from chapter 4"
    return tmpl.format(id=e["id"], level=e["level"], title=e["title"], task=wrap(e["task"]),
                       hint=wrap(e.get("hint") or "-"), done=wrap(e.get("done_when") or "-"),
                       file=e.get("file") or e.get("server", ""), imports=imports,
                       hint_line=(f"**Hint:** {e['hint']}\n\n" if e.get("hint") else ""), **extra)

def ensure_starter(e):
    """Create your starter file the first time. Returns (path, created)."""
    path = _my_file(e)
    if path is None or path.exists():
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    starter = STARTERS / path.name
    if e["kind"] in ("build", "test") and starter.exists():
        path.write_text(_starter_text(e, starter.read_text()))
        return path, True
    tmpl = {"concept": CONCEPT_MD, "build": STUB_PY, "test": STUB_TEST,
            "inspector": STUB_SERVER}[e["kind"]]
    path.write_text(_fill(tmpl, e))
    return path, True

def has_check(e) -> bool:
    return (CHECKS / f"check_{e['id'].replace('.', '_')}.py").exists()

def _starter_text(e, body: str) -> str:
    """The exercise text as a header, then the starter code (functions to fill in)."""
    notes = ""
    if body.lstrip().startswith('"""'):                 # the starter's own notes go in the header
        start = body.index('"""') + 3
        end = body.index('"""', start)
        notes, body = body[start:end].strip() + "\n\n", body[end + 3:].lstrip("\n")
    wrap = lambda t: textwrap.fill(t or "", 80)
    lines = [f"Exercise {e['id']} ({e['level']}): {e['title']}", "", wrap(e["task"]), ""]
    if e.get("hint"):
        lines += [wrap("Hint: " + e["hint"]), ""]
    lines += [wrap("Done when: " + (e.get("done_when") or "-")), ""]
    if notes:
        lines += [notes.rstrip(), ""]
    lines.append(f"Fill in the TODOs, then run:   ./course.sh ex {e['id']}")
    if has_check(e):
        lines.append(f"Check your answer:            ./course.sh check {e['id']}")
    return '"""' + "\n".join(lines) + '\n"""\n' + body

# ---------------------------------------------------------------- requirements
def need_api_key():
    if is_local():
        return True
    if not os.environ.get("ANTHROPIC_API_KEY", "").startswith("sk-"):
        warn("ANTHROPIC_API_KEY is not set. Copy .env.example to .env next to course.sh "
             "and add your key, or use the free local model (PROVIDER=local, see Appendix H).")
        return False
    return True

def sandbox_alive():
    hb = WS / ".sandbox" / "heartbeat"
    return hb.exists() and time.time() - float(hb.read_text() or 0) < 10

def check_needs(e):
    need = e.get("needs")
    if need == "sandbox" and not sandbox_alive():
        fail("This exercise needs the isolated test sandbox. On your computer run:")
        say("    ./course.sh sandbox up        (stop it later with: ./course.sh sandbox down)")
        return False
    if need == "github" and not os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"):
        fail("This exercise needs GITHUB_PERSONAL_ACCESS_TOKEN in your .env file "
             "(a read-only fine-grained token).")
        return False
    return True

# ---------------------------------------------------------------- running things
def sh(command, check=False):
    head(f"$ {command}")
    return subprocess.run(["bash", "-c", command], cwd=WS, env=env_for_runs()).returncode

def cmd_ex(args):
    if not args:
        return cmd_list([])
    args = [_id(args[0])] + list(args[1:])
    e = BY_ID.get(args[0])
    if not e:
        fail(f"No exercise '{args[0]}'. See: ./course.sh list")
        return 2
    brief(e)
    if "--info" in args:
        return 0
    if not check_needs(e):
        return 1
    path, created = ensure_starter(e)
    kind = e["kind"]
    if kind == "concept":
        verb = "Created" if created else "Your answer file is"
        ok(f"{verb}: {host_path(path)}  — open it in any editor and write your answer.")
        return 0
    if e.get("setup"):
        sh(e["setup"])
    if kind in ("run", "build") and not e.get("nokey"):
        need_api_key()          # a warning only
    if kind in ("build", "test") and created:
        ok(f"Created your starter file: {host_path(path)}")
        say("   Write your solution there (it's on your computer), then run this command again.")
        return 0
    if kind == "run":
        return sh(e["cmd"])
    if kind == "ask":
        return cmd_ask([e["module"]] + ([e["question"]] if e.get("question") else []))
    if kind == "build":
        return sh(f"python {e['file']}")
    if kind == "test":
        return sh(f"python -m pytest -q {e['file']}")
    if kind == "inspector":
        if created:
            ok(f"Created your starter server: {host_path(path)}")
        return cmd_inspector([e["server"]])
    if kind == "desktop":
        return cmd_desktop_config([e["server"]])
    return 0

def cmd_ask(args):
    """Chat with any chapter's tools:  course ask ch06_notes_tools ["question"]"""
    if not args:
        fail("Usage: ./course.sh ask <module> [\"question\"]   e.g. ask ch08_sql_tools")
        return 2
    need_api_key()
    os.chdir(WS)
    sys.path.insert(0, str(WS))
    mod = importlib.import_module(args[0].removesuffix(".py"))
    from ch04_agent import run_agent
    system = getattr(mod, "SYSTEM", "You are a helpful assistant. Use the tools.")
    if len(args) > 1:
        answer, _, stats = run_agent(" ".join(args[1:]), mod.TOOLS, mod.run_tool, system=system)
        print(f"\n{answer}\n")
        say(_c("2", f"[{stats}]"))
        return 0
    head(f"Chatting with the {args[0]} tools. Type 'quit' to stop.")
    history = []
    while True:
        try:
            q = input("\nYou: ").strip()
        except EOFError:
            break
        if q in ("quit", "exit", ""):
            break
        answer, history, stats = run_agent(q, mod.TOOLS, mod.run_tool, system=system,
                                           messages=history)
        print(f"\nAgent: {answer}")
        say(_c("2", f"[{stats['tool_calls']} tool calls, "
                    f"{stats['input_tokens'] + stats['output_tokens']} tokens]"))
    return 0

def cmd_inspector(args):
    if not args:
        fail("Usage: ./course.sh inspector <server.py> [--cli]")
        return 2
    server = args[0]
    if "--cli" in args:
        rest = [a for a in args[1:] if a != "--cli"] or ["--method", "tools/list"]
        return subprocess.call(["mcp-inspector", "--cli", "python", server, *rest],
                               cwd=WS, env=env_for_runs())
    env = env_for_runs() | {"HOST": "0.0.0.0", "DANGEROUSLY_BIND_ALL_INTERFACES": "true",
                            "MCP_AUTO_OPEN_ENABLED": "false"}
    head("Starting MCP Inspector. Open the http://localhost:6274 link below in your browser.")
    say("(The Inspector is published only to your own computer. Press Ctrl+C to stop.)\n")
    return subprocess.call(["mcp-inspector", "--web", "python", server], cwd=WS, env=env)

def cmd_serve(args):
    """Run an MCP server over Streamable HTTP on http://localhost:8000/mcp"""
    server = args[0] if args else "ch12_weather_server.py"
    head(f"Serving {server} at http://localhost:8000/mcp  (Ctrl+C to stop)")
    env = env_for_runs() | {"MCP_HOST": "0.0.0.0"}
    return subprocess.call(["python", server, "streamable-http"], cwd=WS, env=env)

def cmd_serve_api(args):
    """Chapter 30: the agent as a web API on http://localhost:8080 (docs at /docs)"""
    need_api_key()
    if not os.environ.get("AGENT_API_KEYS", "").strip():
        import secrets
        fail("AGENT_API_KEYS is not set, so the API would have no protection. Add this line "
             "to the .env file next to course.sh, then run serve-api again:")
        say(f"    AGENT_API_KEYS={secrets.token_urlsafe(24)}")
        return 1
    head("Agent API at http://localhost:8080   (interactive docs: http://localhost:8080/docs)")
    say("Other course containers reach it as http://agentic-ai-api:8080. Ctrl+C to stop.")
    env = env_for_runs()
    return subprocess.call(["python", "-m", "uvicorn", "ch30_service:app", "--host", "0.0.0.0",
                            "--port", "8080", *args], cwd=WS, env=env)

def cmd_serve_mcp(args):
    """Chapter 30: the token-protected remote MCP server on http://localhost:8000/mcp"""
    if not os.environ.get("MCP_TOKEN", "").strip():
        import secrets
        fail("MCP_TOKEN is not set. Add these lines to the .env file next to course.sh "
             "(the second is optional: a token that can only read), then run serve-mcp again:")
        say(f"    MCP_TOKEN={secrets.token_urlsafe(24)}\n    MCP_READONLY_TOKEN={secrets.token_urlsafe(24)}")
        return 1
    head("Remote MCP server at http://localhost:8000/mcp   (needs 'Authorization: Bearer <MCP_TOKEN>')")
    say("Other course containers reach it as http://agentic-ai-mcp:8000/mcp. Ctrl+C to stop.")
    env = env_for_runs() | {"MCP_HOST": "0.0.0.0"}
    return subprocess.call(["python", "ch30_remote_mcp.py", *args], cwd=WS, env=env)

def cmd_serve_a2a(args):
    """The Chapter 21 A2A analyst agent on port 9999 (use ./course.sh serve-a2a)."""
    need_api_key()
    head("A2A agent card: http://localhost:9999/.well-known/agent-card.json   (Ctrl+C stops it)")
    os.chdir(WS)
    env = env_for_runs() | {"A2A_HOST": "0.0.0.0"}
    os.execvpe(sys.executable, [sys.executable, "ch21_a2a_server.py"], env)

def cmd_desktop_config(args):
    server = args[0] if args else "ch12_weather_server.py"
    host_dir = os.environ.get("COURSE_HOST_DIR") or "/ABSOLUTE/PATH/TO/building-agentic-ai"
    compose = str(Path(host_dir) / "compose.yaml") if "\\" not in host_dir \
        else host_dir.rstrip("\\") + "\\compose.yaml"
    name = Path(server).stem.replace("ch12_", "").replace("_server", "")
    config = {"mcpServers": {name: {"command": "docker", "args": [
        "compose", "-f", compose, "run", "--rm", "-T", "course", "python", server]}}}
    head("Add this to Claude Desktop's config (Settings → Developer → Edit Config):\n")
    print(json.dumps(config, indent=2))
    say("\nThen fully quit and restart Claude Desktop. Docker Desktop must be running.")
    return 0

def cmd_data(args):
    import argparse
    p = argparse.ArgumentParser(prog="course data")
    p.add_argument("kind", choices=["notes", "library", "messy", "repo", "db", "traces", "all"])
    p.add_argument("--count", type=int, default=0)
    p.add_argument("--out")
    p.add_argument("--fresh", action="store_true", help="replace existing data")
    a = p.parse_args(args)
    sys.path.insert(0, str(COURSE / "data"))
    import generate
    os.chdir(WS)
    if a.kind == "notes":
        generate.notes(a.count, a.out or "notes")
    elif a.kind == "library":
        generate.library(a.out or "library")
    elif a.kind == "messy":
        out = Path(a.out or "messy")
        if a.fresh and out.exists():
            shutil.rmtree(out)
        generate.messy(a.count or 15, str(out))
    elif a.kind == "repo":
        if a.fresh and Path("buggy_repo").exists():
            shutil.rmtree("buggy_repo")
        generate.run_script("ch10_make_repo.py")
    elif a.kind == "db":
        generate.run_script("ch08_make_db.py")
    elif a.kind == "traces":
        generate.traces(a.count or 60, a.out or "traces.jsonl")
    else:
        generate.all_data(WS)
    return 0

def cmd_reset(args):
    if not args:
        fail("Usage: ./course.sh reset <file>   (restores the original course file)")
        return 2
    by_name = {p.name: p for p in pristine_files()}
    for name in args:
        src = by_name.get(Path(name).name)
        if src is None:
            fail(f"{name} is not a course file.")
            continue
        dst = WS / src.name
        if dst.exists():
            shutil.copy2(dst, dst.with_suffix(dst.suffix + ".bak"))
            say(f"  your version saved as {host_path(dst)}.bak")
        shutil.copy2(src, dst)
        ok(f"Restored {src.name}")
    return 0

# ---------------------------------------------------------------- sandbox worker
def _limit_resources():
    """Runs in the child before the test command: hard limits it can't raise."""
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))          # 1 GB of memory
    resource.setrlimit(resource.RLIMIT_FSIZE, (50 << 20, 50 << 20))     # 50 MB per file
    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))                 # 2 CPU-minutes

def _run_job(job):
    """Copy the job's folder into a fresh temporary folder and run the command THERE,
    in its own process group. The model-written code never touches /workspace, can't
    import your course files, and every process it started is killed afterwards."""
    import signal
    import tempfile
    cwd = Path(job.get("cwd", str(WS))).resolve()
    if cwd != WS and WS not in cwd.parents:
        return "ERROR: sandbox jobs must run inside /workspace", 1
    with tempfile.TemporaryDirectory(prefix="job-") as tmp:
        work = Path(tmp) / cwd.name
        shutil.copytree(cwd, work, ignore=shutil.ignore_patterns(".git", "__pycache__", ".sandbox"))
        proc = subprocess.Popen(job["cmd"], cwd=work, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, start_new_session=True,
                                preexec_fn=_limit_resources,
                                env={"PATH": os.environ["PATH"], "HOME": tmp,
                                     "PYTHONDONTWRITEBYTECODE": "1", "LANG": "C.UTF-8"})
        try:
            out, _ = proc.communicate(timeout=min(int(job.get("timeout", 60)), 600))
            code = proc.returncode
        except subprocess.TimeoutExpired:
            out, code = "ERROR: timed out in the sandbox", 124
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)     # also kills anything it left running
            except ProcessLookupError:
                pass
            proc.wait()
    return (out or "")[-6000:], code

def cmd_sandbox_worker(args):
    """Runs in the network-less `sandbox` service; executes queued test jobs."""
    q = WS / ".sandbox"
    (q / "requests").mkdir(parents=True, exist_ok=True)
    (q / "results").mkdir(parents=True, exist_ok=True)
    say("sandbox worker: waiting for jobs (no network, no secrets, read-only workspace)")
    while True:
        if not WS.exists():                  # workspace removed (e.g. a test run ended)
            return 0
        try:
            (q / "heartbeat").write_text(str(time.time()))
        except OSError:
            (q / "requests").mkdir(parents=True, exist_ok=True)
            (q / "results").mkdir(parents=True, exist_ok=True)
            continue
        for req in sorted((q / "requests").glob("*.json")):
            try:
                job = json.loads(req.read_text())
            finally:
                req.unlink(missing_ok=True)
            try:
                out, code = _run_job(job)
            except Exception as exc:
                out, code = f"ERROR: {type(exc).__name__}: {exc}", 1
            say(f"sandbox worker: job {job.get('id')} exit={code}")
            tmp = q / "results" / f"{job['id']}.tmp"
            tmp.write_text(json.dumps({"output": out, "returncode": code}))
            tmp.rename(q / "results" / f"{job['id']}.json")
        time.sleep(0.3)

# ---------------------------------------------------------------- diagnostics
def _ver(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).strip().splitlines()[0] if r.returncode == 0 else None
    except Exception:
        return None

def cmd_check_exercise(e):
    """Run the automatic checks for one exercise against YOUR file."""
    target = WS / CHECK_TARGET.get(e["id"], e.get("file") or "")
    if not target.is_file():
        fail(f"Your file {host_path(target) if WS in target.parents else target} doesn't exist yet.")
        say(f"    Create it first with:  ./course.sh ex {e['id']}")
        return 1
    head(f"Checking exercise {e['id']} ({host_path(target)})")
    env = env_for_runs() | {"EXERCISE_FILE": str(target), "PYTHONDONTWRITEBYTECODE": "1"}
    check = CHECKS / f"check_{e['id'].replace('.', '_')}.py"
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short", "--no-header",
                        "-p", "no:cacheprovider", "--rootdir", str(CHECKS), str(check)],
                       cwd=WS, env=env, capture_output=True, text=True)
    if r.returncode == 0:
        ok(f"All checks passed for {e['id']}. Compare with the solution: ./course.sh solution {e['id']}")
        return 0
    out = r.stdout
    unfinished = re.findall(r"^FAILED \S+::(\w+) - NotImplementedError", out, re.M)
    if unfinished:
        warn("Not written yet (still raise NotImplementedError): "
             + ", ".join(t.removeprefix("test_") for t in unfinished))
    messages = re.findall(r"^E\s+AssertionError: (.+)$", out, re.M)
    for m in dict.fromkeys(messages):                      # unique, in order
        fail(m)
    if not messages and not unfinished:
        say(out[-2500:])
    summary = out.strip().splitlines()[-1] if out.strip() else ""
    say(_c("2", summary))
    return 1

def cmd_check(args):
    if args and not args[0].startswith("-"):
        e = BY_ID.get(_id(args[0]))
        if not e:
            fail(f"No exercise '{args[0]}'. See: ./course.sh list")
            return 2
        if not has_check(e):
            warn(f"Exercise {e['id']} has no automatic check. Compare with: ./course.sh solution {e['id']}")
            return 0
        return cmd_check_exercise(e)
    head("Environment check")
    import anthropic
    import mcp
    from importlib.metadata import version
    rows = [
        ("Python", sys.version.split()[0]),
        ("anthropic SDK", version("anthropic")),
        ("mcp SDK", version("mcp")),
        ("Node.js", _ver(["node", "--version"])),
        ("MCP Inspector", "installed" if shutil.which("mcp-inspector") else None),
        ("Filesystem server", "installed" if shutil.which("mcp-server-filesystem") else None),
        ("Memory server", "installed" if shutil.which("mcp-server-memory") else None),
        ("Git server", "installed" if shutil.which("mcp-server-git") else None),
        ("Fetch server", "installed" if shutil.which("mcp-server-fetch") else None),
        ("Time server", "installed" if shutil.which("mcp-server-time") else None),
        ("GitHub server", "installed" if shutil.which("github-mcp-server") else None),
        ("Provider (PROVIDER)", "local: free model through Ollama" if is_local() else "claude: the Claude API"),
        ("Model (MODEL)", os.environ.get("MODEL")),
        ("ANTHROPIC_API_KEY", "not needed (local model)" if is_local()
         else "set" if os.environ.get("ANTHROPIC_API_KEY") else None),
        ("GitHub token", "set" if os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
         else "not set (only needed for 14.3, 14.4, capstone 4)"),
        ("Sandbox (chapter 10)", "running" if sandbox_alive()
         else "stopped (start with ./course.sh sandbox up when needed)"),
    ]
    bad = 0
    for name, val in rows:
        if val:
            ok(f"{name:<22} {val}")
        else:
            fail(f"{name:<22} missing")
            bad += 1
    if "--api" in args and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            r = anthropic.Anthropic().messages.create(
                model=os.environ.get("MODEL", "claude-sonnet-5"), max_tokens=1000,
                messages=[{"role": "user", "content": "Reply with the word ready."}])
            reply = "".join(b.text for b in r.content if b.type == "text").strip()
            ok(f"{'API call':<22} {reply} ({r.model})")
        except Exception as exc:
            fail(f"{'API call':<22} {type(exc).__name__}: {str(exc)[:600]}")
            bad += 1
    elif "--api" not in args:
        say(_c("2", "\nAdd --api to also make one tiny test call to the model."))
    return 1 if bad else 0

def _cost(name: str) -> str:
    """A figure from course/cost.json, written by dev/cost_model.py (the book quotes the same file)."""
    try:
        return json.loads((COURSE / "cost.json").read_text())[name]
    except Exception:
        return "see COST_MODEL.md"

def cmd_quickstart(args):
    """Your first agent with a scripted stand-in model: no API key, no download."""
    os.chdir(WS)
    return subprocess.call([sys.executable, "quickstart.py"], env=env_for_runs())

def cmd_selftest(args):
    return subprocess.call([sys.executable, str(COURSE / "selftest" / "selftest.py")])


# ---------------------------------------------------------------- solutions
SOLUTIONS = Path("/solutions")

def flatten_solutions():
    """The solutions are organised into chapter subfolders (exercises/ch04/, ...), but the
    runner, index.json and the reference tests expect one flat exercises/ folder. Build a
    flat read-only copy in /tmp and point SOLUTIONS at it."""
    global SOLUTIONS
    import tempfile
    ex = SOLUTIONS / "exercises"
    if not ex.is_dir() or not any(d.is_dir() and d.name.startswith("ch") for d in ex.iterdir()):
        return
    flat = Path(tempfile.gettempdir()) / "solutions-flat"
    shutil.rmtree(flat, ignore_errors=True)
    shutil.copytree(SOLUTIONS, flat, symlinks=True,
                    ignore=shutil.ignore_patterns("outputs", "exercises", "__pycache__"))
    (flat / "exercises").mkdir()
    grouping = re.compile(r"ch\d+|capstones|interludes?(_\w+)?")   # the chapter folders
    for d in sorted(ex.iterdir()):
        if d.name in ("_index", "__pycache__"):
            continue
        if d.is_file():
            shutil.copy2(d, flat / "exercises" / d.name)
        elif not grouping.fullmatch(d.name):              # a real package, e.g. skills/
            shutil.copytree(d, flat / "exercises" / d.name,
                            ignore=shutil.ignore_patterns("__pycache__"))
        else:
            for src in sorted(d.rglob("*")):
                if (src.is_file() and "__pycache__" not in src.parts
                        and src.name not in ("__init__.py", ".gitkeep")):
                    shutil.copy2(src, flat / "exercises" / src.name)
    SOLUTIONS = flat

def cmd_solution(args):
    if not (SOLUTIONS / "index.json").exists():
        fail("The 'solutions' folder is missing. It should sit next to course.sh.")
        return 1
    if not args:
        say((SOLUTIONS / "README.md").read_text())
        return 0
    index = json.loads((SOLUTIONS / "index.json").read_text())
    args = [_id(args[0])] + list(args[1:])
    e = BY_ID.get(args[0])
    if e and e["kind"] == "concept":
        index.setdefault(args[0], ["ANSWERS.md"])
    files = index.get(args[0])
    if not files:
        fail(f"No reference solution listed for {args[0]}.")
        return 1
    import re
    # Shared automated checks (tests/test_chNN_*.py) cover many exercises: point to them only.
    shared = [f for f in files if re.match(r"tests/test_ch\d", f)] if len(files) > 1 else []
    for f in files:
        if f in shared:
            continue
        path = SOLUTIONS / f
        head(f"\n===== solutions/{f} =====")
        text = path.read_text()
        if f == "ANSWERS.md":           # just this exercise: from its heading to the next one
            text = _answer_for(args[0], text) or text
        print(text)
    for f in shared:
        say(_c("2", f"\nAutomated check for this exercise: solutions/{f}"))
    return 0

def _answer_for(ex_id, text):
    """Exercise ex_id's part of ANSWERS.md (from its heading to the next one), or None."""
    m = re.search(rf"^\*\*(?:[\w.]+ and )?{re.escape(ex_id)}[ *].*?"
                  rf"(?=^\*\*[0-9A-Z]+\.\d+[ *]|^## |\Z)", text, re.S | re.M)
    return m.group(0).strip() if m else None

CAPSTONES = {  # number: (folder, data script or None, program, default arguments)
    "1": ("c1_support", "data.py", "agent.py", []),
    "2": ("c2_analyst", None, "agent.py", []),
    "3": ("c3_incident", "data.py", "agent.py", []),
    "4": ("c4_review", "data.py", "agent.py", []),
    "5": ("c5_research", None, "research.py", []),
    "6": ("c6_backoffice", "data.py", "agent.py", []),
    "7": ("c7_engagement", "data.py", "engagement.py", []),
}

def cmd_capstone(args):
    """Run a reference capstone:  capstone <1-7> [arguments]"""
    if not args or args[0] not in CAPSTONES:
        head("Reference capstones (build your own first!):")
        for n, (folder, _, prog, _) in CAPSTONES.items():
            say(f"  ./course.sh capstone {n}     solutions/capstones/{folder}/{prog}")
        return 0 if not args else 2
    folder, data, prog, default = CAPSTONES[args[0]]
    base = SOLUTIONS / "capstones" / folder
    if not base.exists():
        fail("The 'solutions' folder is missing. It should sit next to course.sh.")
        return 1
    need_api_key()
    env = env_for_runs()
    env["PYTHONPATH"] = f"{SOLUTIONS / 'capstones'}:{SOLUTIONS / 'exercises'}:{env['PYTHONPATH']}"
    if data:
        head(f"Generating capstone {args[0]} sample data...")
        subprocess.call([sys.executable, str(base / data)], cwd=WS, env=env)
    head(f"Running solutions/capstones/{folder}/{prog}")
    return subprocess.call([sys.executable, str(base / prog), *(args[1:] or default)], cwd=WS, env=env)

def cmd_verify_solutions(args):
    env = env_for_runs() | {"COURSE_CODE": str(PRISTINE), "COURSE_DATA": str(COURSE / "data"),
                            "COURSE_EXERCISES": str(COURSE / "exercises.json"),
                            "PYTHONDONTWRITEBYTECODE": "1"}
    env["PYTHONPATH"] = f"{SOLUTIONS / 'capstones'}:{SOLUTIONS / 'exercises'}"
    head("Running every reference solution, capstone and exercise command (offline)...")
    return subprocess.call([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                            "--rootdir", "/tmp", str(SOLUTIONS / "tests"), *args],
                           cwd="/tmp", env=env)


# ---------------------------------------------------------------- live check
# Every chapter's main file, run against the real model, in a scratch copy of your
# workspace with the ORIGINAL chapter files (your edits are never used or touched).
# (part, file and args, text typed at the keyboard, rough cost in US cents)
LIVE_RUNS = [
    ("1", "ch01_summarize.py", "", 1), ("1", "ch01_where_llms_fail.py", "", 1),
    ("1", "ch02_first_tool.py", "", 1), ("1", "ch02_calculator_agent.py", "", 1),
    ("1", "ch03_structured.py", "", 1), ("1", "ch03_routing_eval.py", "", 3),
    ("1", "ch04_agent.py", "", 2),
    ("2", "ch05_todo_tools.py", "Add a task: buy milk tomorrow\nWhat is on my list?\nquit\n", 2),
    ("2", "ch06_notes_tools.py", "", 3),
    ("3", "ch07_weather_tools.py", "", 2), ("3", "ch08_sql_tools.py", "", 3),
    ("3", "ch09_organizer.py", "n\n" * 10, 3),
    ("4", "ch10_fixer.py", "", 6), ("4", "ch11_research_team.py", "", 10),
    ("5", "ch13_mcp_agent.py servers.json", "How many open tasks are there?\nquit\n", 3),
    ("5", "ch14_policy_agent.py", "What time is it in Tokyo?\n" + "n\n" * 4 + "quit\n", 4),
    ("5", "ch15_modern.py", "", 0),
    ("6", "ch16_context.py", "", 5), ("6", "ch17_memory.py", "Remember that I prefer Celsius.\nquit\n", 2),
    ("6", "ch16_assemble.py", "", 1), ("6", "ch18_rag.py", "", 3), ("6", "ch18_agentic.py", "", 4),
    ("7", "ch19_durable.py", "", 1), ("7", "ch19_harness.py", "", 5),
    ("7", "ch20_planning.py", "", 5), ("7", "ch20_router.py", "", 5),
    ("7", "ch21_orchestrator.py", "", 6), ("7", "ch22_guarded.py", "n\n" * 3, 3),
    ("7", "ch23_browser.py", "", 5),
    ("7", "ch24_tool_runner.py", "", 3),
    ("7", "ch24_langchain.py", "", 3), ("7", "ch24_agent_sdk.py", "", 5),
    ("8", "ch25_quarantine.py", "", 3), ("8", "ch25_guards.py", "", 2),
    ("8", "ch26_identity.py", "n\n" * 2, 2),
    ("9", "ch27_eval.py", "", 15), ("9", "ch27_judge.py", "", 5),
    ("9", "ch27_trajectory.py", "", 5), ("9", "ch28_otel.py", "", 2),
    ("9", "ch28_agentops.py spans.jsonl", "", 0), ("9", "ch29_costs.py", "", 0),
    ("9", "ch27_scorecard.py", "", 0), ("9", "ch28_ops.py", "", 0), ("9", "ch29_perf.py", "", 0),
    ("9", "ch30_jobs_server.py", "", 0), ("9", "ch30_gateway.py", "", 0),
    # offline demos added in the corrected printing: no model, so they cost nothing
    ("6", "ch17_memory_security.py", "", 0), ("7", "ch21_coordination.py", "", 0),
    ("7", "ch23_reliability.py", "", 0), ("7", "ch24_skill_registry.py", "", 0),
    ("8", "ch25_risk.py", "", 0), ("8", "ch26_discovery.py", "", 0),
    ("9", "ch28_profile.py", "", 0), ("9", "ch29_economics.py", "", 0),
    ("9", "ch30_improvement_loop.py", "", 0),
]

def cmd_live_check(args):
    """Run every chapter's main file against the real model and write a report."""
    import tempfile
    if not need_api_key():
        return 1
    if args[:1] == ["exercises"]:
        return cmd_live_exercises(args[1:])
    parts = [a for a in args if not a.startswith("-")]
    runs = [r for r in LIVE_RUNS if not parts or r[0] in parts]
    cents = sum(r[3] for r in runs)
    head(f"Live check: {len(runs)} chapter files against {os.environ.get('MODEL', 'claude-sonnet-5')}")
    if is_local():
        say("Local model: free, but slow on a CPU (allow an hour or more). "
            "Your own files are not used or changed.")
    else:
        say(f"Estimated cost: about ${cents / 100:.2f}. Your own files are not used or changed.")
    if "--yes" not in args and input("Continue? [y/N] ").strip().lower() != "y":
        return 0
    rows, report = [], ["# Live check report", "",
                        f"Model: {os.environ.get('MODEL', 'claude-sonnet-5')}", ""]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copytree(WS, tmp, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".sandbox", "__pycache__", "*.bak"))
        copy_pristine(tmp)                                 # the book's code, not your edits
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONUNBUFFERED="1")
        limit = 1800 if is_local() else 600          # a local model on a CPU is much slower
        for part, cmd, stdin, _ in runs:
            t = time.time()
            try:
                r = subprocess.run([sys.executable, *cmd.split()], cwd=tmp, env=env, input=stdin,
                                   capture_output=True, text=True, timeout=limit)
                out, code = (r.stdout + r.stderr), r.returncode
            except subprocess.TimeoutExpired as exc:
                partial = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) \
                    else (exc.stdout or "")
                out, code = f"TIMEOUT after {limit} s\n{partial}", -1
            passed = code == 0 and "Traceback (most recent call last)" not in out
            secs = time.time() - t
            (ok if passed else fail)(f"Part {part}  {cmd:<34} {secs:5.0f} s")
            rows.append(passed)
            tail = "\n".join(out.strip().splitlines()[-25:])
            report += [f"## {'PASS' if passed else 'FAIL'}: {cmd} (Part {part}, {secs:.0f} s, exit {code})",
                       "", "```", tail, "```", ""]
    out_file = WS / "live_report.md"
    out_file.write_text("\n".join(report))
    say(f"\n{sum(rows)}/{len(rows)} passed. Compare each output with the book's \"what you should "
        f"see\" notes in ANSWERS.md. Full report: {host_path(out_file)}")
    return 0 if all(rows) else 1

def _live_command(e):
    """The command that runs exercise e with its REFERENCE solution, or (None, reason)."""
    kind = e["kind"]
    if kind == "run":
        return e["cmd"], None
    if kind == "ask" and e.get("question"):
        code = (f"import {e['module']} as m; from ch04_agent import run_agent; "
                f"print(run_agent({e['question']!r}, m.TOOLS, m.run_tool, "
                f"system=getattr(m, 'SYSTEM', 'x'))[0])")
        return f'python -c "{code}"', None
    if kind == "build":
        sol = SOLUTIONS / "exercises" / Path(e["file"]).name
        if sol.exists():                  # run_args: a smaller run for run-chapter
            return f"python {sol} {e.get('run_args', '')}".rstrip(), None
        return None, "no runnable reference solution (see ./course.sh solution)"
    article = "an" if kind[0] in "aeiou" else "a"
    return None, f"{article} {kind} exercise: nothing to run against a model"

def cmd_live_exercises(args):
    """Run every exercise that uses a model, with its reference solution, against the model
    you've chosen (Claude or local), in a scratch copy of your workspace. Writes a report."""
    import tempfile
    only = {a.upper() for a in args if not a.startswith("-")}
    wanted = [e for e in EXERCISES
              if e.get("model", "any") in ("any", "claude-rec", "claude")
              and (not only or e["id"].split(".")[0] in only or e["id"] in only)]
    head(f"Live exercise check: {len(wanted)} exercises against {os.environ.get('MODEL')}"
         f" ({'local model' if is_local() else 'Claude API'})")
    if is_local():
        say("Free, but slow on a CPU: allow several hours for all of them. Exercises marked "
            "'Claude only' are skipped.")
    else:
        say(f"This uses your API key: about {_cost('first')} for one pass of every paid exercise (COST_MODEL.md).")
    if "--yes" not in args and input("Continue? [y/N] ").strip().lower() != "y":
        return 0
    rows, report = [], ["# Live exercise report", "",
                        f"Model: {os.environ.get('MODEL')} "
                        f"({'local' if is_local() else 'Claude API'})", "",
                        "| Exercise | Result | Seconds |", "| --- | --- | --- |"]
    details = []
    out_file = WS / "live_exercises_report.md"

    def save():                     # after every exercise, so a stopped run keeps its results
        try:
            out_file.write_text("\n".join(report + ["", *details]))
        except OSError as exc:
            warn(f"Couldn't write {host_path(out_file)}: {exc}")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copytree(WS, tmp, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".sandbox", "__pycache__", "*.bak", "exercises",
                                                      "live_*report.md", ".git"))
        copy_pristine(tmp)
        # COURSE_WORKSPACE: `course data ...` in an exercise's setup writes into the scratch copy
        env = dict(os.environ, PYTHONUNBUFFERED="1", COURSE_WORKSPACE=str(tmp),
                   PYTHONPATH=f"{tmp}:{SOLUTIONS / 'exercises'}:{SOLUTIONS / 'capstones'}")
        for e in wanted:
            cmd, why = _live_command(e)
            if e.get("model") == "claude" and is_local():
                cmd, why = None, "Claude only"
            elif e.get("needs") == "sandbox" and not sandbox_alive():
                cmd, why = None, "needs the sandbox: ./course.sh sandbox up"
            elif e.get("needs") == "github" and not os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"):
                cmd, why = None, "needs GITHUB_PERSONAL_ACCESS_TOKEN"
            if not cmd:
                say(_c("2", f"-  {e['id']:<5} skipped: {why}"))
                report.append(f"| {e['id']} {e['title']} | skipped: {why} | |")
                save()
                continue
            t = time.time()
            try:
                if e.get("setup"):
                    subprocess.run(["bash", "-c", e["setup"]], cwd=tmp, env=env,
                                   capture_output=True, timeout=900)
                r = subprocess.run(["bash", "-c", cmd], cwd=tmp, env=env, input="n\nquit\nquit\n",
                                   capture_output=True, text=True, timeout=1800)
                out, code = r.stdout + r.stderr, r.returncode
            except subprocess.TimeoutExpired:
                out, code = "TIMEOUT after 30 minutes", -1
            except Exception as exc:                     # never lose the whole run to one exercise
                out, code = f"{type(exc).__name__}: {exc}", -1
            passed = code == 0 and "Traceback (most recent call last)" not in out
            secs = time.time() - t
            (ok if passed else fail)(f"{e['id']:<5} {e['title'][:44]:<44} {secs:5.0f} s")
            rows.append(passed)
            report.append(f"| {e['id']} {e['title']} | {'PASS' if passed else 'FAIL'} | {secs:.0f} |")
            tail = "\n".join(out.strip().splitlines()[-20:])
            details += [f"## {'PASS' if passed else 'FAIL'}: {e['id']} {e['title']}", "",
                        f"`{cmd[:200]}`", "", "```", tail, "```", ""]
            save()
    say(f"\n{sum(rows)}/{len(rows)} passed, {len(wanted) - len(rows)} skipped. A PASS means the "
        f"reference solution ran without errors; read the answers to judge their quality. "
        f"Full report: {host_path(out_file)}")
    return 0 if all(rows) else 1

# ---------------------------------------------------------------- chapter runner
# ./course.sh run-chapter 7    runs every exercise of a chapter with its reference solution,
# in a scratch copy of your workspace, and keeps each one's full output as a log file:
#   <outputs>/ch07/7.5.log, <outputs>/ch07/summary.json and an index in <outputs>/README.md.
# <outputs> is /outputs (the kit's solutions/outputs folder, see compose.yaml).
# The model is the free LOCAL model unless you ask for Claude (--model claude or RUN_MODEL).
OUTPUTS = Path(os.environ.get("COURSE_OUTPUTS", "/outputs"))
RUN_MODELS = ("local", "claude")
PERSON_KINDS = {"inspector": "needs a person: MCP Inspector in a browser",
                "desktop": "needs a person: the Claude Desktop app"}

def _run_model(args):
    """'local' or 'claude': --model wins, then RUN_MODEL, then local. None if invalid."""
    choice = os.environ.get("RUN_MODEL", "").strip().lower() or "local"
    for i, a in enumerate(args):
        if a == "--model":
            choice = args[i + 1].lower() if i + 1 < len(args) else ""
        elif a.startswith("--model="):
            choice = a.split("=", 1)[1].lower()
    choice = {"ollama": "local", "qwen": "local", "api": "claude"}.get(choice, choice)
    return choice if choice in RUN_MODELS else None

def _chapter_keys():
    """Chapter keys in book order (0, P, 1, T, 2, ...), then the capstones C1..C7."""
    keys = []
    for e in EXERCISES:                              # exercises.json is in book order
        k = e["id"].split(".")[0]
        if k not in keys:
            keys.append(k)
    return keys + [f"C{n}" for n in CAPSTONES]

def _chapter_key(text):
    """'7', '07', 'ch7', 'p', 'c1' -> the key used in exercises.json ('7', 'P', 'C1')."""
    k = text.strip().upper().removeprefix("CH")
    if k.startswith("CAPSTONE") and k != "CAPSTONES":
        k = "C" + k.removeprefix("CAPSTONE").strip("-_ ")
    return str(int(k)) if k.isdigit() else k

def _chapter_dir(key):
    """Folder for a chapter's logs: ch07, ch00, P, T, C1."""
    return f"ch{int(key):02d}" if key.isdigit() else key

def _chapter_exercises(key):
    """A chapter's exercises in order (new ones may be appended anywhere in the json)."""
    found = [e for e in EXERCISES if e["id"].split(".")[0] == key]
    minor = lambda e: int(e["id"].split(".")[1]) if e["id"].split(".")[1].isdigit() else 0
    return sorted(found, key=minor)

def _outputs_dir():
    """/outputs if it is mounted (compose.yaml), else workspace/outputs."""
    if OUTPUTS.is_dir() and os.access(OUTPUTS, os.W_OK):
        return OUTPUTS
    fallback = WS / "outputs"
    warn(f"{OUTPUTS} isn't mounted (older compose.yaml?): writing the logs to "
         f"{host_path(fallback) if WS in fallback.parents else fallback} instead.")
    return fallback

def _outputs_label(out):
    """How the outputs folder looks on your computer."""
    if out == OUTPUTS:
        return "solutions/outputs" if str(out) == "/outputs" else str(out)
    return host_path(out) if WS in out.parents else str(out)

def _local_model_ready():
    import httpx
    try:
        return bool(httpx.get(f"{ADAPTER_URL}/health", timeout=5).json().get("ok"))
    except (httpx.HTTPError, ValueError):
        return False

def _chapter_command(e):
    """(command, None) to run exercise e with its reference solution, or (None, reason).
    Like _live_command, plus test exercises (their reference tests) and build exercises
    whose solution file has another name (listed in solutions/index.json)."""
    cmd, why = _live_command(e)
    if cmd or e["kind"] not in ("build", "test"):
        return cmd, why
    index = SOLUTIONS / "index.json"
    files = json.loads(index.read_text()).get(e["id"], []) if index.exists() else []
    if e["kind"] == "test":
        tests = [f for f in files if re.match(r"tests/test_\w+\.py$", f)]
        own = [f for f in tests if not re.match(r"tests/test_ch\d", f)] or tests
        if own:                  # solutions/tests/conftest.py stands in for the model
            return ("python -m pytest -q -p no:cacheprovider --rootdir /tmp "
                    + " ".join(str(SOLUTIONS / f) for f in own)), None
        return None, "no reference test to run (see ./course.sh solution)"
    progs = [f for f in files if f.startswith("exercises/") and f.endswith(".py")]
    if progs:
        return f"python {SOLUTIONS / progs[0]}", None
    return None, why

def _skip_reason(e, local, free_only):
    """Why exercise e can't run unattended here, or None."""
    need = e.get("model", "any")
    if e["kind"] in PERSON_KINDS or need == "desktop":
        return PERSON_KINDS.get(e["kind"], PERSON_KINDS["desktop"])
    if free_only and need != "none":
        return "needs a model (--free-only)" + (": Claude only" if need == "claude" else "")
    if need == "claude" and local:
        return "Claude only"
    if e.get("needs") == "sandbox" and not sandbox_alive():
        return "needs the sandbox: ./course.sh sandbox up"
    if e.get("needs") == "github" and not os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"):
        return "needs GITHUB_PERSONAL_ACCESS_TOKEN in .env"
    return None

def _run_logged(cmd, cwd, env, limit, setup=None):
    """Run a shell command; returns (combined stdout+stderr, exit code). Every process it
    starts is killed after `limit` seconds."""
    import signal
    out = ""
    for step, timeout in ([(setup, 900)] if setup else []) + [(cmd, limit)]:
        if setup:
            out += f"$ {step}\n"
        proc = subprocess.Popen(["bash", "-c", step], cwd=cwd, env=env, text=True,
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, start_new_session=True,
                                errors="replace")
        try:
            text, _ = proc.communicate("n\nquit\nquit\n", timeout=timeout)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            text, _ = proc.communicate()
            text, code = (text or "") + f"\nTIMEOUT after {timeout} s\n", -1
        out += text or ""
        if code != 0 and step is setup:
            return out + f"\n(setup failed with exit code {code})\n", code
    return out, code

def _write_log(path, e_id, title, cmd, model, code, secs, body):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Exercise: {e_id}  {title}\n# Command:  {cmd}\n# Model:    {model}\n"
        f"# Date:     {stamp}\n# Exit code: {code}\n# Seconds:  {secs:.1f}\n"
        + "#" + "-" * 79 + "\n" + body.rstrip() + "\n", errors="replace")

def _provenance(model_label):
    """What produced a result: the code (commit), the environment (Python, packages) and the
    model. Written into every run-chapter summary so a result can be reproduced or explained."""
    import hashlib
    import platform
    from importlib import metadata
    pkgs = sorted(f"{d.metadata['Name'].lower()}=={d.version}" for d in metadata.distributions()
                  if d.metadata["Name"])
    ver = dict(p.split("==", 1) for p in pkgs)
    local = os.environ.get("PROVIDER") == "local"
    return {"commit": os.environ.get("COURSE_COMMIT") or "not recorded (run outside course.sh)",
            "python": platform.python_version(),
            "packages_sha256": hashlib.sha256("\n".join(pkgs).encode()).hexdigest()[:16],
            "packages": {k: ver.get(k) for k in ("anthropic", "mcp", "claude-agent-sdk",
                                                 "langchain", "httpx", "pytest")},
            "provider": "local" if local else "claude",
            "model_id": os.environ.get("LOCAL_MODEL", "qwen3.5:9b") if local
                        else os.environ.get("MODEL", "claude-sonnet-5"),
            "model_label": model_label}


def _refresh_outputs_index(out):
    """Rewrite <outputs>/README.md: a table of every chapter that has a summary.json."""
    order = {_chapter_dir(k): i for i, k in enumerate(_chapter_keys())}
    rows = []
    for f in sorted(out.glob("*/summary.json"), key=lambda p: order.get(p.parent.name, 999)):
        try:
            s = json.loads(f.read_text())
        except ValueError:
            continue
        n = {k: sum(1 for x in s["exercises"] if x["status"] == k)
             for k in ("passed", "failed", "skipped")}
        written = sum(1 for x in s["exercises"] if x.get("kind") == "concept")
        rows.append(f"| [{s['chapter']}]({f.parent.name}/) | {s['title']} | {n['passed']} | "
                    f"{n['failed']} | {n['skipped']} | {written} | {s['model']} | {s['date']} |")
    (out / "README.md").write_text("\n".join([
        "# Exercise outputs", "",
        "Real output of every exercise's reference solution, written by "
        "`./course.sh run-chapter <chapter|all>` (Windows: `.\\course.cmd run-chapter ...`, "
        "or double-click `run-chapters.cmd`). Each chapter folder has one `<id>.log` per "
        "exercise (a short header, then everything the program printed) and a "
        "`summary.json`. Concept exercises get their sample answer from "
        "`solutions/ANSWERS.md`; they count as skipped (nothing to run).", "",
        "This file is rewritten after every run.", "",
        "| Chapter | Title | Passed | Failed | Skipped | Written answers | Model | Run on |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |", *rows,
        *([] if rows else ["", "No runs yet."]), ""]))

def _start_service(e, cwd, env):
    """Exercises marked service="api" talk to the chapter 30 agent API, and service="mcp"
    to the chapter 30 remote MCP server: start it in the scratch copy for the length of
    the exercise. Returns (process, env for the exercise)."""
    import secrets, socket
    if e.get("service") == "api":
        env = dict(env, AGENT_API_URL="http://127.0.0.1:8080")
        if not env.get("AGENT_API_KEYS"):
            env["AGENT_API_KEYS"] = secrets.token_urlsafe(24)
        cmd, port = [sys.executable, "-m", "uvicorn", "ch30_service:app", "--host",
                     "127.0.0.1", "--port", "8080"], 8080
    elif e.get("service") == "mcp":
        env = dict(env, MCP_HOST="127.0.0.1", MCP_PORT="8000")
        for var in ("MCP_TOKEN", "MCP_READONLY_TOKEN"):
            if not env.get(var):
                env[var] = secrets.token_urlsafe(24)
        # the learner's config points at the agentic-ai-mcp container; use the local server
        config = json.loads((SOLUTIONS / "exercises" / "servers_remote.json").read_text())
        for spec in config["servers"].values():
            if "url" in spec:
                spec["url"] = "http://localhost:8000/mcp"
        (Path(cwd) / "servers_remote.json").write_text(json.dumps(config, indent=2))
        cmd, port = [sys.executable, "ch30_remote_mcp.py"], 8000
    else:
        return None, env
    proc = subprocess.Popen(cmd, cwd=cwd, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):                                   # wait for the port to open
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
            break
        except OSError:
            time.sleep(0.5)
    return proc, env

def cmd_run_chapter(args):
    """run-chapter <chapter|exercise id|all> [--model local|claude] [--free-only] [--yes]"""
    import tempfile
    free_only, yes = "--free-only" in args, "--yes" in args or "-y" in args
    words = [a for i, a in enumerate(args) if not a.startswith("-")
             and not (i and args[i - 1] == "--model")]
    usage = ("Usage: ./course.sh run-chapter <chapter|exercise id|all> [--model local|claude] "
             "[--free-only] [--yes]     e.g.  run-chapter 7   run-chapter P   run-chapter 3.7   "
             "run-chapter all")
    if not words:
        fail(usage)
        return 2
    model = _run_model(args)
    if model is None:
        fail("--model (or RUN_MODEL) must be 'local' (the free qwen3.5:9b) or 'claude'.")
        return 2
    keys = _chapter_keys()
    ids = {e["id"].upper(): e["id"] for e in EXERCISES}
    only = {ids[w.upper()] for w in words if w.upper() in ids}   # single exercises: 3.7, 24.6
    if any(w.lower() == "all" for w in words):
        chosen = keys
    else:
        chosen = []
        for w in words:
            k = w.upper().split(".")[0] if w.upper() in ids else _chapter_key(w)
            group = [c for c in keys if c.startswith("C")] if k == "CAPSTONES" else [k]
            if k != "CAPSTONES" and k not in keys:
                fail(f"No chapter '{w}'. Chapters: {' '.join(keys)} (or: all, capstones)")
                return 2
            chosen += [c for c in group if c not in chosen]
    # The model switch: PROVIDER decides where every program sends its requests
    # (main() already set it from --model/RUN_MODEL; apply_provider() did the rest).
    local = model == "local"
    os.environ["PROVIDER"] = model
    if local and os.environ.get("ANTHROPIC_BASE_URL") != ADAPTER_URL:
        apply_provider()                   # main() normally did this already
    model_name = os.environ.get("MODEL", "claude-sonnet-5")
    label = f"{model_name} (local, through Ollama)" if local else f"{model_name} (Claude API)"
    plan = []                                              # (chapter, exercise or capstone)
    for k in chosen:
        whole = not only or any(_chapter_key(w) == k for w in words if w.upper() not in ids)
        plan += [(k, e) for e in _chapter_exercises(k) if whole or e["id"] in only] \
            if not k.startswith("C") \
            else [(k, {"id": k, "kind": "capstone", "model": "any",
                       "title": f"Capstone {k[1:]} ({CAPSTONES[k[1:]][0]})",
                       "chapter": f"Capstone {k[1:]}"})]
    uses_model = [e for _, e in plan if e.get("model", "any") != "none"
                  and e["kind"] != "concept" and not _skip_reason(e, local, free_only)]
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if uses_model and not local and (not key.startswith("sk-") or "your-key-here" in key
                                     or key == "sk-local-ollama"):
        fail("--model claude needs ANTHROPIC_API_KEY in the .env file next to course.sh. "
             "Leave out --model to use the free local model, or add --free-only.")
        return 1
    if uses_model and local and not _local_model_ready():
        fail("The local model isn't running. Start it first (the first time downloads it):")
        say("    ./course.sh local up        (Windows: .\\course.cmd local up)")
        say("Or run only the exercises that need no model:  run-chapter ... --free-only")
        return 1
    head(f"Chapter runner: {len(plan)} exercises in {len(chosen)} chapter(s)"
         + ("" if free_only else f", {len(uses_model)} of them use {label}"))
    if free_only:
        say("--free-only: only exercises that need no model run; the others are skipped.")
    elif uses_model:
        say("Free, but slow on a CPU: allow several hours for everything." if local else
            f"This uses your API key: about {_cost('first')} for one pass of every chapter (COST_MODEL.md).")
        say("Your own files are not used or changed.")
        try:
            if not yes and input("Continue? [y/N] ").strip().lower() != "y":
                return 0
        except EOFError:                        # no keyboard (e.g. a script): add --yes
            fail("No answer to 'Continue?'. Add --yes to run without asking.")
            return 1
    out_root = _outputs_dir()
    answers = SOLUTIONS / "ANSWERS.md"
    answers = answers.read_text() if answers.exists() else ""
    limit = 1800 if local else 600                  # a local model on a CPU is much slower
    totals = {"passed": 0, "failed": 0, "skipped": 0}
    with tempfile.TemporaryDirectory(prefix="run-chapter-") as tmp:
        tmp = Path(tmp)
        shutil.copytree(WS, tmp, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".sandbox", "__pycache__", "*.bak",
                                                      "exercises", "live_*report.md", ".git",
                                                      "outputs"))
        copy_pristine(tmp)                                 # the book's code, not your edits
        env = dict(os.environ, PYTHONUNBUFFERED="1", COURSE_WORKSPACE=str(tmp),
                   PYTHONDONTWRITEBYTECODE="1", COURSE_CODE=str(PRISTINE),
                   COURSE_DATA=str(COURSE / "data"),
                   COURSE_EXERCISES=str(COURSE / "exercises.json"),
                   PYTHONPATH=f"{tmp}:{SOLUTIONS / 'exercises'}:{SOLUTIONS / 'capstones'}")
        run_provenance = _provenance(label)
        for k in chosen:
            folder = out_root / _chapter_dir(k)
            folder.mkdir(parents=True, exist_ok=True)
            items = [e for c, e in plan if c == k]
            head(f"\n{items[0]['chapter']}  ->  {_outputs_label(out_root)}/{folder.name}/")
            entries = []
            for e in items:
                need = e.get("model", "any")
                ex_model = "none (no model needed)" if need == "none" else label
                entry = {"id": e["id"], "title": e["title"], "kind": e["kind"],
                         "status": "skipped", "reason": None, "seconds": 0, "log": None,
                         "model": "none" if need == "none" or e["kind"] == "concept" else label}
                log = folder / f"{e['id']}.log"
                if e["kind"] == "concept":                   # a written answer: nothing to run
                    text = _answer_for(e["id"], answers)
                    entry["reason"] = ("concept exercise: written answer copied from ANSWERS.md"
                                       if text else
                                       "concept exercise: written answer, see ANSWERS.md")
                    if text:
                        _write_log(log, e["id"], e["title"], "(none: a written answer)",
                                   "none", 0, 0, text)
                        entry["log"] = f"{folder.name}/{log.name}"
                    say(_c("2", f"-  {e['id']:<5} written answer"))
                    entries.append(entry)
                    continue
                why = _skip_reason(e, local, free_only)
                cmd = None
                if not why and e["kind"] == "capstone":
                    cmd = f"{sys.executable} {Path(__file__).resolve()} capstone {k[1:]}"
                elif not why:
                    cmd, why = _chapter_command(e)
                if not cmd:
                    entry["reason"] = why
                    say(_c("2", f"-  {e['id']:<5} skipped: {why}"))
                    entries.append(entry)
                    continue
                t = time.time()
                service = None
                try:
                    service, run_env = _start_service(e, tmp, env)
                    out, code = _run_logged(cmd, tmp, run_env,
                                            limit if need != "none" else 600,
                                            setup=e.get("setup"))
                except Exception as exc:                 # never lose the whole run to one
                    out, code = f"{type(exc).__name__}: {exc}", -1
                finally:
                    if service:
                        service.terminate()
                        service.wait(timeout=10)
                secs = time.time() - t
                passed = code == 0 and "Traceback (most recent call last)" not in out
                shown = f"course capstone {k[1:]}" if e["kind"] == "capstone" else cmd
                _write_log(log, e["id"], e["title"], shown, ex_model, code, secs, out)
                if passed and "first, then run this again" in out:   # the learner's own file
                    entry.update(reason="needs a file you create yourself: " + out.strip(),
                                 log=f"{folder.name}/{log.name}")
                    say(_c("2", f"-  {e['id']:<5} skipped: needs your own file (see its log)"))
                    entries.append(entry)
                    continue
                entry["commit"] = run_provenance["commit"]
                entry.update(status="passed" if passed else "failed", seconds=round(secs, 1),
                             log=f"{folder.name}/{log.name}",
                             reason=None if passed else
                             (f"exit code {code}" if code else "printed a Traceback"))
                (ok if passed else fail)(f"{e['id']:<5} {e['title'][:44]:<44} {secs:5.0f} s")
                entries.append(entry)
            for x in entries:
                totals[x["status"]] += 1
            chapter_model = "none (--free-only)" if free_only else label
            summary = folder / "summary.json"
            if len(items) < len(_chapter_exercises(k)) and not k.startswith("C") \
                    and summary.exists():        # only some exercises ran: merge them in
                old = json.loads(summary.read_text())
                new = {x["id"]: x for x in entries}
                needs = {e["id"]: e.get("model", "any") for e in _chapter_exercises(k)}
                for x in old["exercises"]:        # entries written before per-exercise models
                    x.setdefault("model", "none" if x["kind"] == "concept"
                                 or needs.get(x["id"]) == "none" else old["model"])
                entries = [new.pop(x["id"], x) for x in old["exercises"]] + list(new.values())
                models = {x["model"] for x in entries if x["model"] != "none"}
                chapter_model = models.pop() if len(models) == 1 else "mixed: see each exercise"
            summary.write_text(json.dumps({
                "chapter": k, "title": items[0]["chapter"], "model": chapter_model,
                "date": time.strftime("%Y-%m-%d %H:%M"), "provenance": run_provenance,
                "exercises": entries}, indent=1) + "\n")
            _refresh_outputs_index(out_root)
    say(f"\n{totals['passed']} passed, {totals['failed']} failed, {totals['skipped']} skipped "
        f"(including written answers). Logs: {_outputs_label(out_root)}/  (index: README.md)")
    return 1 if totals["failed"] else 0

# ---------------------------------------------------------------- free local model
def cmd_local_adapter(args):
    """Run the adapter between the Anthropic SDK and Ollama (the local-adapter service)."""
    sys.path.insert(0, str(COURSE))
    import uvicorn
    from local_adapter import app
    say(f"Local model adapter on :8787, forwarding to {OLLAMA_URL}")
    uvicorn.run(app, host="0.0.0.0", port=8787, log_level="warning")
    return 0

def cmd_local_pull(args):
    """Download the local model into Ollama (once; it's kept in a Docker volume)."""
    import httpx
    model = (args[0] if args else None) or os.environ.get("LOCAL_MODEL") or LOCAL_DEFAULT_MODEL
    head(f"Downloading {model} into the local model server (only the first time)...")
    for _ in range(30):                                  # Ollama needs a moment to start
        try:
            httpx.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            break
        except httpx.HTTPError:
            time.sleep(2)
    else:
        fail(f"Can't reach Ollama at {OLLAMA_URL}. Is it running?  ./course.sh local up")
        return 1
    last = ""
    try:
        with httpx.stream("POST", f"{OLLAMA_URL}/api/pull", json={"model": model, "stream": True},
                          timeout=httpx.Timeout(None, connect=10)) as r:
            for line in r.iter_lines():
                if not line.strip():
                    continue
                msg = json.loads(line)
                if msg.get("error"):
                    fail(msg["error"])
                    return 1
                status = msg.get("status", "")
                if msg.get("total"):
                    pct = 100 * msg.get("completed", 0) // msg["total"]
                    print(f"\r  {status[:30]:<30} {pct:3d}% of {msg['total'] / 1e9:.1f} GB",
                          end="", file=sys.stderr)
                elif status != last:
                    say(f"\n  {status}" if last else f"  {status}")
                last = status
    except httpx.HTTPError as exc:
        fail(f"Download failed: {exc}. Check your internet connection and try again.")
        return 1
    say("")
    ok(f"{model} is ready. " + ("PROVIDER=local is set, so the course now uses it." if is_local()
                                else "Set PROVIDER=local in .env to use it (see Appendix H)."))
    return 0

def cmd_local_status(args):
    import httpx
    say(f"Provider: {'local (free model)' if is_local() else 'claude (Claude API)'}"
        f"   (change PROVIDER in .env)")
    try:
        h = httpx.get(f"{ADAPTER_URL}/health", timeout=5).json()
    except (httpx.HTTPError, ValueError):
        fail("The local model isn't running. Start it with:  ./course.sh local up")
        return 1
    if not h.get("ok"):
        fail(f"The adapter is running but can't reach Ollama at {h.get('ollama')}.")
        return 1
    want = os.environ.get("LOCAL_MODEL") or LOCAL_DEFAULT_MODEL
    ok(f"Local model server running. Models: {', '.join(h['models']) or 'none yet'}")
    if not any(m == want or m == want + ":latest" for m in h["models"]):
        warn(f"{want} isn't downloaded yet. Run:  ./course.sh local up")
        return 1
    return 0

# ---------------------------------------------------------------- help
HELP = """Building Agentic AI Systems: course commands (run them from the kit folder on your computer)

  ./course.sh setup                  first-time setup: Docker check, .env, your API key
  ./course.sh quickstart             your first agent, free: no API key, no download
  ./course.sh list [chapter]         list exercises, e.g.  list 4  or  list P
  ./course.sh ex <id>                show and run an exercise, e.g.  ex 4.2  or  ex T.2
  ./course.sh ex <id> --info         just show the exercise
  ./course.sh ask <module> ["q"]     chat with a chapter's tools, e.g.  ask ch08_sql_tools
  ./course.sh python <file.py> ...   run any course file, e.g.  python ch04_agent.py
  ./course.sh shell                  open a terminal inside the course container
  ./course.sh check [--api]          check the environment (and your API key)
  ./course.sh check <id>             check your answer to an exercise, e.g.  check 0.4
  ./course.sh selftest               offline self-test of the whole setup (no API key needed)
  ./course.sh live-check [part]      run every chapter's main file against the real model
  ./course.sh live-check exercises [chapter]   run every exercise that uses a model, with its
                                     reference solution, against your model (Claude or local)
  ./course.sh run-chapter <ch|all> [--model local|claude] [--free-only] [--yes]
                                     run a chapter's exercises (reference solutions) and keep
                                     each one's output in solutions/outputs/chNN/<id>.log. Uses
                                     the free local model unless --model claude (or
                                     RUN_MODEL=claude); --free-only runs just the no-model ones
  ./course.sh data <kind> [...]      regenerate sample data: notes, library, messy, repo, db
  ./course.sh reset <file>           restore an original course file (yours is kept as .bak)

  ./course.sh inspector <server.py>  MCP Inspector web UI on http://localhost:6274
  ./course.sh serve <server.py>      run an MCP server over HTTP on http://localhost:8000/mcp
  ./course.sh desktop-config [srv]   print the Claude Desktop config for a server
  ./course.sh serve-api              the chapter 30 agent API on http://localhost:8080
  ./course.sh serve-mcp              the chapter 30 remote MCP server (token-protected)
  ./course.sh serve-a2a              the chapter 21 A2A analyst agent on http://localhost:9999
  ./course.sh sandbox up|down        start/stop the network-less test sandbox (chapter 10)
  ./course.sh build                  (re)build the Docker image

  Free local model (qwen3.5:9b through Ollama; set PROVIDER=local in .env, see Appendix H):
  ./course.sh local up [--gpu]       start the local model (downloads it the first time)
  ./course.sh local status           is the local model running, and which models are there?
  ./course.sh local down             stop it and free the memory

  Solutions (try the exercise first!):
  ./course.sh solution <id>          show the solution for an exercise, e.g.  solution 4.4
  ./course.sh capstone <1-7>         run a reference capstone
  ./course.sh check-solutions        run every solution and capstone offline (no API key)

Your files live in the 'workspace' folder next to course.sh. Edit them with any editor.
"""

COMMANDS = {
    "list": cmd_list, "ex": cmd_ex, "exercise": cmd_ex, "ask": cmd_ask,
    "inspector": cmd_inspector, "serve": cmd_serve, "serve-api": cmd_serve_api,
    "serve-mcp": cmd_serve_mcp, "serve-a2a": cmd_serve_a2a, "desktop-config": cmd_desktop_config,
    "data": cmd_data, "reset": cmd_reset, "check": cmd_check, "selftest": cmd_selftest,
    "quickstart": cmd_quickstart,
    "sandbox-worker": cmd_sandbox_worker, "solution": cmd_solution,
    "check-solutions": cmd_verify_solutions, "live-check": cmd_live_check, "capstone": cmd_capstone, "verify-solutions": cmd_verify_solutions,
    "local-adapter": lambda a: cmd_local_adapter(a), "local-pull": lambda a: cmd_local_pull(a),
    "local-status": lambda a: cmd_local_status(a), "run-chapter": cmd_run_chapter,
}

def main(argv):
    if not argv or argv[0] in ("help", "-h", "--help"):
        say(HELP)
        return 0
    cmd, args = argv[0], argv[1:]
    if cmd == "init":
        init(force="--force" in args, quiet=False)
        return 0
    if cmd == "run-chapter" and _run_model(args):   # its own model switch, before apply_provider
        os.environ["PROVIDER"] = _run_model(args)      # (default: the free local model)
    if cmd not in ("sandbox-worker", "selftest", "verify-solutions", "check-solutions", "solution",
                   "local-adapter", "local-pull", "local-status"):
        init(quiet=cmd == "quickstart")
        if cmd != "quickstart":                 # needs no model, so no provider check
            apply_provider()
    if cmd in COMMANDS:
        if cmd in ("run-chapter", "live-check", "solution", "capstone",
                   "check-solutions", "verify-solutions"):
            flatten_solutions()
        return COMMANDS[cmd](args) or 0
    if cmd == "shell":
        os.execvpe("bash", ["bash"], env_for_runs())
    if cmd.endswith(".py"):                     # ./course.sh ch04_agent.py
        argv = ["python"] + argv
    os.chdir(WS)
    try:
        os.execvpe(argv[0], argv, env_for_runs())   # python, pytest, bash, npx, ...
    except FileNotFoundError:
        fail(f"Unknown command '{cmd}'.")
        say(HELP)
        return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
