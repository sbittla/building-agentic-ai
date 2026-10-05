# Building Agentic AI Systems: code, exercises and solutions

The companion repository for the book *Building Agentic AI Systems: From First Agent to MCP, Multi-Agent Orchestration, and Production* by Srinivasa Rao Bittla. It has every chapter's code, **237 exercises** across 31 chapters and 6 interludes (with starter files, checkers and reference solutions), **six capstone projects**, and one Docker image that runs all of it.

Everything runs inside Docker, so Docker is the only thing you install. You edit files on your computer with any editor; Docker runs them.

**Where to find what**

| File | What it's for |
| --- | --- |
| `README.md` (this file) | Setup, how to practise, every command, verified results, troubleshooting |
| [EXERCISE_INDEX.md](EXERCISE_INDEX.md) | Every exercise: type, model needed, solution file, latest result |
| [LOCAL_MODEL.md](LOCAL_MODEL.md) | The free local model in depth (Appendix H of the book) |
| [RESOURCES.md](RESOURCES.md) | Every reference from the book: courses, docs, where to ask for help |
| [solutions/README.md](solutions/README.md) | How the solutions and capstones are organised and run |
| [solutions/SOLUTIONS.md](solutions/SOLUTIONS.md) | What each reference solution shows |
| [COMPATIBILITY.md](COMPATIBILITY.md) | The dated matrix of pinned versions, models, prices and protocol versions; protocol vs SDK changes |
| [CHANGELOG.md](CHANGELOG.md) · [MIGRATION.md](MIGRATION.md) | What changed between tags, and what to change in your code |
| [ERRATA.md](ERRATA.md) | Mistakes in each printing, and their corrections |
| [verification/](verification/README.md) · [benchmarks/](benchmarks/README.md) | Test and security results with their provenance; the published benchmark runs |
| [PILOT.md](PILOT.md) | For the author: testing the book with real learners |

On Windows, replace `./course.sh` with `.\course.cmd` in every command below.

---

## Book editions and code versions

Each printing of the book is matched by a tag, so you can always get the exact code it was tested against. `main` keeps moving: fixes and compatibility updates land there and are listed in [CHANGELOG.md](CHANGELOG.md), never silently. A tag never moves, so the code at your printing's tag always matches your book; mistakes in the printed text are in [ERRATA.md](ERRATA.md).

| Book printing | Exercises | Tag | Get it |
| --- | ---: | --- | --- |
| First printing, September 2026 | 231 | `edition-1.0` | `git checkout edition-1.0` |
| Corrected printing, October 2026 | 237 | `edition-1.1` | `git checkout edition-1.1` |

Not sure which printing you have? The copyright page says, and the corrected printing opens with a two-page Contents at a Glance.

## 1. One-time setup (about 20 minutes)

**You need:** 16 GB of RAM (32 GB recommended), about 15 GB of free disk space, and an internet connection for the first build.

1. **Install Docker.** Docker Desktop on Windows or macOS, or Docker Engine with the Compose plugin on Linux. Start it and wait until it says it's running. On Windows it needs WSL 2 and virtualization switched on (the installer tells you).
2. **Get the code.**
   ```bash
   git clone https://github.com/sbittla/building-agentic-ai.git
   cd building-agentic-ai
   ```
   No Git? Download the ZIP from the repository page and unzip it anywhere, for example `D:\Learning\building-agentic-ai`.
