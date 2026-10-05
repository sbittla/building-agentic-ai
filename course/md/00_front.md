# How to Use This Book

This book teaches you to build AI agents from nothing. You start with the Python and web basics you need and finish with production agents that use the Model Context Protocol (MCP), retrieval, memory and frameworks, and run as secure services. You'll build a working agent in almost every chapter, practice the supporting skills in short interludes and finish with at least one of six capstone projects. This page shows you where to start, how the book is organized and how to set up the course kit once so every example runs.

## Who this is for

Anyone who wants to build AI agents, including complete beginners. You don't need machine-learning experience.

Table: Where to start
| If you… | Start at |
| --- | --- |
| Have never programmed, or aren't sure what JSON or an API is | Chapter 0 and the Python interlude, and do every exercise |
| Know some Python but have never called a web API | Chapter 0: skim it, and do exercises 0.4–0.6 |
| Write Python and have used web APIs | Chapter 1 |
| Have built a simple agent already | Read Chapter 1's frameworks, skim the rest of Part 1, then start at Chapter 5, or go straight to Part 5 (MCP and interoperability), Part 6 (context and memory), Part 7 (advanced agent architectures), Part 8 (trust, security and identity) or Part 9 (production engineering) |
| Are an architect, staff engineer or engineering leader | Chapter 1 (sections 1.3 to 1.8), section 12.1, then Chapters 15, 22, 26 to 30 and Appendix I's reference cards |
| Are a performance or reliability engineer | Chapter 1, then Chapters 19, 27, 28 and 29 |

The interludes (Python, testing, regular expressions, SQL, measuring an agent and asynchronous Python) come right before the chapters that need them. Skip any you already know; each ends with exercises so you can check yourself.

## What you will build

Table: What you build in each part
| Part | Chapters | You build | Key idea |
| --- | --- | --- | --- |
| 0. Foundations | 0 (+ Python interlude) | Python, JSON and API basics | The ground everything else stands on |
| 1. Your first agent | 1–4 (+ testing interlude) | Summarizer, calculator agent, multi-tool assistant with tool search, the agent loop | Agent = model + tools + loop |
| 2. State and environment | 5–6 (+ regex interlude) | To-do agent, notes Q&A agent | Agents change things and look around |
| 3. Real-world tools | 7–9 (+ SQL and measuring interludes) | Weather advisor, SQL analyst measured with repeated trials, file organizer | APIs fail, agents self-correct, measurements beat impressions, humans approve |
| 4. Autonomy and multi-agent systems | 10–11 (+ async interlude) | Code fixer, research team, router, handoff, critic and voting teams | Feedback loops, and when several agents beat one |
| 5. MCP and interoperability | 12–15 | MCP server, MCP client, an agent published as a server, ecosystem servers behind a policy layer, MCP requests by hand | Package tools and agents once, use them anywhere, safely |
| 6. Context, memory and knowledge | 16–18 | A context assembler, a memory store with rules, a knowledge agent that checks its citations | Decide what the agent knows at every step |
| 7. Advanced agent architectures | 19–24 | A durable job runner, a planner and model router, an orchestrated team, a rule-controlled workflow, a browser agent, the same agent on four runtimes | More independence, with code in control |
| 8. Trust, security and identity | 25–26 | An injection-resistant inbox assistant, scoped and short-lived agent tokens | Agents that can't be turned against you |
| 9. Production engineering | 27–30 | Trajectory evaluations, traces and alerts, cost budgets and a capacity plan, a deployed agent API and remote MCP server, durable MCP jobs and a gateway | Measured, observed, affordable, deployed, at company scale |
| Case study | — | The support agent through one release: decisions, evidence, an incident and a rollback | How the pieces work together |
| Capstones | — | Six end-to-end projects | Prove it on your own build |

Each part ends with a **checkpoint**: a short list of things you should now be able to do. If two or more items feel shaky, revisit the exercises the checkpoint points to before you move on.

## Reading paths

This is a long book, and you don't have to read all of it before you build something real. Pick the path that matches where you are, and come back for the rest when you need it.

Table: Three reading paths
| Path | For | Read |
| --- | --- | --- |
| **Fast path** | You want one working, safe agent soon | Chapters 0–4, 9, 12 and 16, then sections 27.1–27.3 and 30.1–30.3. Do the Simple exercises only |
| **Builder path** | You're new to agents and want the full skill set | Every part in order, with the interludes you need and the Simple and Medium exercises, then one capstone |
| **Production path** | You already build agents and want to run them at scale | Chapters 12–30, skimming Chapters 12–14 if you've used MCP before and dipping back into Chapters 9 and 11 when they're referenced, then a capstone to the full rubric |

