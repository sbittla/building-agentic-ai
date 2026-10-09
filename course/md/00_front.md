# How to Use This Book

Fifteen minutes from now, an agent can be running on your computer, picking its own tools to answer a question a plain chatbot gets wrong. This page gets you there: where to start, how the book is organized and how to set up the course kit once. After that, you'll build a working agent in almost every chapter, all the way to production agents that use the Model Context Protocol (MCP), retrieval and memory. There's no schedule. Skip what you know, and do the Simple and Medium exercises before the Complex ones.

## Who this is for

Anyone who wants to build AI agents, including complete beginners; you don't need machine-learning experience. Find the row that sounds most like you, and it points to one of the reading paths below.

Table: Where to start
| If you… | Follow | Start at |
| --- | --- | --- |
| Have never programmed, or aren't sure what JSON or an API is | The beginner path | Chapter 0 and the Python interlude, with every exercise |
| Know some Python but have never called a web API | The beginner path | Chapter 0: skim it and do exercises 0.4–0.6; skip the Python interlude |
| Write Python and have used web APIs, or have built a simple agent | The agent engineer path | Chapter 1, after setting up the kit (section 0.1) and your key (section 0.5) |
| Already run services, or work on performance and reliability | The production path | Chapters 1–4, quickly |
| Design platforms or set standards as an architect or engineering leader | The architect path | Chapter 1's frameworks (sections 1.3–1.10) |
| Build agents for customers, or are preparing for a forward-deployed engineer interview | The forward-deployed path | Chapters 1–4, quickly, with `INTERVIEW_PREP.md` from the course kit beside you |

Short interludes on Python, testing, regular expressions, SQL, measurement and async code sit right before the chapters that need them. Skip any you know; their exercises tell you whether you can.

## What you will build

Table: What you build in each part
| Part | Chapters | You build | Key idea |
| --- | --- | --- | --- |
| 0. Foundations (optional) | 0 (+ Python interlude) | Python, JSON and API basics | The ground everything stands on |
| 1. Your first agent | 1–4 (+ testing interlude) | Summarizer, calculator agent, the agent loop | Agent = model + tools + loop |
| 2. State and environment | 5–6 (+ regex interlude) | To-do agent, notes Q&A agent | Agents change things and look around |
| 3. Real-world tools | 7–9 (+ SQL and measuring interludes) | Weather advisor, SQL analyst, file organizer | APIs fail, agents self-correct, humans approve |
| 4. Autonomy and multi-agent systems | 10–11 (+ async interlude) | Code fixer, research team, router, critic and voting teams | When several agents beat one |
| 5. MCP and interoperability | 12–15 | MCP server and client, an agent as a server, a policy layer | Package tools once, use them anywhere |
| 6. Context, memory and knowledge | 16–18 | Context assembler, memory store, citation-checking knowledge agent | Decide what the agent knows |
| 7. Advanced agent architectures | 19–24 | Durable job runner, planner, orchestrated team, rule-controlled workflow, browser agent | More independence, code in control |
| 8. Trust, security and identity | 25–26 | Injection-resistant inbox assistant, short-lived agent tokens | Agents that can't be turned against you |
| 9. Production engineering | 27–30 | Evaluations, traces and alerts, cost budgets, a deployed agent API | Measured, observed, affordable, deployed |
| 10. In the field | 31 | A field kit, brief checker to pilot gate | Ship inside a customer's business |
| Case study | — | One release of the support agent, incident and rollback included | How the pieces fit |
| Capstones | — | Seven end-to-end projects, the last a customer engagement | Prove it on your own build |

Each part ends with a **checkpoint** listing what you should now be able to do. If two items feel shaky, redo the exercises it points to. For a finer check, `CHAPTER_OUTCOMES.md` in the course kit lists every chapter's outcomes, each tied to an exercise or a section.

## Reading paths

You don't have to read the whole book before you build something real. Follow your row in order.