3. **Choose a model.**
   - **Claude:** create an API key in the Claude Console (Chapter 0 of the book walks you through it). Exercises cost cents each; running every exercise costs roughly $5–15.
   - **The free local model `qwen3.5:9b`:** no key and no cost, but slower. It runs every exercise except the 4 marked *Claude only*. See [section 2](#2-the-free-local-model-optional).
4. **Run the setup.** It checks Docker, creates your `.env` file from `.env.example`, asks which model you want (and, for Claude, your key, without showing it), and generates the other secrets the course needs:
   ```bash
   ./course.sh setup
   ```
   Your key lives only in `.env`, which Git ignores. The sample value `ANTHROPIC_API_KEY=sk-ant-your-key-here` means "no key yet". Never commit `.env` or paste your key anywhere else.
5. **Build the image** (5–10 minutes the first time):
   ```bash
   ./course.sh build
   ```
6. **Check that everything works:**
   ```bash
   ./course.sh selftest          # offline: Docker, the image and the course files (no key needed)
   ./course.sh check --api       # one real model call (uses your key, or the local model)
   ```

The first command after setup creates a **`workspace/` folder** with all the course code and sample data. **That folder is yours.** Edit files there; they're kept between runs and never overwritten. `./course.sh reset <file>` restores a single original file (yours is kept as `.bak`).

## 2. The free local model (optional)

The kit can run the open-source model `qwen3.5:9b` in Docker, and the book's code uses it unchanged. `course/local_adapter.py` bridges the few Claude features a local model lacks (forced tools, structured outputs, prompt caching).

| Step | Command |
| --- | --- |
| Start it (downloads about 6.6 GB the first time) | `./course.sh local up` |
| The same, on an NVIDIA GPU | `./course.sh local up --gpu` |
| Is it running? | `./course.sh local status` |
| Stop it and free the memory | `./course.sh local down` |

Then set `PROVIDER=local` in `.env` (setup does this if you choose the local model). Set it back to `PROVIDER=claude` to use Claude. Full guide, including Windows memory, GPUs and Macs: [LOCAL_MODEL.md](LOCAL_MODEL.md).

What each exercise needs (shown by `./course.sh list` and in [EXERCISE_INDEX.md](EXERCISE_INDEX.md)):

| Model needed | Exercises | Meaning |
| --- | ---: | --- |
| No model | 114 | Runs offline, no key |
| Local or Claude | 103 | Works with either |
| Claude recommended | 9 | Runs locally, but a small model often stalls or skips steps |
| Claude only | 4 | Needs `PROVIDER=claude` and an API key (3.7, 16.7, 24.6, 24.7) |
| Claude Desktop | 1 | Needs the Claude Desktop app |

## 3. How to practise

Work through the book in order. For each chapter:

1. **Read the chapter**, then run its main file to see it work:
   ```bash
   ./course.sh list 4                      # the chapter's exercises (interludes: list P, T, R, S or A)
   ./course.sh python ch04_agent.py        # any file in your workspace
   ```
2. **Open an exercise** and read the task and the "done when" line:
   ```bash
   ./course.sh ex 4.2 --info               # show the exercise only
   ./course.sh ex 4.2                      # show it and start it
   ```
3. **Do the exercise.** What `ex` sets up depends on the type:

   | Type | What happens | What you do |
   | --- | --- | --- |
   | Written answer | Creates `workspace/answers/exN_M.md` with the question | Write your answer in that file |
   | Run chapter code | Runs the chapter file, for example `python ch04_agent.py` | Edit the file first if the task says so, then run `ex` again |
   | Chat with tools | Starts a chat with that chapter's tools (also: `./course.sh ask ch08_sql_tools`) | Ask the question in the task and watch the tool calls |
   | Build | First run creates a starter file in `workspace/exercises/` (with function names and examples in the early chapters) | Fill it in, then run `ex` again to run it |
   | Write tests | First run creates `workspace/tests/test_exN_M_*.py` | Write the tests, then run `ex` again |
   | MCP Inspector | Opens the Inspector at http://localhost:6274 for the server | Call the tools by hand in the browser |

4. **Check your answer.** Some exercises have automatic checkers (Chapter 0, the interludes, 2.4 and 3.4); for the rest, compare the result with the exercise's "done when" line.
   ```bash
   ./course.sh check 0.4
   ```
5. **Compare with the reference solution**, only after you've tried:
   ```bash
   ./course.sh solution 4.4
   ```
   Model answers can differ from run to run: judge by the "done when" line, not by matching the solution's wording.
6. **Stuck?** Re-read the exercise's hint (`ex <id> --info`), check the troubleshooting table below, then look at [RESOURCES.md](RESOURCES.md) for where to ask.

After each part of the book, try the matching **capstone project** yourself before running the reference one:

```bash
./course.sh capstone 1                      # creates the sample data, then runs the support agent
./course.sh capstone 4 pr-3                 # extra arguments go to the capstone program
```

## 4. Run and verify every exercise

`run-chapter` runs each exercise's **reference solution** in a scratch copy of your workspace (your files are never used or changed) and saves the full output of each one.

```bash
./course.sh run-chapter 7                        # one chapter, on the free local model
./course.sh run-chapter 7 13 24                  # several chapters
./course.sh run-chapter 3.7 24.6 --model claude  # single exercises, on Claude
./course.sh run-chapter capstones                # the six capstones
./course.sh run-chapter all                      # everything, in book order (several hours locally)
./course.sh run-chapter all --free-only          # only the exercises that need no model
```

- The local model is the default: start it first with `./course.sh local up`. `--model claude` (or `RUN_MODEL=claude` in `.env`) uses your API key.
- Output goes to `solutions/outputs/chNN/<id>.log` (capstones: `solutions/outputs/C1/` and so on), with a `summary.json` per chapter and an overview in `solutions/outputs/README.md`.
- Running single exercises merges their results into the chapter's existing `summary.json`, and each result records which model produced it.
- Written answers are copied from `solutions/ANSWERS.md`. Exercises that need a person, the Claude Desktop app, a GitHub token or the sandbox are skipped, with the reason in the summary.
- On Windows you can double-click `run-chapters.cmd`; on macOS or Linux run `./run-chapters.sh [chapter]`.
- After a run, `python dev/exercise_index.py` refreshes [EXERCISE_INDEX.md](EXERCISE_INDEX.md) and the results table below.

## 5. Verified results

<!-- results:start -->
### A. Deterministic checks (no model)

Every reference solution, capstone and exercise command, run against a scripted stand-in model: no API key, no model provider, so the same commit gives the same result anywhere.

| Passed | Failed | Errors | Skipped (not applicable here) | Tests |
| ---: | ---: | ---: | ---: | ---: |
| 473 | 0 | 0 | 5 | 478 |

Commit `93187a20b935`; `requirements.lock` sha256 `c28c848a2447`; outside the course image (Linux); 2026-10-05. Skipped: 2 needs mcp-server-filesystem from the course image; 1 needs mcp-server-git from the course image; 1 needs mcp-server-fetch, mcp-server-memory from the course image; 1 needs mcp-server-fetch, mcp-server-filesystem, mcp-server-git, mcp-server-time from the course image. Details: [verification/README.md](verification/README.md), [verification/offline.json](verification/offline.json).

### B. Exercises run with a real model

Every exercise run with its reference solution by `run-chapter` (runs from 2026-09-27 to 2026-09-28; models: `claude-sonnet-5`, `qwen3.5:9b`). **163 of 164 runnable exercises passed (99.4%)**. A real model's answers vary from run to run, so these show that each exercise works end to end, not that it always will. Runs before October 2026 didn't record the commit; newer runs do (`provenance` in each summary.json). Per-exercise results and logs: [EXERCISE_INDEX.md](EXERCISE_INDEX.md), `solutions/outputs/`.

How the totals count: the book has **237 exercises**; the table adds the 6 capstones, so it has 243 rows of work. Every count here, in EXERCISE_INDEX.md and in the book is computed from `course/exercises.json`. *Written answer* exercises have nothing to run; *needs a person* means a person at the keyboard, the Claude Desktop app, a GitHub token or a file the reader creates; *not run yet* means no run has been recorded for this version.

| Chapter | Exercises | ✔ Passed | ✘ Failed | Written answer | Needs a person | Not run yet | Pass rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Chapter 0: Foundations | 7 | 4 | 0 | 2 | 1 | 0 | 100% |
| Interlude: The Python You'll Need | 5 | 5 | 0 | 0 | 0 | 0 | 100% |
| Chapter 1: What an Agent Is (and Isn't) | 9 | 4 | 0 | 5 | 0 | 0 | 100% |
| Interlude: Testing with pytest | 4 | 4 | 0 | 0 | 0 | 0 | 100% |
| Chapter 2: Tool Calling (Function Calling) | 6 | 4 | 0 | 2 | 0 | 0 | 100% |
| Chapter 3: Tool Selection, Routing and Tool Search | 7 | 5 | 0 | 2 | 0 | 0 | 100% |
| Chapter 4: The Agent Loop | 5 | 4 | 0 | 1 | 0 | 0 | 100% |
| Chapter 5: State and Short-Term Memory | 7 | 5 | 0 | 2 | 0 | 0 | 100% |
| Interlude: Regular Expressions | 4 | 4 | 0 | 0 | 0 | 0 | 100% |
| Chapter 6: Agentic Search: Exploring an Environment | 6 | 4 | 0 | 1 | 1 | 0 | 100% |
| Chapter 7: Real APIs | 6 | 2 | 0 | 2 | 2 | 0 | 100% |
| Interlude: SQL in One Sitting | 4 | 4 | 0 | 0 | 0 | 0 | 100% |
| Chapter 8: Self-Correction: A Text-to-SQL Agent | 7 | 2 | 0 | 2 | 3 | 0 | 100% |
| Interlude: Measuring an Agent | 3 | 0 | 0 | 1 | 0 | 2 | — |
| Chapter 9: Human-in-the-Loop Approval | 6 | 4 | 0 | 2 | 0 | 0 | 100% |
| Chapter 10: Feedback Loops | 7 | 4 | 0 | 2 | 1 | 0 | 100% |
| Interlude: Asynchronous Python | 4 | 4 | 0 | 0 | 0 | 0 | 100% |
| Chapter 11: Multi-Agent Systems | 7 | 5 | 0 | 2 | 0 | 0 | 100% |
| Chapter 12: MCP Fundamentals and Your First Server | 7 | 1 | 0 | 2 | 4 | 0 | 100% |
| Chapter 13: Build Your Own MCP Client | 8 | 7 | 0 | 1 | 0 | 0 | 100% |
| Chapter 14: Using Servers You Didn't Write | 5 | 1 | 0 | 2 | 2 | 0 | 100% |
| Chapter 15: MCP in 2026: From Tool Calling to Agent Infrastructure | 4 | 2 | 0 | 2 | 0 | 0 | 100% |
| Chapter 16: Context Engineering | 8 | 6 | 0 | 2 | 0 | 0 | 100% |
| Chapter 17: Agent Memory Engineering | 8 | 6 | 0 | 2 | 0 | 0 | 100% |
| Chapter 18: Agentic RAG and Knowledge Systems | 9 | 7 | 0 | 2 | 0 | 0 | 100% |
| Chapter 19: Long-Running Agents | 6 | 4 | 0 | 2 | 0 | 0 | 100% |
| Chapter 20: Planning and Model Routing | 6 | 4 | 0 | 2 | 0 | 0 | 100% |
| Chapter 21: Multi-Agent Orchestration | 6 | 4 | 0 | 2 | 0 | 0 | 100% |
| Chapter 22: Hybrid Architectures: Probabilistic Intelligence, Deterministic Control | 6 | 4 | 0 | 2 | 0 | 0 | 100% |
| Chapter 23: Computer-Use Agents | 6 | 4 | 0 | 2 | 0 | 0 | 100% |
| Chapter 24: Skills, Frameworks and Agent Runtimes | 9 | 6 | 0 | 3 | 0 | 0 | 100% |
| Chapter 25: Agentic Security | 6 | 4 | 0 | 2 | 0 | 0 | 100% |
| Chapter 26: Agent Identity and Authorization | 6 | 4 | 0 | 2 | 0 | 0 | 100% |
| Chapter 27: Agent Evaluation: Dimensions, Trajectories and Scorecards | 8 | 5 | 1 | 2 | 0 | 0 | 83% |
| Chapter 28: AgentOps: Observability, Telemetry and SLOs for Agents | 7 | 6 | 0 | 1 | 0 | 0 | 100% |
| Chapter 29: Agent Performance Engineering: Latency, Throughput and Cost | 7 | 5 | 0 | 1 | 0 | 1 | 100% |
| Chapter 30: Deploying Agents: From One Service to an Agent Platform | 11 | 9 | 0 | 2 | 0 | 0 | 100% |
| Capstone projects C1–C6 | 6 | 6 | 0 | 0 | 0 | 0 | 100% |
| **Total** | **243** | **163** | **1** | **62** | **14** | **3** | **99.4%** |

Failed: **27.8** (An agent scorecard: exit code 1).
<!-- results:end -->

**About the one failure.** Exercise 27.8 is a quality gate: its scorecard deliberately exits with an error when a model misses the thresholds (for the local model: 78% success against 80% required, reliability 50% against 60%, safety violations 11% against 0%). That's the exercise working as designed. Run it on Claude with `./course.sh run-chapter 27.8 --model claude`.

**What "skipped" means:** 6 *ask* exercises (you chat with the tools yourself), 4 that need a person at the keyboard (12.3–12.6), 2 that need a GitHub token (14.3, 14.4), 1 that needs a file you create (0.3), and 1 that needs the sandbox (10.7, `./course.sh sandbox up`).

## 6. Solutions

The `solutions/` folder has a worked solution for every exercise and reference versions of all six capstones. The book shows where each lives: every exercise box names its solution file, [solutions/SOLUTIONS.md](solutions/SOLUTIONS.md) lists them all, every capstone ends with a *Reference solution* table, and Appendix F maps the folder.

```bash
./course.sh solution 4.4        # show the solution for exercise 4.4
./course.sh capstone 1          # run reference capstone 1
./course.sh check-solutions     # run every solution offline (no API key needed)
```

Solutions are grouped by chapter (`solutions/exercises/ch04/`, `interlude_python/`, …). The runner and tests use a flat copy built automatically. For quick lookups in an editor, `generate_symlinks.ps1` (Windows: double-click `create_symlinks.bat`) creates `solutions/exercises/_index/` and `course/code/_index/` with a shortcut to every file. These folders are local only (Git ignores them) and safe to delete.

## 7. All commands

| Command | Purpose |
| --- | --- |
| `./course.sh setup` / `build` / `selftest` | One-time setup, build the image, offline self-test |
| `./course.sh check --api` | One real call to your model |
| `./course.sh list [chapter]` | All exercises, or one chapter's |
| `./course.sh ex <id> [--info]` | Show an exercise and start it |
| `./course.sh check <id>` | Check your answer (Chapter 0, interludes, 2.4, 3.4) |
| `./course.sh solution <id>` | Show the reference solution |
| `./course.sh python <file>` | Run any file in your workspace |
| `./course.sh ask <module> ["question"]` | Chat with a chapter's tools |
| `./course.sh shell` | A terminal inside the container |
| `./course.sh data <kind>` | More sample data: `notes --count 2000 --out notes_big`, `library`, `messy`, `repo --fresh`, `db`, `traces` |
| `./course.sh reset <file>` | Restore an original file (yours is kept as `.bak`) |
| `./course.sh inspector <server.py>` | MCP Inspector web UI on http://localhost:6274 |
| `./course.sh serve <server.py>` | An MCP server over HTTP at http://localhost:8000/mcp |
| `./course.sh desktop-config` | The Claude Desktop config that runs your server through Docker |
| `./course.sh serve-api` | The Chapter 30 agent API at http://localhost:8080 (docs at /docs) |
| `./course.sh serve-mcp` | The Chapter 30 token-protected MCP server at http://localhost:8000/mcp |
| `./course.sh serve-a2a` | The Chapter 13 A2A analyst agent (card at http://localhost:9999/.well-known/agent-card.json) |
| `./course.sh sandbox up` / `down` | Network-less test sandbox for exercise 10.7 |
| `./course.sh local up` / `status` / `down` / `logs` | The free local model |
| `./course.sh live-check [part] [--yes]` | Run every chapter's main file against the model; report in `workspace/live_report.md` |
| `./course.sh run-chapter <chapter\|id\|all\|capstones> [--model local\|claude] [--free-only] [--yes]` | Run reference solutions and save their output (section 4) |
| `./course.sh capstone <1-6> [args]` | Run a reference capstone |
| `./course.sh check-solutions` | Run every solution offline |

To deploy the Chapter 30 agent API, build `ch30_service.Dockerfile` from your workspace folder and follow exercise 30.7.

## 8. Good to know

- **Network:** the course container has internet access (the model API, Open-Meteo, web fetches). The Chapter 10 sandbox has none.
- **Ports** are published only to your own computer (127.0.0.1): 6274–6275 for the Inspector, 8000 for MCP servers over HTTP, 8080 for the agent API, 11434 for the local model.
- **Containers talking to each other (chapters 13, 19 and 30):** `serve-a2a`, `serve-api` and `serve-mcp` run in containers named `agentic-ai-a2a`, `agentic-ai-api` and `agentic-ai-mcp`. Other course containers reach them by those names; your browser uses localhost.
- **Embeddings (Chapter 18):** the image includes a small local embedding model. If it's missing, Chapter 18 falls back to the built-in hashing embedder; set `EMBEDDER=hashing` in `.env` to choose it yourself.
- **GitHub (Chapter 14, capstone 4):** add a read-only `GITHUB_PERSONAL_ACCESS_TOKEN` to `.env`.
- **Switching models:** set `MODEL=...` in `.env`.
- **Updating:** after changing `Dockerfile` or getting a new kit, run `./course.sh build`. Your workspace is never overwritten.
- **Linux:** files the container creates are owned by your user.
- **Windows:** if PowerShell blocks scripts, use `course.cmd` (it runs `course.ps1` with a one-time bypass).

## 9. Troubleshooting

| Problem | Fix |
| --- | --- |
| "Docker is not running" | Start Docker Desktop and wait until it says it's running |
| `ANTHROPIC_API_KEY is not set` | Run `./course.sh setup`, or copy `.env.example` to `.env` and put your key in it |
| Build fails pulling `ghcr.io/github/github-mcp-server` | Your network blocks ghcr.io. Add `GITHUB_MCP_IMAGE=nogithub` to `.env` and build again. Only 14.3–14.4 and capstone 4 need it |
| Port 6274, 8000, 8080 or 11434 already in use | Stop the other program, or change the left-hand port in `compose.yaml` |
| Inspector page asks for a token | Use the full link printed in the terminal (it includes the token) |
| Claude Desktop doesn't show the server | Docker Desktop must be running; fully quit and restart Claude Desktop |
| Local model: out of memory, or containers restart | Close other programs and other Docker projects, set `LOCAL_CONTEXT=8192` or `16384`, or give WSL more memory ([LOCAL_MODEL.md](LOCAL_MODEL.md), section 7) |
| Windows + NVIDIA GPU: **every** container restarts when the model loads, and a run ends with `error waiting for container: unexpected EOF` | WSL's GPU driver is in a bad state. Run `wsl --shutdown` in PowerShell (Docker Desktop restarts itself), then `./course.sh local up --gpu`. If it keeps happening, reboot, or run on the CPU with `./course.sh local up` |
| An exercise times out on the local model | Normal on a CPU for the long benchmarks. Use `--gpu`, set `LOCAL_THINKING=off`, or run that exercise on Claude |

## License

The author will choose the license for this repository before it is published. Until a `LICENSE` file is added, all rights are reserved.