The interludes are optional on every path: read one when a chapter uses something that's new to you.

## Thirty-minute learning paths

If you have limited time, these focused paths get you to working code or architectural understanding in half an hour:

Table: Thirty-minute learning paths
| Goal | Path | Time |
| --- | --- | --- |
| **Build your first agent** | Chapter 0 (if new to Python) + Chapter 1 (sections 1.1–1.5) + Chapter 2 (sections 2.1–2.3) | 30 min |
| **Add state and memory** | Chapter 5 (sections 5.1–5.2) + Chapter 17 (sections 17.1–17.2) | 30 min |
| **Connect real tools safely** | Chapter 2 (tool definition) + Chapter 8 (self-correction) + Chapter 9 (approval) | 30 min |
| **Route between specialists** | Chapter 11 (sections 11.1–11.2) + Chapter 21 (sections 21.1–21.2) | 30 min |
| **Publish as an MCP server** | Chapter 12 (sections 12.1–12.3) + Chapter 13 (sections 13.1–13.2) | 30 min |
| **Add retrieval (RAG)** | Chapter 16 (sections 16.1–16.2) + Chapter 18 (sections 18.1–18.2) | 30 min |
| **Make it observable** | Chapter 27 (sections 27.1–27.3) + Chapter 28 (sections 28.1–28.2) | 30 min |
| **Understand trade-offs** | Chapter 1 (sections 1.3–1.4) + Chapter 20 + Chapter 29 | 30 min |

Combine paths to go deeper: *First agent* → *Add state* → *Connect tools* → *Add retrieval* = **Agent Q&A over your files** in 2 hours.

## From first agent to production

The book is long, but the route is one line. Each milestone ends with something that runs, and a command that shows it works:

Table: Five milestones from a first agent to production
| Milestone | Chapters | You'll have | Check it with |
| --- | --- | --- | --- |
| 1. A first agent | 0–4 | A model, tools and the loop, with stop conditions | `./course.sh python ch04_agent.py` |
| 2. A useful, safe agent | 5–9 | State, files, a real API, a database and approval gates | `./course.sh ex 9.3` |
| 3. Tools anyone can use | 12–14 | Your tools as MCP servers, your own MCP host, a policy layer | `./course.sh python ch13_mcp_agent.py servers.json` |
| 4. Measured | The measurement interlude, 27 | An evaluation suite with repeated trials and a release gate | `./course.sh python ch27_eval.py eval_sql.jsonl 3` |
| 5. Deployed | 28–30 | Traces and SLOs, a cost and capacity model, a service | `./course.sh serve-api` |

The other chapters deepen each milestone: context, memory and retrieval (Part 6), long-running work, planning and teams (Part 7), and security and identity (Part 8).

## What your computer needs

Table: What your computer needs, by model
| | Claude | Free local model |
| --- | --- | --- |
| Software | Docker Desktop (Windows, macOS) or Docker Engine with Compose (Linux) | The same |
| Memory (RAM) | 16 GB recommended | 16 GB minimum, 32 GB recommended |
| Disk | About 15 GB for the image and data | About 25 GB: the image, data and the 6.6 GB model |
| Graphics card | Not needed | Optional: an NVIDIA GPU with 8 GB or more makes it fast |
| Network | To build the image once, then to reach the Claude API | To build the image and download the model once; then none |
| Money | An API key with a few dollars of credit; about $35–75 for the whole book | Nothing |

You can start with no model at all: the quick start below, the offline self-test and the 100-plus exercises marked *No model* need neither a key nor the download.

## Setup (do this once)

Everything in this book runs inside one Docker image, a packaged, ready-to-run environment: Python, Node.js, the MCP SDK, the reference MCP servers, MCP Inspector, sample data and all the chapter code. The only thing you install on your computer is **Docker**, so everyone gets exactly the same working environment.