Table: Learning paths by role
| Path | For | Read, in this order | Finish with |
| --- | --- | --- | --- |
| **Beginner** | You're new to programming, or new to agents | Chapter 0 and the interludes you need → first agent (Chapters 1–4) → state, real tools and approvals (Chapters 5–9) → measuring an agent (the measurement interlude, sections 27.1–27.3) → your first MCP server (Chapter 12). Simple exercises first | Capstone 1 |
| **Agent engineer** | You write Python and want to build capable agents | Chapters 1–4 quickly → state, tools and approvals (Chapters 5–9) and the measurement interlude → feedback loops and teams (Chapters 10–11) → MCP (Chapters 12–15) → context, memory and knowledge (Chapters 16–18) → long-running work, planning, orchestration and control (Chapters 19–22) → security (Chapter 25) → evaluation (Chapter 27). Simple and Medium exercises | Capstone 2 or 5 |
| **Production engineer** | You already run services and must ship agents safely | Chapters 1–4 quickly → a real API (Chapter 7) and the measurement interlude → approvals (Chapter 9) → the MCP policy layer (Chapter 14) → deterministic control (Chapter 22) → security and identity (Chapters 25 and 26) → evaluation (Chapter 27) → AgentOps (Chapter 28) → performance and cost (Chapter 29) → deployment and the platform (Chapter 30) | The case study, then Capstone 3 |
| **Architect** | You design agent platforms and set standards | Chapter 1's frameworks → approvals (Chapter 9) → teams and orchestration (Chapters 11 and 21) → MCP in 2026 and discovery (Chapter 15) → memory (Chapter 17) → long-running work and planning (Chapters 19 and 20) → deterministic control (Chapter 22) → skills (sections 24.7 and 24.10) → security and identity (Chapters 25 and 26) → evaluation (Chapter 27) → economics (section 29.9) → the platform (Chapter 30) → the case study | Appendix I's cards and Appendix K's decision records, then Capstone 6 |
| **Forward-deployed** | You build agents with and for customers, or are interviewing for these roles | Chapters 1–4 quickly → a real API (Chapter 7) and the measurement interlude → approvals (Chapter 9) → context (Chapter 16) → retrieval (Chapter 18) → deterministic control (Chapter 22) → security and identity (sections 25.1–25.5, Chapter 26) → evaluation (Chapter 27) → cost and payback (sections 29.1 and 29.9) → deployment and lifecycle (sections 30.1–30.7 and 30.13) → customer production (Chapter 31) | Capstone 7, then `FIELD_GUIDE.md` and `INTERVIEW_PREP.md` in the course kit |

In a hurry? Chapters 0–4, 9, 12 and 16, then sections 27.1–27.3 and 30.1–30.3, give you one working, safe agent behind an API (section 30.2).

If a chapter's Prerequisites line names something new to you, read that first.

## The roadmap at a glance

The paths above are routes; this table is the map. Read across a row to see how much each chapter matters for each role: **E** is essential (it's on that role's path, so read it in order), **O** is optional (read it when you need it) and **A** is advanced (come back after your first capstone). No role needs all of it.

