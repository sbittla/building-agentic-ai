# How to Use This Book

This book teaches you to build AI agents from nothing. You start with the Python and web basics you need and finish with production agents that use the Model Context Protocol (MCP), retrieval, memory and frameworks, and run as secure services. You'll build a working agent in almost every chapter, practice the supporting skills in short interludes and finish with at least one of seven capstone projects. This page shows you where to start, how the book is organized and how to set up the course kit once so every example runs. There's no schedule to keep: go one part at a time, skip what you know, and do the Simple and Medium exercises before the Complex ones.

## Who this is for

Anyone who wants to build AI agents, including complete beginners. You don't need machine-learning experience.

Table: Where to start
| If you… | Start at |
| --- | --- |
| Have never programmed, or aren't sure what JSON or an API is | The optional beginner path: Chapter 0 and the Python interlude, with every exercise |
| Know some Python but have never called a web API | Chapter 0: skim it, and do exercises 0.4–0.6; skip the Python interlude |
| Write Python and have used web APIs | Chapter 1, after setting up the kit (section 0.1) and your key (section 0.5); skip the beginner path |
| Have built a simple agent already | Read Chapter 1's frameworks, skim the rest of Part 1, then start at Chapter 5, or go straight to Part 5 (MCP and interoperability), Part 6 (context and memory), Part 7 (advanced agent architectures), Part 8 (trust, security and identity) or Part 9 (production engineering) |
| Are an architect, staff engineer or engineering leader | Chapter 1 (sections 1.3 to 1.8), section 12.1, then Chapters 15, 22, 26 to 30 and Appendix I's reference cards |
| Are a performance or reliability engineer | Chapter 1, then Chapters 19, 27, 28 and 29 |
| Build agents for customers, or are preparing for a forward-deployed engineer interview | The forward-deployed path below, then `INTERVIEW_PREP.md` in the course kit |

The interludes (Python, testing, regular expressions, SQL, measuring an agent and asynchronous Python) come right before the chapters that need them. Skip any you already know; each ends with exercises so you can check yourself.

## What you will build

Table: What you build in each part
| Part | Chapters | You build | Key idea |
| --- | --- | --- | --- |
| 0. Foundations (optional beginner path) | 0 (+ Python interlude) | Python, JSON and API basics | The ground everything else stands on |
| 1. Your first agent | 1–4 (+ testing interlude) | Summarizer, calculator agent, multi-tool assistant with tool search, the agent loop | Agent = model + tools + loop |
| 2. State and environment | 5–6 (+ regex interlude) | To-do agent, notes Q&A agent | Agents change things and look around |
| 3. Real-world tools | 7–9 (+ SQL and measuring interludes) | Weather advisor, SQL analyst measured with repeated trials, file organizer | APIs fail, agents self-correct, measurements beat impressions, humans approve |
| 4. Autonomy and multi-agent systems | 10–11 (+ async interlude) | Code fixer, research team, router, handoff, critic and voting teams | Feedback loops, and when several agents beat one |
| 5. MCP and interoperability | 12–15 | MCP server, MCP client, an agent published as a server, ecosystem servers behind a policy layer, MCP requests by hand | Package tools and agents once, use them anywhere, safely |
| 6. Context, memory and knowledge | 16–18 | A context assembler, a memory store with rules, a knowledge agent that checks its citations | Decide what the agent knows at every step |
| 7. Advanced agent architectures | 19–24 | A durable job runner, a planner and model router, an orchestrated team, a rule-controlled workflow, a browser agent, the same agent on four runtimes | More independence, with code in control |
| 8. Trust, security and identity | 25–26 | An injection-resistant inbox assistant, scoped and short-lived agent tokens | Agents that can't be turned against you |
| 9. Production engineering | 27–30 | Trajectory evaluations, traces and alerts, cost budgets and a capacity plan, a deployed agent API and remote MCP server, durable MCP jobs and a gateway | Measured, observed, affordable, deployed, at company scale |
| 10. In the field | 31 | A field kit: a brief checker, a slice ranker, a design checker for the customer's rules, a pilot gate and a handoff check | Ship an agent inside someone else's business, on their terms |
| Case study | — | The support agent through one release: decisions, evidence, an incident and a rollback | How the pieces work together |
| Capstones | — | Seven end-to-end projects, the last one a whole customer engagement | Prove it on your own build |

Each part ends with a **checkpoint**: a short list of things you should now be able to do. If two or more items feel shaky, revisit the exercises the checkpoint points to before you move on.

## Reading paths

This is a long book, and you don't have to read all of it before you build something real. Find your role below; the row is your route through the book. Come back for the rest when you need it.