:::warn Before you start: can this computer run Docker?
- **Installing** Docker Desktop needs administrator rights. On a work laptop, ask IT first; some companies block it.
- **Windows** needs WSL 2 and hardware virtualization switched on (Docker's installer checks both and explains how to enable them).
- **Licensing:** Docker Desktop is free for personal use, education and small businesses; larger companies need a paid subscription. Check Docker's current terms.
- **No Docker possible?** Use a cloud development environment that includes Docker (GitHub Codespaces, for example): open the kit folder there and follow the same steps.
:::

1. Install **Docker Desktop** (Windows or macOS) or Docker Engine with the Compose plugin (Linux), and start it.
2. Get the course kit, the book's companion code repository. With Git: `git clone https://github.com/sbittla/building-agentic-ai.git`. Without Git: download the ZIP from github.com/sbittla/building-agentic-ai and unzip it. Either way you end up with a folder such as `D:\Learning\building-agentic-ai`.
3. Choose your model (see "Choose your model: Claude or free and local" below). For Claude, get a Claude API key first (Chapter 0, section 0.5, walks you through it). Then open a terminal in the kit folder and run the setup. The setup checks Docker, creates your `.env` file, asks which model you want (and, for Claude, the key, without showing it) and generates the other secrets the kit needs:

```bash
./course.sh setup          # Windows: .\course.cmd setup
```

4. Build and check the image:

```bash
./course.sh build          # Windows: .\course.cmd build      (a few minutes, once)
./course.sh selftest       # offline check of the whole setup, no API key needed
./course.sh check --api    # confirms the model answers, with one tiny call
```

If you chose the free local model, run `./course.sh local up` before `check --api`. It starts the model and downloads it the first time (about 6.6 GB).

The first command also creates a **workspace** folder next to the scripts, with all the chapter code and sample data. Edit files there with any editor on your computer. The container (the running copy of the image) sees your changes immediately, and nothing you write is ever overwritten.

## Your first agent, free

Before you choose a model, see an agent work. Once the image is built, run:

```bash
./course.sh quickstart
```

It runs the real agent loop from Chapter 4 with the real date tools from Chapter 3. Only the model is replaced, by a scripted stand-in, so it needs no key and no download. You should see something like this (with today's date):

```
Question: How many days until July 4 next, and what weekday will it be?

[step 1] get_current_date({}) -> '2026-10-05 (Monday)'  (0 ms)
[step 2] days_between({"start": "2026-10-05", "end": "2027-07-04"}) -> '272 days; 2027-07-04 is a Sunday'  (0 ms)

ANSWER: It's 272 days until July 4; 2027-07-04 is a Sunday.
```

That's an agent: the model asked for a tool, your code ran it, the result went back, and the loop repeated until the model answered. Chapter 1 explains the parts and Chapter 4 builds the loop. To see a real model make the same choices on its own, choose one in "Choose your model" below, then run `./course.sh python ch04_agent.py`.

:::tip If the first commands fail
- **"Docker is not running"**: start Docker Desktop and wait until it says it's running.
- **The build stops at `ghcr.io/github/github-mcp-server`**: your network blocks that registry. Add `GITHUB_MCP_IMAGE=nogithub` to `.env` and build again; only exercises 14.3 and 14.4 and Capstone 4 need it.
- **`check --api` shows `AuthenticationError`**: the key in `.env` is missing or mistyped. Run `./course.sh setup` again.
- **"Can't reach the local model"**: start it with `./course.sh local up`, and check with `./course.sh local status`.

Appendix B has the full list, and a step-by-step playbook for when an agent runs but does the wrong thing.
:::

## Choose your model: Claude or free and local

You can work through this book with either of two models, and switch between them at any time with one line in `.env`. No code changes.

Table: Claude or the free local model
| | Claude (the default) | Free local model |
| --- | --- | --- |
| Model | `claude-sonnet-5` through the Claude API | `qwen3.5:9b`, an open-source model, in a Docker container on your computer |
| Cost | Pay per use: about $35–75 for the whole book | Free |
| Needs | An API key (Chapter 0, section 0.5) | 16 GB of RAM (32 GB recommended), 10 GB of disk; a GPU is optional |
| Speed | A few seconds per answer | A few seconds with a GPU; up to a minute or more on a CPU |
| Quality | Best: agents rarely pick the wrong tool | Good for learning; makes more mistakes from Chapter 8 on |
| Runs | Every exercise | All except the {{exercises:claude-only}} marked **Claude only** |
| Turn on | `PROVIDER=claude` in `.env` (or no `PROVIDER` line) | `./course.sh local up`, then `PROVIDER=local` in `.env` |

**Why your results may differ from the book's.** A model's answers vary from run to run, and two models differ more. The sample outputs in the chapters show one run of one model; on the local model, expect different wording, more steps, and more mistakes in tool choice and self-correction, especially from Chapter 8 on, plus slower answers on a CPU. The concepts and the code are the same, and every exercise's *Done when* line describes behavior (the right tool, a refused action, a correct number), not exact text. If a local-model run goes wrong, run it again, then compare with the same exercise on Claude: when one model fails where another succeeds, you've learned something about the model, not about your code. Appendix H lists what the local model does differently, and which exercises need Claude.

A good plan on a tight budget: do the book on the local model, and add a small Claude credit (a few dollars) for the {{exercises-word:claude-only}} **Claude only** exercises and the {{exercises-word:claude-rec}} marked **Claude recommended**. Appendix H has the full local-model guide: hardware, GPUs, Macs, speed tips and exactly what the kit adapts for you. The kit's repository has the same guide as `LOCAL_MODEL.md`, kept up to date.

:::tip Changing the Claude model
With Claude, the examples read the model name from the `MODEL` environment variable and default to `claude-sonnet-5`, which balances speed and cost well for learning. Model names change over time, so check the current list at platform.claude.com/docs/en/models/overview. To switch, set `MODEL=...` in your `.env` file. With the local model, the kit uses `LOCAL_MODEL` instead (default `qwen3.5:9b`).
:::

## Running exercises

Every exercise has a **Run** line with the command that starts it. For example:

```bash
./course.sh list 4         # the exercises in chapter 4
./course.sh ex 4.2         # show exercise 4.2 and run it
./course.sh ex 1.5         # first run creates workspace/exercises/ex1_5_workflow.py
```

Concept exercises create an answer file in `workspace/answers`. Build exercises create a starter file in `workspace/exercises` the first time, with the function names and examples already in place. You fill in the `TODO`s and run the same command again. Exercises in Chapter 0, the interludes and a few early chapters also have an automatic check: `./course.sh check 0.4` tells you whether your answer is right, and what's wrong if it isn't. You can also run any chapter file directly (for example, `./course.sh python ch04_agent.py`) or chat with a chapter's tools using `./course.sh ask ch08_sql_tools`. Appendix A lists every command. On Windows, use `.\course.cmd` wherever this book shows `./course.sh`.

## How each chapter is organized

Every chapter follows the same pattern:

1. **Learning objectives**: what you can do after the chapter.
2. **Real-world connection**: a production system that uses the same pattern.
3. **Lessons**: numbered subtopics, each with an explanation and runnable code.
4. **Common mistakes**: the bugs people hit most often.
5. **Summary**: the chapter's key points, in a short bulleted list.
6. **Exercises** at four levels:
    - **Concept**: no code. Explain, classify or design. Checks understanding.
    - **Simple**: a small change to the chapter's code. Builds confidence.
    - **Medium**: a new feature that needs a design decision. Builds skill.
    - **Complex**: an open-ended build with measurements. Builds judgment.
7. **Learn more**: free, trustworthy sites for the chapter's topics, marked **Start here** or **Go deeper**. Appendix G adds where to ask for help, free courses and how to keep up to date. The kit's `RESOURCES.md` has every link ready to click.

Each exercise has a **Done when** line that tells you when you've finished, and most have a **Hint**. A **Model** label on every exercise tells you what it needs:

Table: Exercises by the model they need
| Label | Meaning | Exercises |
| --- | --- | --- |
| **No model** | Plain Python, SQL, tests or design work: nothing calls a model, so it's free | {{exercises:none}} |
| **qwen3.5:9b or Claude** | Runs on the free local model or on Claude | {{exercises:any}} |
| **Claude recommended** | Runs on `qwen3.5:9b`, but the result is much better with Claude | {{exercises:claude-rec}} |
| **Claude only** | Uses a feature that only runs on Anthropic's servers, or the Claude Desktop app | {{exercises:claude-only}} |

## What this book covers, and what it doesn't

This is a book about building agents. Everything else it teaches, it teaches only as far as agents need it. Chapter 0 and the interludes are focused tours, not complete courses: they give you enough to read and write the code in the chapters that follow, and each one ends with a **Learn more** list for when you want the full picture.

Table: Topics the book teaches only as far as agents need them
| Topic | What this book gives you | Where to learn the rest |
| --- | --- | --- |
| Python | The fundamentals the chapters use, listed in a table in the Python interlude | The official Python tutorial, Python for Everybody, CS50 Python |
| Terminal, JSON, HTTP, Docker | Enough to run the course kit and call web APIs | Chapter 0's Learn more list (MDN, Docker docs) |
| Testing, regular expressions, SQL, measurement, async | One interlude each, sized to the chapter that needs it | Each interlude's Learn more list |
| Machine learning | Not covered. You use models; you don't train them | Not needed here; if you're curious, fast.ai's free Practical Deep Learning course (course.fast.ai) |
| Web front ends, cloud operations | Only what it takes to put an agent behind an API (Chapter 30) | Chapter 30's Learn more list |
| Agent frameworks | The ideas behind them, plus a short tour (Chapter 24) | Each framework's own documentation |

If something in a chapter feels too fast, that's your cue to spend an hour with the linked resource, not a sign that you're behind. Appendix G collects every link in one place.

## Your pace

There's no schedule to keep. How long the book takes depends on what you already know, how many exercises you do and how deep you go, and every reader's path is different. A few habits help:

- **Go one part at a time.** Each part ends with a checkpoint; when you can do what it lists, move on.
- **Skip what you know.** If an interlude or an early chapter is familiar, do its last exercise to check yourself and keep going.
- **Do the Simple and Medium exercises first.** Complex exercises and capstones are worth a second pass, once the whole picture is clear.
- **Short, regular sessions beat long, rare ones.** An hour on most days keeps the ideas fresh from one chapter to the next.

## Code conventions

All code lives in one flat folder (your workspace), and every file starts with its chapter number: `ch04_agent.py`, `ch07_weather_tools.py` and so on. Later chapters import earlier files, the way a real project grows. For example, `from ch04_agent import run_agent` appears in almost every chapter after Chapter 4.

The examples use the Anthropic Python SDK because it keeps the tool-calling messages visible. The concepts carry over to any LLM (large language model) provider that supports tool calling. Once you understand the agent loop in Chapter 4, moving to another SDK is mostly a matter of renaming fields; section 24.6 shows exactly what changes.

## Solutions

The kit has two folders of code:

Table: The two folders of code in the kit
| Folder | What's in it | How you use it |
| --- | --- | --- |
| `course/code` | The chapter programs you read in each chapter, such as `ch04_agent.py` | Copied into your `workspace` folder on first run; you run and edit them there |
| `solutions` | A worked solution for every exercise, sample answers and every capstone | Read-only reference; look after you've tried the exercise |

You can reach the solutions in three ways:

- **Every exercise box** ends with two commands, `./course.sh ex <id>` to run the exercise and `./course.sh solution <id>` to print its solution, and names the solution file.
- **`solutions/SOLUTIONS.md`** in the kit lists every exercise, chapter by chapter, with its file and what the solution shows, so you can browse the `solutions` folder without the command.
- **Every capstone** ends with a *Reference solution* table describing its files, and `./course.sh capstone <n>` runs it.

```bash
./course.sh solution 4.4        # the solution for exercise 4.4
./course.sh capstone 1          # run the reference support-agent capstone
./course.sh check-solutions     # every solution and capstone, offline, no API key
```

Appendix F maps the whole `solutions` folder. Try each exercise yourself before you look: getting stuck and working your way out is where most of the learning happens. When you've finished, compare your version with the solution. There's usually more than one good answer, and seeing a different approach teaches you something too.

## Cost and safety

With Claude, every model call costs money, and an agent makes many calls per question. With Claude Sonnet 5, doing every chapter and exercise typically costs **$35–75 in total**; Appendix E breaks this down by part. With the free local model (Appendix H), calls cost nothing but time. Chapter 4 shows you how to log token counts so you always know what a run cost. To keep costs down:

- Set a monthly spending limit in the Claude Console before you start.
- Use a smaller, cheaper model while developing (set `MODEL=claude-haiku-4-5` in `.env`) and a larger one for evaluations.
- Use `./course.sh check-solutions` to test code paths for free; it uses a stand-in model.
- Always keep the `max_iterations` cap from Chapter 4.
- Never give an agent write access to anything you care about until Chapter 9 has taught you approval gates.

## Learn more

Free, trustworthy places to read more about building agents in general. Every chapter ends with its own list like this one. Start with the **Start here** rows; **Go deeper** rows are for when you want more detail. Links were checked in September 2026; if one has moved, search for its title.

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic Academy (free courses)**<br>[anthropic.skilljar.com](https://anthropic.skilljar.com) | Free video courses on the Claude API, MCP and Claude Code, with certificates | Start here |
| **Claude Developer Platform docs**<br>[platform.claude.com/docs/en/home](https://platform.claude.com/docs/en/home) | The official reference for everything the book calls through the API | Start here |
| **Anthropic courses on GitHub**<br>[github.com/anthropics/courses](https://github.com/anthropics/courses) | Free notebooks: API fundamentals, prompt engineering, tool use | Start here |
| **Claude Cookbooks**<br>[github.com/anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks) | Short, runnable recipes for common tasks (tools, RAG, caching, agents) | Go deeper |
| **Hugging Face AI Agents Course**<br>[huggingface.co/learn/agents-course](https://huggingface.co/learn/agents-course) | A free, vendor-neutral course on agents, good as a second viewpoint | Go deeper |

With the kit installed and your model answering, you're ready for Chapter 0. It covers the foundations every later chapter assumes: the terminal, the Python you'll read, JSON, web APIs, keeping secrets safe and what Docker is doing for you.