Table: Essential, optional and advanced chapters by role {#t:roadmap}
| Chapters | Beginner | Agent engineer | Production engineer | Architect | Forward-deployed |
| --- | --- | --- | --- | --- | --- |
| 0 and the Python interlude (beginner path) | E | O | O | O | O |
| 1–4: the first agent, testing interlude | E | E | E | E (1) | E |
| 5–6: state, search, regex interlude | E | E | O | O | O |
| 7–8: real APIs, SQL; SQL interlude | E | E | E (7) | O | E (7) |
| Measurement interlude | E | E | E | O | E |
| 9: approvals | E | E | E | E | E |
| 10–11: feedback loops, first teams | O | E | O | E (11) | O |
| 12: your first MCP server | E | E | O | O | O |
| 13–15: MCP clients, ecosystem, MCP in 2026 | A | E | E (14) | E (15) | O |
| 16–18: context, memory, retrieval | A | E | O | E (17) | E (16, 18) |
| 19–20: long-running work, planning, routing | A | E | O | E | O |
| 21: multi-agent orchestration | A | E | O | E | A |
| 22: deterministic control | O | E | E | E | E |
| 23–24: computer use, frameworks, skills | A | O | A | E (24.7, 24.10) | A |
| 25–26: security, identity | O | E (25) | E | E | E (25.1–25.5, 26) |
| 27: evaluation and release gates | E (27.1–27.3) | E | E | E | E |
| 28: AgentOps | A | O | E | O | O |
| 29: performance and cost | A | O | E | E (29.9) | E (29.1, 29.9) |
| 30: deployment and the platform | A | O | E | E | E (30.1–30.7, 30.13) |
| 31: customer production | A | O | O | O | E |
| The case study | O | O | E | E | O |
| Your capstone | 1 | 2 or 5 | 3 | 6 | 7 |

## From first agent to production

Each milestone ends with something that runs and a command that proves it:

Table: Five milestones from a first agent to production
| Milestone | Chapters | You'll have | Check it with |
| --- | --- | --- | --- |
| 1. A first agent | 0–4 | A model, tools and the loop, with stop conditions | `./course.sh python ch04_agent.py` |
| 2. A useful, safe agent | 5–9 | State, files, a real API, a database and approval gates | `./course.sh ex 9.3` |
| 3. Tools anyone can use | 12–14 | Your tools as MCP servers, your own MCP host, a policy layer | `./course.sh python ch13_mcp_agent.py servers.json` |
| 4. Measured | The measurement interlude, 27 | An evaluation suite with repeated trials and a release gate | `./course.sh python ch27_eval.py eval_sql.jsonl 3` |
| 5. Deployed | 28–30 | Traces and SLOs, a cost and capacity model, a service | `./course.sh serve-api` |

Parts 6, 7 and 8 deepen each milestone.

## Setup (do this once)

Everything runs inside one Docker image with Python, Node.js, the MCP SDK, reference MCP servers, sample data and the chapter code. The only thing you install is **Docker** (Docker Desktop on Windows and macOS, Docker Engine with Compose on Linux). Then get the course kit with `git clone https://github.com/sbittla/building-agentic-ai.git` (or download the ZIP), open a terminal in its folder and run:

```bash
./course.sh setup          # checks Docker, creates .env, asks Claude or local model (and the key)
./course.sh build          # builds the image (a few minutes, once)
./course.sh selftest       # offline check of the whole setup, no API key needed
./course.sh check --api    # confirms the model answers, with one tiny call
```

On Windows, use `.\course.cmd` wherever this book shows `./course.sh`. With the free local model, run `./course.sh local up` before `check --api`; the first run downloads about 6.6 GB. Setup also creates a **workspace** folder with the chapter code and sample data. Edit there with any editor; the container sees changes immediately. If a command fails, see Appendix A.

## Your first agent, free

Before you choose a model, see an agent work. Once the image is built, run:

```bash
./course.sh quickstart
```

It runs the real agent loop from Chapter 4 with the real date tools from Chapter 3. Only the model is a scripted stand-in, so you need no key. You should see something like this, with today's date:

```
Question: How many days until July 4 next, and what weekday will it be?

[step 1] get_current_date({}) -> '2026-10-05 (Monday)'  (0 ms)
[step 2] days_between({"start": "2026-10-05", "end": "2027-07-04"}) -> '272 days; 2027-07-04 is a Sunday'  (0 ms)

ANSWER: It's 272 days until July 4; 2027-07-04 is a Sunday.
```

The model asked for a tool, your code ran it, the result went back, and the loop repeated until the model answered. That loop is the whole idea of an agent, and Chapter 4 builds it. To watch a real model make the same choices, pick one (next section) and run `./course.sh python ch04_agent.py`.

## Choose your model: Claude or free and local

You can use either of two models and switch with one line in `.env`.

Table: Claude or the free local model
| | Claude (the default) | Free local model |
| --- | --- | --- |
| Model | `claude-sonnet-5` through the Claude API | `qwen3.5:9b`, open source, in Docker on your computer |
| Cost | Pay per use: about {{cost:learner}} for the whole book | Free |
| Needs | An API key (section 0.5) | 16 GB of RAM (32 GB recommended), 10 GB of disk; GPU optional |
| Speed | Seconds per answer | Seconds with a GPU; a minute or more on a CPU |
| Quality | Rarely picks the wrong tool | Good for learning; more mistakes from Chapter 8 on |
| Runs | Every exercise | All except the {{exercises:claude-only}} marked **Claude only** |
| Turn on | `PROVIDER=claude` in `.env` (or no `PROVIDER` line) | `./course.sh local up`, then `PROVIDER=local` in `.env` |

**Why your results may differ from the book's.** Answers vary between runs, and more between models, so each *Done when* line checks behavior (the right tool, a refused action, a correct number) rather than exact text. To change the Claude model, set `MODEL=...` in `.env`; current names are at platform.claude.com/docs/en/models/overview.

On a tight budget, do the book on the local model and add a few dollars of Claude credit for the {{exercises-word:claude-only}} **Claude only** exercises and the {{exercises-word:claude-rec}} marked **Claude recommended**. Appendix H is the local-model guide.

## How each chapter is organized

Every chapter opens with what you'll build, where it sits in the architecture (section 1.7), its **Prerequisites** and **Learning objectives**, and a production system using the same pattern (**In the real world**). Numbered **lessons** follow with runnable code; a listing marked *excerpt* shows the parts that teach. **Common mistakes**, **Key takeaways** and **Learn more** close the chapter.

**Exercises** come at four levels: **Concept** (no code), **Simple** (a small change to the chapter's code), **Medium** (a new feature with a design decision) and **Complex** (an open-ended build with measurements). Each has a measurable **Done when** line. Run one with `./course.sh ex <id>` (a build exercise's first run creates a starter file in `workspace/exercises`), check it with `./course.sh check <id>` where a checker exists, and print the reference solution with `./course.sh solution <id>`. `./course.sh list 4` lists Chapter 4's exercises. Each box also names the model it needs:

Table: Exercises by the model they need
| Label | Meaning | Exercises |
| --- | --- | --- |
| **No model** | Plain Python, SQL, tests or design; free | {{exercises:none}} |
| **qwen3.5:9b or Claude** | Runs on the free local model or on Claude | {{exercises:any}} |
| **Claude recommended** | Runs on `qwen3.5:9b`, but much better on Claude | {{exercises:claude-rec}} |
| **Claude only** | Needs Anthropic's servers or Claude Desktop | {{exercises:claude-only}} |

## What this book covers, and what it doesn't

Everything besides agents, the book teaches only as far as agents need it.

Table: Topics the book teaches only as far as agents need them
| Topic | What this book gives you | Where to learn the rest |
| --- | --- | --- |
| Python | The fundamentals the chapters use | The official Python tutorial, Python for Everybody, CS50 Python |
| Terminal, JSON, HTTP, Docker | Enough to run the kit and call web APIs | Chapter 0's Learn more list |
| Testing, regex, SQL, measurement, async | One interlude each | Each interlude's Learn more list |
| Machine learning | Not covered: you use models, you don't train them | fast.ai's free Practical Deep Learning course (course.fast.ai) |
| Web front ends, cloud operations | Enough to put an agent behind an API (Chapter 30) | Chapter 30's Learn more list |
| Agent frameworks | The ideas behind them, plus a short tour (Chapter 24) | Each framework's documentation |

If something feels too fast, spend an hour with the linked resource. That's normal.

## Code conventions

All code lives in one flat folder, your workspace, and every file starts with its chapter number: `ch04_agent.py`, `ch07_weather_tools.py`. Later chapters import earlier files the way a real project grows; `from ch04_agent import run_agent` appears in almost every chapter after Chapter 4.

The examples use the Anthropic Python SDK because it keeps the tool-calling messages visible. Any LLM (large language model) provider with tool calling works the same way; switching SDKs is mostly renaming fields, as section 24.6 shows.

## Solutions

The read-only `solutions` folder holds a worked solution for every exercise and capstone, listed in `solutions/SOLUTIONS.md`. `./course.sh capstone <n>` runs a reference capstone, and `./course.sh check-solutions` runs them all offline, with no API key. Appendix F maps the kit. Try each exercise before you look; getting unstuck is where most of the learning happens.

## Cost and safety

An agent makes many model calls per question, and with Claude each one costs money. On Claude Sonnet 5, the whole book costs about **{{cost:learner}}**, counting reruns ({{cost:first}} for one clean pass); Appendix E breaks this down. The local model (Appendix H) costs nothing but time. To keep costs down:

- Set a monthly spending limit in the Claude Console before you start.
- Develop on a cheaper model (`MODEL=claude-haiku-4-5` in `.env`) and evaluate on a larger one.
- Always keep the `max_iterations` cap from Chapter 4.
- Don't give an agent write access to anything you care about until Chapter 9's approval gates.

## Learn more

Start with these. `RESOURCES.md` in the kit has all 5 links, ready to click.

| Resource | What you'll find |
| --- | --- |
| **Anthropic Academy (free courses)**<br>[anthropic.skilljar.com](https://anthropic.skilljar.com) | Free video courses on the Claude API, MCP and Claude Code, with certificates |
| **Claude Developer Platform docs**<br>[platform.claude.com/docs/en/home](https://platform.claude.com/docs/en/home) | The official reference for everything the book calls through the API |
| **Anthropic courses on GitHub**<br>[github.com/anthropics/courses](https://github.com/anthropics/courses) | Free notebooks: API fundamentals, prompt engineering, tool use |

With the kit installed and a model answering, you're ready. If the terminal, JSON or web APIs feel shaky, Chapter 0 is next. If not, turn to Chapter 1, which starts with the question every agent project should ask first: do you need an agent at all?