Table: Learning paths by role
| Path | For | Read, in this order | Finish with |
| --- | --- | --- | --- |
| **Beginner** | You're new to programming, or new to agents | Chapter 0 and the interludes you need → first agent (Chapters 1–4) → state and real tools (Chapters 5–9) → measuring an agent (the measurement interlude, sections 27.1–27.3) → your first MCP server (Chapter 12). Simple exercises first | Capstone 1 |
| **Agent engineer** | You write Python and want to build capable agents | Chapters 1–4 quickly → state, tools and approvals (Chapters 5–9) → feedback loops and teams (Chapters 10–11) → MCP (Chapters 12–15) → context, memory and knowledge (Chapters 16–18) → architectures (Chapters 19–24) → evaluation (Chapter 27). Simple and Medium exercises | Capstone 2 or 5 |
| **Production agent engineer** | You already run services and must ship agents safely | Architecture (sections 1.7, 1.10, 22.1 and 30.15) → security (Chapters 9, 14, 25 and 26, starting with the security boundary in section 25.2) → evaluation (Chapter 27) → performance and cost (Chapter 29) → deployment (Chapter 30) → AgentOps (Chapter 28, sections 30.13 and 30.14) | The case study, then Capstone 3 |
| **Advanced architect** | You design agent platforms and set standards | Multi-agent systems (Chapters 11 and 21) → discovery (Chapter 15, sections 26.9 and 26.10) → skills (sections 24.7 and 24.10) → memory (Chapter 17) → governance (sections 25.11 and 30.12) → economics (sections 21.10 and 29.9) → long-running systems (Chapters 19 and 20) | Appendix K's decision records, then Capstone 6 |
| **Forward-deployed engineer** | You build agents with and for customers, or are interviewing for these roles | Chapters 1–4 quickly → approvals (Chapter 9) → the system prompt and context (section 4.10, Chapter 16) → retrieval (Chapter 18) → security and identity (sections 25.1–25.5, Chapter 26) → evaluation (Chapter 27) → cost and payback (sections 29.1 and 29.9) → deployment and lifecycle (sections 30.1–30.7 and 30.13) → customer production (Chapter 31) | Capstone 7, then `FIELD_GUIDE.md` and `INTERVIEW_PREP.md` in the course kit |

In a hurry? Chapters 0–4, 9, 12 and 16, then sections 27.1–27.3 and 30.1–30.3, give you one working, safe agent behind an API (section 30.2).

Every path skips what you already know: if a chapter's Prerequisites line names something new to you, read that first. The interludes are optional on every path: read one when a chapter uses something that's new to you.

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

## Setup (do this once)

Everything in this book runs inside one Docker image, a packaged, ready-to-run environment with Python, Node.js, the MCP SDK, the reference MCP servers, sample data and all the chapter code. The only thing you install is **Docker** (Docker Desktop on Windows and macOS, Docker Engine with Compose on Linux). Then get the course kit, the book's companion repository: `git clone https://github.com/sbittla/building-agentic-ai.git`, or download the ZIP from github.com/sbittla/building-agentic-ai. Open a terminal in the kit folder and run:

```bash
./course.sh setup          # checks Docker, creates .env, asks Claude or local model (and the key)
./course.sh build          # builds the image (a few minutes, once)
./course.sh selftest       # offline check of the whole setup, no API key needed
./course.sh check --api    # confirms the model answers, with one tiny call
```

On Windows, use `.\course.cmd` wherever this book shows `./course.sh`. With the free local model, run `./course.sh local up` before `check --api`; it downloads the model the first time (about 6.6 GB). The first command also creates a **workspace** folder with all the chapter code and sample data: edit files there with any editor, and the container sees your changes immediately. Appendix A has the details: what your computer needs, Docker on work laptops and Windows, and what to do if a command fails.

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

That's an agent: the model asked for a tool, your code ran it, the result went back, and the loop repeated until the model answered. Chapter 1 explains the parts and Chapter 4 builds the loop. To see a real model make the same choices on its own, choose one (next section), then run `./course.sh python ch04_agent.py`.

## Choose your model: Claude or free and local

You can work through this book with either of two models, and switch between them at any time with one line in `.env`. No code changes.

Table: Claude or the free local model
| | Claude (the default) | Free local model |
| --- | --- | --- |
| Model | `claude-sonnet-5` through the Claude API | `qwen3.5:9b`, an open-source model, in a Docker container on your computer |
| Cost | Pay per use: about {{cost:learner}} for the whole book | Free |
| Needs | An API key (Chapter 0, section 0.5) | 16 GB of RAM (32 GB recommended), 10 GB of disk; a GPU is optional |
| Speed | A few seconds per answer | A few seconds with a GPU; up to a minute or more on a CPU |
| Quality | Best: agents rarely pick the wrong tool | Good for learning; makes more mistakes from Chapter 8 on |
| Runs | Every exercise | All except the {{exercises:claude-only}} marked **Claude only** |
| Turn on | `PROVIDER=claude` in `.env` (or no `PROVIDER` line) | `./course.sh local up`, then `PROVIDER=local` in `.env` |

