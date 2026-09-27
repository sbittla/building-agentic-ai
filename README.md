# Building Agentic AI Systems: code, exercises and solutions

The companion repository for the book *Building Agentic AI Systems: From First Agent to MCP, Multi-Agent Orchestration, and Production* by Srinivasa Rao Bittla. It has every chapter's code, 173 exercises with starter files, checkers and reference solutions, six capstone projects, and a Docker image that runs all of it.

```bash
git clone https://github.com/sbittla/building-agentic-ai.git
cd building-agentic-ai
```

No Git? Download the ZIP from the repository page and unzip it anywhere.

Everything for the course runs inside one Docker image, so the only thing you install on your computer is Docker. You edit files on your computer with any editor; Docker runs them.

## 1. One-time setup

1. Install **Docker Desktop** (Windows or macOS) or **Docker Engine** with the Compose plugin (Linux), and start it. Installing needs admin rights; on Windows it also needs WSL 2 and virtualization switched on.
2. Clone this repository (or unzip the download) anywhere, for example `D:\Learning\building-agentic-ai`.
3. Choose a model: **Claude** (get an Anthropic API key from the Claude Console; Chapter 0 of the book walks you through it) or the **free local model** `qwen3.5:9b` (see below). Then run the setup. It checks Docker, creates `.env`, asks which model you want (and, for Claude, your key, without showing it), and generates the other secrets the course needs:

| | macOS / Linux | Windows (PowerShell or Command Prompt) |
| --- | --- | --- |
| Setup | `./course.sh setup` | `.\course.cmd setup` |
| Build | `./course.sh build` | `.\course.cmd build` |
| Offline self-test | `./course.sh selftest` | `.\course.cmd selftest` |
| Check the model answers | `./course.sh check --api` | `.\course.cmd check --api` |

The first command after setup also creates a `workspace` folder next to the scripts, containing all course code and sample data. **That folder is yours**: edit files there, and they're kept between runs.

### Free local model (no API key, no cost)

The kit can run an open-source model, **`qwen3.5:9b`**, in Docker on your computer, and the book's code uses it unchanged. You need 16 GB of RAM (32 GB recommended) and about 10 GB of disk space; a GPU is optional.

| | macOS / Linux | Windows |
| --- | --- | --- |
| Start it (downloads about 6.6 GB the first time) | `./course.sh local up` | `.\course.cmd local up` |
| The same, with an NVIDIA GPU | `./course.sh local up --gpu` | `.\course.cmd local up --gpu` |
| Is it running? | `./course.sh local status` | `.\course.cmd local status` |
| Stop it and free the memory | `./course.sh local down` | `.\course.cmd local down` |

Then put `PROVIDER=local` in `.env` (setup does this if you choose option 2). Set it back to `PROVIDER=claude` to use Claude. Every exercise shows which model it needs: `./course.sh list` marks the 4 **Claude recommended** and 5 **Claude only** ones; all the others run locally, and 81 need no model at all. `course/local_adapter.py` bridges the few Claude features a local model lacks (forced tools, structured outputs, prompt caching). **Full step-by-step guide: [LOCAL_MODEL.md](LOCAL_MODEL.md)** (the same as Appendix H of the book), including Windows, Macs, GPUs, checking every exercise with `./course.sh live-check exercises`, and troubleshooting.

## 2. Doing the exercises

## 📚 Exercise Index

**[EXERCISE_INDEX.md](EXERCISE_INDEX.md)** — Complete directory of all 130+ exercises organized by chapter.

Find any exercise instantly with:
- Chapter-by-chapter organization (Ch 0 through Ch 30)
- Direct file paths for each exercise
- How to run each one (`./course.sh solution X.Y`)
- Where outputs are saved
- Interludes and capstone projects

Use Ctrl+F to search by chapter number, exercise name, or topic.


```
./course.sh list            # all 173 exercises
./course.sh list 4          # just chapter 4 (interludes: list T, R, S or A)
./course.sh ex 4.2          # show exercise 4.2 and run it
./course.sh ex 4.2 --info   # just show it
./course.sh check 0.4       # check your answer (Chapter 0, the interludes, 2.4 and 3.4)
```

What `ex` does depends on the exercise:

| Exercise type | What happens |
| --- | --- |
| Concept | Creates `workspace/answers/exN_M.md` with the question. Write your answer there. |
| Run a chapter file | Runs it (for example `python ch04_agent.py`). Edit the file first if the exercise says so. |
| Chat with the tools | Starts a chat with that chapter's tools (you can also use `./course.sh ask ch08_sql_tools`). |
| Build something new | First run creates a starter file in `workspace/exercises/` (with function names and examples for the early chapters). Fill it in, then run `ex` again. |
| Write tests | First run creates `workspace/tests/test_exN_M_*.py`. Write the tests, then run `ex` again. |
| MCP Inspector | Opens the Inspector at http://localhost:6274 for the server. |

On Windows, replace `./course.sh` with `.\course.cmd` everywhere.

## 3. Solutions

The `solutions` folder has a worked solution for every exercise and reference versions of all six capstones. Try each exercise first, then compare:

```
./course.sh solution 4.4        # show the solution for exercise 4.4
./course.sh capstone 1          # run reference capstone 1 (needs your API key)
./course.sh check-solutions     # run every solution offline (no API key needed)
```

The book shows where each solution lives: every exercise box names its solution file, `solutions/SOLUTIONS.md` lists them all, every capstone ends with a *Reference solution* table, and Appendix F maps the whole folder. See `solutions/README.md` for how to run solutions and capstones with a real model.

## Where to learn more

`RESOURCES.md` lists every reference from the book, ready to click: free courses, official documentation for each chapter's topics, where to ask for help when you're stuck, and how to keep up to date. The book has the same links in each chapter's *Learn more* section and in Appendix G.

## 4. Other commands

| Command | Purpose |
| --- | --- |
| `./course.sh python ch07_weather_tools.py` | Run any file in your workspace |
| `./course.sh ask <module> ["question"]` | Chat with a chapter's tools |
| `./course.sh shell` | A terminal inside the container |
| `./course.sh data notes --count 2000 --out notes_big` | Make more sample data (also: `library`, `messy`, `repo --fresh`, `db`) |
| `./course.sh reset ch04_agent.py` | Restore an original file (yours is kept as `.bak`) |
| `./course.sh inspector ch12_weather_server.py` | MCP Inspector web UI on http://localhost:6274 |
| `./course.sh serve ch12_weather_server.py` | MCP server over HTTP at http://localhost:8000/mcp |
| `./course.sh desktop-config` | Print the Claude Desktop config that runs your server through Docker |
| `./course.sh serve-api` | The chapter 30 agent API at http://localhost:8080 (docs at /docs) |
| `./course.sh serve-mcp` | The chapter 30 token-protected MCP server at http://localhost:8000/mcp |
| `./course.sh serve-a2a` | The chapter 13 A2A analyst agent; its card is at http://localhost:9999/.well-known/agent-card.json |
| `./course.sh sandbox up` / `down` | Network-less test sandbox for exercise 10.7 |
| `./course.sh live-check [part] [--yes]` | Run every chapter's main file against the real model (about $1); report in `workspace/live_report.md` |
| `./course.sh run-chapter <chapter\|all> [--model local\|claude] [--free-only] [--yes]` | Run every exercise of a chapter (or `all`, in book order, then the capstones) with its reference solution in a scratch copy of your workspace; each exercise's full output goes to `solutions/outputs/chNN/<id>.log`, plus `summary.json` and an index in `solutions/outputs/README.md`. Uses the free local model by default (run `./course.sh local up` first); `--model claude` (or `RUN_MODEL=claude`) uses your API key; `--free-only` runs only the exercises that need no model. Double-click `run-chapters.cmd` (Windows) or run `./run-chapters.sh` to run them all |

To deploy the Chapter 30 agent API, build `ch30_service.Dockerfile` from your workspace folder on your own computer and follow exercise 30.7. To test the book with real learners before publishing, follow `PILOT.md`.

## 5. Good to know

- **Network:** the course container has internet access (the model API, Open-Meteo, web fetches). The chapter 10 sandbox has none.
- **Ports** are published only to your own computer (127.0.0.1): 6274–6275 for the Inspector, 8000 for MCP servers over HTTP, 8080 for the chapter 30 agent API.
- **Two containers talking (chapters 13 and 19):** `serve-a2a`, `serve-api` and `serve-mcp` run in containers named `agentic-ai-a2a`, `agentic-ai-api` and `agentic-ai-mcp`; other course containers reach them by those names, and your browser uses localhost.
- **Chapter 18 embedding model:** the build downloads a small model (about 30 MB) from Hugging Face. If that's blocked, chapter 18 uses the built-in hashing embedder instead; set `EMBEDDER=hashing` in `.env` to choose it yourself.
- **GitHub (chapter 14, capstone 4):** add a read-only `GITHUB_PERSONAL_ACCESS_TOKEN` to `.env`.
- **Model:** set `MODEL=...` in `.env` to switch models.
- **Updating:** after changing `Dockerfile` or getting a new kit, run `./course.sh build`. Your workspace is never overwritten; `./course.sh reset <file>` restores single files.
- **Linux:** files created by the container are owned by your user automatically.
- **Windows:** if PowerShell blocks scripts, use `course.cmd` (it runs `course.ps1` with a one-time bypass).

## 6. Troubleshooting

| Problem | Fix |
| --- | --- |
| "Docker is not running" | Start Docker Desktop and wait until it says it's running |
| Build fails pulling `ghcr.io/github/github-mcp-server` | Your network blocks ghcr.io. Add `GITHUB_MCP_IMAGE=nogithub` to `.env` and run the build again. Only exercises 14.3–14.4 and capstone 4 need it |
| `ANTHROPIC_API_KEY is not set` | Create `.env` from `.env.example` next to the scripts |
| Port 6274, 8000 or 8080 already in use | Stop the other program, or change the left-hand port in `compose.yaml` |
| Inspector page asks for a token | Use the full link printed in the terminal (it includes the token) |
| Claude Desktop doesn't show the server | Docker Desktop must be running; fully quit and restart Claude Desktop |

## License

The author will choose the license for this repository before it is published. Until a `LICENSE` file is added, all rights are reserved.