**Why your results may differ from the book's.** A model's answers vary from run to run, and two models differ more. The sample outputs show one run of one model, so every exercise's *Done when* line describes behavior (the right tool, a refused action, a correct number), not exact text. When one model fails where another succeeds, you've learned something about the model, not about your code. To change the Claude model, set `MODEL=...` in `.env` (the default is `claude-sonnet-5`); model names change, so check platform.claude.com/docs/en/models/overview.

A good plan on a tight budget: do the book on the local model, and add a few dollars of Claude credit for the {{exercises-word:claude-only}} **Claude only** exercises and the {{exercises-word:claude-rec}} marked **Claude recommended**. Appendix H is the local-model guide.

## How each chapter is organized

Every chapter follows the same pattern. It opens with what you'll build, where it sits in the agent architecture (section 1.7), its **Prerequisites** and its **Learning objectives**, then a production system that uses the same pattern (**In the real world**). The numbered **lessons** follow, each with an explanation and runnable code; a listing marked *excerpt* shows the parts that teach, and the full file is in the kit. **Common mistakes** lists the bugs people hit most often, **Key takeaways** sums up the chapter, and **Learn more** names the best free places to start, with every link, including the **Go deeper** reading, in the kit's `RESOURCES.md`.

The **Exercises** come at four levels: **Concept** (no code: explain, classify or design), **Simple** (a small change to the chapter's code), **Medium** (a new feature that needs a design decision) and **Complex** (an open-ended build with measurements). Each has a **Done when** line, a measurable outcome that tells you when you've finished; long exercises print a short brief, and the kit shows the full one. Run any exercise with `./course.sh ex <id>` (the first run of a build exercise creates a starter file in `workspace/exercises` for you to fill in), check it with `./course.sh check <id>` where a checker exists, and print its reference solution with `./course.sh solution <id>`. `./course.sh list 4` lists Chapter 4's exercises, and `CHAPTER_OUTCOMES.md` in the kit lists every chapter's outcomes. Each exercise box also names the model it needs:

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

If something in a chapter feels too fast, that's your cue to spend an hour with the linked resource, not a sign that you're behind. `RESOURCES.md` in the kit collects every link in one place.

## Code conventions

All code lives in one flat folder (your workspace), and every file starts with its chapter number: `ch04_agent.py`, `ch07_weather_tools.py` and so on. Later chapters import earlier files, the way a real project grows. For example, `from ch04_agent import run_agent` appears in almost every chapter after Chapter 4.

The examples use the Anthropic Python SDK because it keeps the tool-calling messages visible. The concepts carry over to any LLM (large language model) provider that supports tool calling. Once you understand the agent loop in Chapter 4, moving to another SDK is mostly a matter of renaming fields; section 24.6 shows exactly what changes.

## Solutions

The kit's `course/code` folder holds the chapter programs, copied into your `workspace` on first run; `solutions` holds a worked solution for every exercise, sample answers and every capstone, read-only. Besides `./course.sh solution <id>`, `solutions/SOLUTIONS.md` lists every exercise with its file, and `./course.sh capstone <n>` runs a reference capstone; `./course.sh check-solutions` runs them all offline, with no API key. Appendix F maps the folder. Try each exercise before you look: getting stuck and working your way out is where most of the learning happens, and there's usually more than one good answer.

## Cost and safety

With Claude, every model call costs money, and an agent makes many calls per question. With Claude Sonnet 5, doing every chapter and exercise costs about **{{cost:learner}} in total**, counting reruns ({{cost:first}} for one clean pass); Appendix E breaks this down by part and states every assumption. With the free local model (Appendix H), calls cost nothing but time. Chapter 4 shows you how to log token counts so you always know what a run cost. To keep costs down:

- Set a monthly spending limit in the Claude Console before you start.
- Use a smaller, cheaper model while developing (set `MODEL=claude-haiku-4-5` in `.env`) and a larger one for evaluations.
- Use `./course.sh check-solutions` to test code paths for free; it uses a stand-in model.
- Always keep the `max_iterations` cap from Chapter 4.
- Never give an agent write access to anything you care about until Chapter 9 has taught you approval gates.

## Learn more

Start with these. `RESOURCES.md` in the course kit has all 5 links, including the **Go deeper** reading, ready to click.

| Resource | What you'll find |
| --- | --- |
| **Anthropic Academy (free courses)**<br>[anthropic.skilljar.com](https://anthropic.skilljar.com) | Free video courses on the Claude API, MCP and Claude Code, with certificates |
| **Claude Developer Platform docs**<br>[platform.claude.com/docs/en/home](https://platform.claude.com/docs/en/home) | The official reference for everything the book calls through the API |
| **Anthropic courses on GitHub**<br>[github.com/anthropics/courses](https://github.com/anthropics/courses) | Free notebooks: API fundamentals, prompt engineering, tool use |

With the kit installed and your model answering, you're ready for Chapter 0. It covers the foundations every later chapter assumes: the terminal, the Python you'll read, JSON, web APIs, keeping secrets safe and what Docker is doing for you.
