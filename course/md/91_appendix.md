# Appendices

The appendices are reference material for when you need a fact quickly. They cover how to run the course kit, fixes for common errors, a glossary, sources, costs, the solutions folder, where to learn more, the free local model, one-page reference cards and the same concepts on other platforms. You don't need to read them in order: keep them open while you work through the chapters and capstones.

## Appendix A: Running the Course Kit with Docker

Every exercise runs in the course kit's Docker image. You type commands on your own computer; Docker runs them in the container, against the files in your `workspace` folder. On Windows, use `.\course.cmd` wherever this book shows `./course.sh`.

### What's in the kit

| File or folder | Purpose |
| --- | --- |
| `Dockerfile` | Builds the image: Ubuntu 24.04, Python 3.12, Node.js 24, the MCP SDK, MCP Inspector, the reference servers, GitHub's server, and for the later parts the Claude Agent SDK, LangChain, FastAPI and a small embedding model |
| `compose.yaml` | Defines the `course` service, the network-less `sandbox` service and, for the free local model, `local-model` (Ollama) and `local-adapter` |
| `compose.gpu.yaml` | Adds an NVIDIA GPU to the local model (`./course.sh local up --gpu`) |
| `course.sh`, `course.ps1`, `course.cmd` | The launchers for macOS/Linux and Windows |
| `.env.example` | Template for your `.env` (API key or `PROVIDER=local`, model, GitHub token) |
| `workspace/` | Created on first run: your copy of all the kit's code and sample data. Everything you write lives here |
| `solutions/` | Worked solutions for every exercise, sample answers for concept exercises, and the reference capstones |

### Commands

| Command | What it does |
| --- | --- |
| `./course.sh setup` | First-time setup: checks Docker, creates `.env`, asks which model you want (and your API key for Claude), generates the Chapter 30 secrets |
| `./course.sh build` | Build (or rebuild) the image |
| `./course.sh selftest` | Offline check of the whole setup, with no API key and no cost |
| `./course.sh check --api` | Show installed tools and make one tiny model call |
| `./course.sh check <id>` | Check your answer to an exercise (Chapter 0, the interludes and 3.3) |
| `./course.sh list [chapter]` | List exercises (`list 4`; interludes are `list P`, `T`, `R`, `S` and `A`) |
| `./course.sh ex <id> [--info]` | Show an exercise and run it |
| `./course.sh ask <module> ["question"]` | Chat with a chapter's tools, e.g. `ask ch08_sql_tools` |
| `./course.sh python <file.py>` | Run any file in your workspace |
| `./course.sh pytest <path>` | Run tests |
| `./course.sh shell` | Open a terminal inside the container |
| `./course.sh data <kind>` | Regenerate sample data: `notes`, `library`, `messy`, `repo` or `db` (options `--count`, `--out`, `--fresh`) |
| `./course.sh reset <file>` | Restore an original kit file |
| `./course.sh solution <id>` | Show the solution for an exercise |
| `./course.sh check-solutions` | Run every solution and capstone offline, with no API key |
| `./course.sh live-check [part]` | Run every chapter's main file against the model and write `live_report.md` (about $1 on Claude; free but slow on the local model) |
| `./course.sh live-check exercises [chapter]` | Run every exercise that uses a model, with its reference solution, and write `live_exercises_report.md` |
| `./course.sh local up [--gpu\|--native]` | Start the free local model and download `qwen3.5:9b` the first time (Appendix H) |
| `./course.sh local status` | Is the local model running, and is `qwen3.5:9b` downloaded? |
| `./course.sh local down` | Stop the local model and free its memory |
| `./course.sh capstone <1-6> [args]` | Run a reference capstone (creates its sample data; needs your API key or the local model) |
| `./course.sh inspector <server.py>` | MCP Inspector web UI at http://localhost:6274 |
| `./course.sh serve <server.py>` | MCP server over HTTP at http://localhost:8000/mcp |
| `./course.sh desktop-config` | Print the Claude Desktop config for your server |
| `./course.sh mcp python <server.py>` | Run a stdio MCP server for any MCP host |
| `./course.sh serve-api` | The Chapter 30 agent API at http://localhost:8080 (docs at `/docs`) |
| `./course.sh serve-mcp` | The Chapter 30 token-protected MCP server at http://localhost:8000/mcp |
| `./course.sh serve-a2a` | The Chapter 21 A2A analyst agent; its card is at http://localhost:9999/.well-known/agent-card.json |
| `./course.sh sandbox up` / `down` / `logs` | Start, stop or watch the network-less test sandbox |

### How the ex command runs each kind of exercise

| Exercise kind | First run | Later runs |
| --- | --- | --- |
| Concept | Creates `answers/exN_M.md` with the question | Reminds you where your answer file is |
| Run a chapter file | Runs it, e.g. `python ch04_agent.py` | Same, with your edits |
| Chat with tools | Starts a chat with that chapter's tools | Same |
| Build | Creates a starter `exercises/exN_M_*.py` | Runs your solution |
| Tests | Creates a starter `tests/test_exN_M_*.py` | Runs it with pytest |
| MCP Inspector | Opens the Inspector for the server | Same |

### Networking and safety

- The `course` container can reach the internet: the model API, Open-Meteo and web pages for the Fetch server.
- The `sandbox` container has **no network**, a read-only file system except the workspace, and no API keys. Chapter 10 runs model-written code there.
- Published ports (6274–6275 for the Inspector, 8000 for MCP servers over HTTP, 8080 for the agent API) are bound to 127.0.0.1, so only your own computer can reach them.
- `serve-api`, `serve-mcp` and `serve-a2a` run in containers named `agentic-ai-api`, `agentic-ai-mcp` and `agentic-ai-a2a`. Other kit containers reach them by those names; `ch30_client.py` finds the first two automatically, and `ch21_a2a_client.py --url http://agentic-ai-a2a:9999` reaches the third.
- Your `.env` file is read by Docker Compose and never copied into the image.

## Appendix B: Troubleshooting

The first table covers setup and error messages. After it, a debugging playbook covers the harder case: the agent runs, but does the wrong thing.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `AuthenticationError` or 401 | API key not set in this shell | Export `ANTHROPIC_API_KEY` again, or load `.env` |
| `NotFoundError` for the model | Model name retired or misspelled | Set `MODEL` to a current name from the models overview page |
| 400 error mentioning `tool_use` ids | A `tool_use` block has no matching `tool_result` | Return a result for every `tool_use` block, in one user message (section 4.3) |
| `AttributeError: ... has no attribute 'text'` on `content[0]` | Current models start the reply with a thinking block | Select blocks by `type` (section 1.1) |
| `stop_reason` is `max_tokens` and there's no answer | Thinking used up a small `max_tokens` | Raise `max_tokens` (2,000 or more); you pay only for what's used (section 4.8) |
| 400 error about `temperature`, prefill or `budget_tokens` | Settings current models no longer accept | Remove them; use instructions, structured outputs and `effort` (sections 3.3 and 4.8) |
| 400 error about `tool_choice` on the newest models | Forced tools aren't allowed on Opus 5.5 and the 5.1 models | Use structured outputs, or a strict tool with `tool_choice` `auto` (section 3.3) |
| Agent loops until `max_iterations` | Tool keeps failing, or the description is misleading | Read the trace; improve the error message or description |
| Answer ignores the tool result | Tool output too long or unclear | Shorten and structure the output; put the key fact first |
| 429 rate-limit errors | Too many requests at once | Retry with backoff; lower concurrency (section 29.7) |
| "Docker is not running" | Docker Desktop or the Docker service is stopped | Start it and wait until it reports it's running |
| Image build fails on `ghcr.io/github/github-mcp-server` | Your network blocks ghcr.io | Add `GITHUB_MCP_IMAGE=nogithub` to `.env` and build again (only 14.3, 14.4 and Capstone 4 need GitHub) |
| Port 6274 or 8000 is already in use | Another program, or an Inspector you didn't stop | Stop it (Ctrl+C in its terminal), or change the left-hand port in `compose.yaml` |
| Exercise 10.7 says the sandbox isn't running | The sandbox service is stopped | `./course.sh sandbox up` |
| A kit file is broken beyond repair | Edits went wrong | `./course.sh reset <file>`; your version is kept as `.bak` |
| MCP server "disconnected" right away | A crash at start-up, or (outside Python's SDK) output written to stdout | Run the server by itself to see the error; log to stderr |
| Claude Desktop doesn't show your tools | Wrong path in the config, or the app wasn't restarted | Use absolute paths; fully quit and restart the app |
| `ModuleNotFoundError` inside a server | The host started the server with a different Python | Start servers with `uv --directory <project> run python ...` |
| Validation warnings from older MCP servers | Newer clients probe features older servers don't support | Usually harmless if tools still list and run; update the server if not |
| `Couldn't reach the agent API` (Chapter 30) | `serve-api` isn't running, or was started without the wrapper | Start `./course.sh serve-api` in another terminal and leave it running |
| Chapter 18 says the local model is unavailable | The build couldn't download it from Hugging Face | Use `EMBEDDER=hashing`, or set `VOYAGE_API_KEY`; rebuild later to retry the download |
| `CanUseToolShadowedWarning` (Chapter 24) | A tool in `allowed_tools` skips your approval callback | Expected for harmless tools; move risky tools out of `allowed_tools` |

### When your agent doesn't work: a debugging playbook

Most agent bugs aren't crashes: the agent runs, then does the wrong thing. Work through these steps in order. Each one is quick, and most problems are found by the third.

1. **Read the trace, not the answer.** Print every model call, tool call and tool result (Chapter 4's `verbose=True`, or the OpenTelemetry spans from Chapter 28). The final answer hides *where* things went wrong; the trace shows it.
2. **Check the stop reason.** `max_tokens` means the reply was cut off: raise `max_tokens`. `refusal` means the model declined. A loop that hits `max_iterations` means a tool keeps failing or the model can't see how to finish (Chapter 4's `next_action` names each case).
3. **Run the tool by itself.** Call the function directly with the exact arguments from the trace. If it fails or returns something confusing on its own, the model isn't the problem.
4. **Read the tool result the way the model does.** Is it too long, is the key fact buried, is an error phrased so the model can fix its call? Shorten, structure and put the answer first (Chapters 2, 3 and 6).
5. **Check the description.** Would a new colleague know *when* to call this tool from its description alone? Most wrong-tool and no-tool bugs are description bugs (section 3.2).
6. **Shrink the context.** A long conversation or a large system prompt can bury what matters. Try the question in a fresh conversation; if it works, you have a context problem (Chapter 16).
7. **Turn the bug into a test case.** Add the failing question to your evaluation suite with the answer you expect (Chapter 27), fix it, and run the whole suite. Run it several times: a fix that works once may not work reliably.

| Symptom | First place to look |
| --- | --- |
| Answers without calling a tool it should use | The tool description (section 3.2); a "no tool" eval case (section 3.4) |
| Calls the wrong tool | Overlapping descriptions; merge or rename tools (Chapter 3) |
| Invents a value it should ask for | Ambiguity handling (section 7.4), or elicitation for MCP servers (exercise 13.7) |
| Repeats the same failing tool call | The tool's error message: does it say how to fix the call? (section 2.6) |
| Works in testing, fails for real users | Run the evaluation suite with several trials; check the model name and limits in production (Chapter 27) |
| Gets slower and more expensive over a session | Context growth: trimming, compaction and caching (Chapter 16) |
| Follows instructions hidden in a web page or file | Prompt injection: the policy layer (Chapter 14), and guards and quarantined reading (Chapter 25) |
| Works locally, fails once deployed | The smoke test, secrets and instance limits (section 30.6) |

## Appendix C: Glossary

| Term | Meaning |
| --- | --- |
| A2A (Agent2Agent) | An open protocol for independent agents to find each other (through agent cards) and hand off tasks; complements MCP (section 21.7) |
| Adaptive thinking | The model decides how much to reason before each answer or tool call; on by default on current Claude models |
| Agent | An LLM that chooses and calls tools in a loop until a task is done |
| Agent architecture reference model | The layers of every agent system: user/API, runtime, planning, memory, context, tools, policies, model, MCP/APIs/A2A, environment, with evaluation and observability across (section 1.7) |
| Agent card | An A2A agent's public JSON description of its skills, endpoint and security, at `/.well-known/agent-card.json` |
| Agent SDK | The Claude Agent SDK: the agent runtime behind Claude Code, as a library |
| Agent Skill | A folder with a `SKILL.md` (name, description, instructions) and optional files, loaded only when a task needs it; an open format |
| Agentic search | Finding information by letting the model list, search and read |
| Approval gate | Code that asks a human before a risky tool runs |
| Audit log | An append-only record of every action an agent took |
| Blackboard (shared board) | A shared record of a team's tasks and results that agents read and only the orchestrator writes (section 21.3) |
| BM25 | A classic keyword-ranking formula that weights rare words more |
| Cache hint (MCP) | `ttlMs` and `cacheScope` on a list result: how long a client may reuse it, and whether it may be shared across users (section 15.3) |
| Cascade | Trying a cheaper model first and escalating to a stronger one only when a check fails (section 20.8) |
| Checkpoint | Saving a step's status and result before the next step starts, so a crashed job can resume (section 19.3) |
| Compaction | Replacing older conversation turns with a summary to save context |
| Compensation | Undoing completed steps, newest first, when a long job is abandoned; the saga pattern (section 19.7) |
| Computer-use agent | An agent that operates a user interface, a web page or a desktop, instead of calling an API (Chapter 23) |
| Content block | One part of a model message: text, `tool_use` or `tool_result` |
| Context engineering | Choosing what goes into the model's context on each call, and what stays out (section 1.7, Chapter 16) |
| Context window | The maximum tokens a model can consider in one call |
| Contract (between agents) | A schema for what one agent hands another, checked in code (section 21.2) |
| Coordinated omission | Measuring latency only after a request gets service, which hides queueing time |
| Deterministic shell | A workflow whose states and transitions are code, with model calls only at chosen steps (section 22.2) |
| Dimensions of agency | Autonomy, state, planning, tool use, environmental interaction, persistence, feedback, delegation and adaptation: what makes a system more or less agentic (section 1.4) |
| Durable execution | Running a job so that its progress survives crashes and restarts (Chapter 19) |
| Effort | A request setting (`low` to `max`) that trades quality for cost and speed |
| Elicitation | An MCP feature that lets a server ask the user for missing input mid-call |
| Embedding | A vector of numbers representing a text's meaning; similar texts get similar vectors |
| Error budget | How much failure an SLO allows over a window; spending it fast triggers alerts (section 28.10) |
| Evaluation (eval) suite | A set of test cases with checks, run after every change |
| Exfiltration | Getting private data out of a system, for example inside a URL the agent fetches |
| Extension (MCP) | An optional, named protocol feature, such as Tasks or MCP Apps, used only when client and server both declare it (section 15.8) |
| Failure taxonomy | The 12 classes of agent failure, each with detection, mitigation and evaluation (section 28.8) |
| Gateway (MCP) | A server in front of other MCP servers that allow-lists tools, checks tokens, rate-limits and audits every call (section 15.5) |
| Goodput | Successful tasks per second; unlike throughput, it doesn't count tasks that failed or gave up (section 29.5) |
| Harness | The code around the model: the loop, the tools, the checks and the limits; it decides what's allowed (section 1.7) |
| Host | The application that runs the model and connects to MCP servers |
| Idempotency key | A stable key sent with a side effect so the receiving system ignores repeats (section 19.5) |
| Idempotent | Safe to repeat: calling twice has the same effect as once |
| JSON Schema | A standard way to describe the shape of JSON data, used for tool inputs |
| Knee (of a load curve) | The load at which throughput stops rising and latency starts climbing, usually where a resource saturates (section 29.5) |
| Lease | A time-limited claim a worker holds on a job; if it expires, another worker may take the job (section 19.6) |
| Lethal trifecta | Private data + untrusted content + a way to send data out: together, an agent can be made to leak |
| LLM (large language model) | A model trained on huge amounts of text to predict the next token; the "model" in every agent in this book |
| Managed agent | An agent whose loop and sandbox run on the provider's servers (Claude Managed Agents) |
| MCP | Model Context Protocol: an open standard connecting AI applications to tools and data |
| MCP Apps | An MCP extension that lets a tool show an interactive user interface inside the chat |
| MCP client | A connection inside a host to one MCP server |
| MCP server | A program that offers tools, resources and prompts over MCP |
| Model routing | Choosing which model handles each task or step, by rules, a classifier or a cascade (section 20.7) |
| Multi round-trip request | Since MCP 2026-07-28: a tool returns "input required" and the client calls again with the answers |
| Orchestrator–worker | A lead agent that delegates subtasks to parallel subagents |
| Output guard | A check in code on what a model wrote, with a safe fallback when it fails (section 22.6) |
| OWASP Agentic Top 10 | OWASP's list of the ten most critical security risks of agentic applications (ASI01 to ASI10) |
| p50 / p95 | The latency that 50% / 95% of requests beat |
| Pass^k | The share of eval cases that pass on every one of k repeated runs |
| Plan (as data) | A list of steps with tools, dependencies and done conditions that code can check before running (section 20.2) |
| Programmatic tool calling | The model writes a program that calls your tools in a sandbox, so bulky results stay out of the context |
| Progressive discovery | Offering tools through search instead of listing them all at once (section 15.5) |
| Prompt (MCP) | A reusable prompt template a server exposes |
| Prompt caching | Reusing the processed form of an unchanged prompt prefix, at a tenth of the input price |
| Prompt injection | Text in data (web pages, files, issues) that tries to give the model instructions |
| RAG | Retrieval-augmented generation: fetch similar document chunks, then call the model |
| Rate limit | A cap on how many requests a caller may make in a period (HTTP 429 when exceeded) |
| Recall@k / MRR | Retrieval metrics: is the right document in the top k, and how high does it rank |
| Reciprocal rank fusion | Merging several rankings by adding 1/(60 + rank) for each result |
| Resource (MCP) | Read-only data a server exposes by URI |
| Scorecard (agent) | One table of quality, safety, cost and latency metrics for a release, compared with the last (section 27.6) |
| Server tool | A tool that runs on the provider's servers (web search, code execution, tool search), not in your code |
| SLO (service-level objective) | A target for a measured behavior, such as task success ≥ 95% over 30 days (section 28.10) |
| SSE (Server-Sent Events) | A simple way for a server to stream events to a client over one HTTP response |
| SSRF | Server-side request forgery: tricking a server or agent into fetching an internal address |
| Stateless protocol | Each request carries everything the server needs, so any copy of the server can answer it; MCP since 2026-07-28 (section 15.2) |
| stdio / Streamable HTTP | The two standard MCP transports: local subprocess or web service |
| Stop reason | Why the model stopped: `end_turn`, `tool_use`, `max_tokens` and others |
| Structured outputs | An API feature that makes the model's reply match a JSON Schema |
| System prompt | Instructions that set the model's behavior for a whole conversation |
| Tasks (MCP) | An MCP extension for long-running calls: the server returns a task id that the client polls with `tasks/get` (section 15.4) |
| Thinking block | A content block holding the model's reasoning, returned before its answer; send it back unchanged |
| Token | A chunk of text the model reads or writes; the unit of cost |
| Token bucket | A rate-limit method: each caller's bucket refills at a steady rate and each request takes one token |
| Tool | A function the model can ask your code to run, described by name, description and schema |
| Tool search | Deferring most tool definitions and letting the model search for the ones it needs |
| Trace | The step-by-step record of one agent run |
| Workflow | A fixed sequence of LLM calls and code, with steps decided by the developer |

## Appendix D: References

- Anthropic, "Building effective agents": anthropic.com/engineering/building-effective-agents
- Anthropic, "How we built our multi-agent research system": anthropic.com/engineering/multi-agent-research-system
- Claude models overview: platform.claude.com/docs/en/models/overview
- Model Context Protocol documentation: modelcontextprotocol.io
- MCP quickstart, "Build an MCP server": modelcontextprotocol.io/docs/develop/build-server
- MCP quickstart, "Build an MCP client": modelcontextprotocol.io/docs/develop/build-client
- MCP reference servers: github.com/modelcontextprotocol/servers
- MCP Registry: registry.modelcontextprotocol.io
- MCP Blog, "MCP joins the Agentic AI Foundation" (December 9, 2025): blog.modelcontextprotocol.io
- GitHub MCP server: github.com/github/github-mcp-server
- GitHub Docs, "About GitHub Copilot cloud agent": docs.github.com
- Uber Engineering, "QueryGPT – Natural Language to SQL Using Generative AI": uber.com/blog/query-gpt
- Intercom Help, "Fin AI Agent outcomes": intercom.com/help
- CX Dive, "Klarna changes its AI tune and again recruits humans for customer service" (May 2025): customerexperiencedive.com
- Open-Meteo API documentation: open-meteo.com/en/docs
- Anthropic, "Effective context engineering for AI agents": anthropic.com/engineering
- Prompt caching documentation: platform.claude.com/docs (search "prompt caching")
- Claude Agent SDK for Python: github.com/anthropics/claude-agent-sdk-python
- LangChain documentation: docs.langchain.com
- model2vec: github.com/MinishLab/model2vec
- Voyage AI documentation: docs.voyageai.com
- FastAPI documentation: fastapi.tiangolo.com
- MCP specification, including authorization: modelcontextprotocol.io/specification
- Simon Willison, "The lethal trifecta for AI agents" (June 2025): simonwillison.net
- Anthropic, "Introducing Contextual Retrieval" (September 2024): anthropic.com/news
- OpenTelemetry semantic conventions for generative AI: opentelemetry.io (search "GenAI semantic conventions")
- Agent2Agent (A2A) protocol: a2a-protocol.org
- Python tutorial (for the Python interlude): docs.python.org/3/tutorial

## Appendix E: What the Exercises Cost

Costs depend on the model, how often you rerun exercises, and how long your conversations get. These estimates assume Claude Sonnet 5 at $2 per million input tokens and $10 per million output tokens (2026 prices), a typical exercise run of 3–6 model calls, and a few reruns while debugging. Check current prices on the provider's pricing page.

| Part | Estimated cost | Biggest items |
| --- | --- | --- |
| 0. Foundations | Under $0.10 | Exercise 0.6 and `check --api` only |
| 1. Your first agent | $2–4 | Routing evals (3.4, 3.6), tool search (3.7), cost profile (4.5) |
| 2. State and environment | $3–6 | The 2,000-note scale test (6.6) |
| 3. Real-world tools | $2–5 | SQL evaluation harness (8.7) |
| 4. Autonomy | $6–12 | Fixer benchmark (10.7), multi-agent comparison (11.6), the four patterns (11.7) |
| 5. MCP and interoperability | $2–5 | Coordinator with an analyst agent (13.8) |
| 6. Context, memory and knowledge | $3–8 | Caching savings (16.5), retrieval evaluation (18.6), verified answers (18.9) |
| 7. Advanced agent architectures | $6–15 | Router evaluation (20.5), mixed team (21.6), browser queues (23.5, 23.6), framework comparison (24.5), managed agents (24.7) |
| 8. Trust | $1–4 | Red-team drill (25.6) |
| 9. Production engineering | $8–20 | Load testing a real agent (29.2), API load drill (30.6) |
| **All chapters** | **About $35–75** | |
| Each capstone | $3–10 | Evaluation runs and load tests |
| Cloud deployment (30.7) | Usually $0 on a free tier | The host's own charges; set a budget alert and delete the service afterward |

Claude Sonnet 5 uses a new tokenizer that counts about 30% more tokens for the same text than earlier models, and thinking is billed as output, so compare costs by measuring your own runs rather than by reusing older token counts. With Claude Haiku 4.5 ($1 input, $5 output per million tokens), the totals are roughly half. Prompt caching (Chapter 16) and smaller tool outputs cut them further. Running `./course.sh check-solutions` is always free.

**Or pay nothing:** with the free local model (`PROVIDER=local`, Appendix H), every exercise except the {{exercises-word:claude-only}} marked **Claude only** costs nothing. A sensible budget plan is to do the book locally and buy a few dollars of Claude credit for those five and the four marked **Claude recommended**.

### Estimate a run yourself

```
cost ≈ (input tokens × input price + output tokens × output price) ÷ 1,000,000
```

Every agent in this book reports its input and output tokens, so you can apply this after any run. Chapter 16's `cost()` function does it for you, including cached tokens.

## Appendix F: The Solutions Folder

The `solutions` folder sits next to `course.sh`. Inside the container it's mounted read-only at `/solutions`, so you can read and run it but never change it by accident.

| Path | What it holds |
| --- | --- |
| `exercises/ch<NN>/`, `exercises/interlude_*/` | One folder per chapter or interlude, with the programs that solve its exercises, such as `ch04/ex4_4_tracer.py` |
| `sol_chNN_*.py` (in those folders) | An improved copy of a chapter file that solves one or more exercises, such as `sol_ch08_sql_tools.py` for 8.5 and 8.6 |
| `*.json`, `*.jsonl` (in those folders) | Extra configuration and evaluation data, such as `servers_remote.json` (30.5) and `eval_sql_more.jsonl` (27.3) |
| `ANSWERS.md` | Written answers for concept exercises, and *what you should see* for exercises that run a chapter file |
| `tests/test_ex*.py` | Solutions that are themselves tests (T.2–T.4, 6.3, 9.6, 12.7, 16.6) |
| `tests/test_ch*.py`, `tests/test_capstones.py` | The automated checks behind `check-solutions`; useful as examples of testing agents with a scripted model |
| `capstones/common.py` | The shared host for all capstones: MCP hub, policy layer and approvals |
| `capstones/c1_support/` … `c6_backoffice/` | The six reference capstones (see the end of each capstone) |
| `SOLUTIONS.md` | Every exercise, chapter by chapter, with its solution file and what the solution shows |
| `index.json` | Which files solve which exercise; `./course.sh solution` reads it |

### Running a solution yourself

Solutions build on the chapter files, so run them from your workspace with the solutions on Python's path:

```bash
./course.sh shell
export PYTHONPATH=/solutions/exercises/ch04:/solutions/exercises:$PYTHONPATH
python /solutions/exercises/ch04/ex4_4_tracer.py
```

To try a solution as a starting point for your own work, copy it into `workspace/exercises` and edit the copy.

## Appendix G: Where to Learn More

Nobody learns this field from one book. This appendix lists where to get help when you're stuck, free courses that complement this one, and how to keep up as models and tools change. Each chapter's **Learn more** section lists the resources for its own topics; the last table here gathers all of them by chapter so you can find any link again.

### When you're stuck: where to ask

Before asking, search the exact error message, and include your code, the full error and what you expected. Never paste your API key or `.env` file into a question.

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic Discord**<br>[discord.com/invite/anthropic](https://discord.com/invite/anthropic) | Ask questions about Claude and the API; developers and Anthropic staff | Start here |
| **Anthropic Help Center**<br>[support.claude.com](https://support.claude.com) | Account, billing and API key questions | Start here |
| **Claude status page**<br>[status.claude.com](https://status.claude.com) | Check whether an outage is causing your errors | Start here |
| **Stack Overflow: python tag**<br>[stackoverflow.com/questions/tagged/python](https://stackoverflow.com/questions/tagged/python) | Search first: most error messages have been asked before | Start here |
| **r/learnpython**<br>[reddit.com/r/learnpython](https://www.reddit.com/r/learnpython/) | A friendly community for beginner Python questions | Start here |
| **Python Discourse: Python Help**<br>[discuss.python.org/c/help/7](https://discuss.python.org/c/help/7) | The official Python forum's help category | Go deeper |
| **MCP discussions on GitHub**<br>[github.com/modelcontextprotocol/modelcontextprotocol/discussions](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions) | Questions and proposals about MCP | Go deeper |
| **Docker Community Forums**<br>[forums.docker.com](https://forums.docker.com) | Installation and container problems | Go deeper |

### Free courses that pair well with this book

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic Academy**<br>[anthropic.skilljar.com](https://anthropic.skilljar.com) | Free courses: Claude API, MCP, Claude Code, agent skills | Start here |
| **Anthropic courses on GitHub**<br>[github.com/anthropics/courses](https://github.com/anthropics/courses) | Free notebooks: prompt engineering and tool use | Start here |
| **DeepLearning.AI short courses**<br>[deeplearning.ai/courses?types=short_course](https://www.deeplearning.ai/courses?types=short_course) | One- to two-hour free courses on agents, RAG, evals and MCP | Start here |
| **Hugging Face AI Agents Course**<br>[huggingface.co/learn/agents-course](https://huggingface.co/learn/agents-course) | Free, vendor-neutral, with a certificate | Go deeper |
| **Hugging Face MCP Course**<br>[huggingface.co/learn/mcp-course](https://huggingface.co/learn/mcp-course) | Free MCP course with hands-on units | Go deeper |
| **Claude docs: Prompt engineering overview**<br>[platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) | Writing prompts that work; useful in every chapter | Start here |

### Keeping up to date

Model names, prices and SDK features change every few months. These pages are where changes appear first.

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Claude Platform release notes**<br>[platform.claude.com/docs/en/release-notes/overview](https://platform.claude.com/docs/en/release-notes/overview) | New models, API features and deprecations, as they ship | Start here |
| **Claude docs: Models overview**<br>[platform.claude.com/docs/en/models/overview](https://platform.claude.com/docs/en/models/overview) | Current model names and prices; check before changing MODEL in .env | Start here |
| **Anthropic Engineering blog**<br>[anthropic.com/engineering](https://www.anthropic.com/engineering) | In-depth posts on agents, tools, evals and context | Go deeper |
| **MCP blog**<br>[blog.modelcontextprotocol.io](https://blog.modelcontextprotocol.io) | Protocol changes and new specification versions | Go deeper |
| **Simon Willison's weblog**<br>[simonwillison.net](https://simonwillison.net) | A well-known independent developer's daily notes on LLMs and agent security | Go deeper |
| **MCP roadmap**<br>[modelcontextprotocol.io/development/roadmap](https://modelcontextprotocol.io/development/roadmap) | The protocol's priorities and upcoming changes | Go deeper |

### Every link in this book, by chapter

| Chapter | Resources |
| --- | --- |
| How to Use This Book | [Anthropic Academy (free courses)](https://anthropic.skilljar.com)<br>[Claude Developer Platform docs](https://platform.claude.com/docs/en/home)<br>[Anthropic courses on GitHub](https://github.com/anthropics/courses)<br>[Claude Cookbooks](https://github.com/anthropics/claude-cookbooks)<br>[Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course) |
| Chapter 0: Foundations | [MDN: Command line crash course](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Command_line)<br>[Docker: Get started](https://docs.docker.com/get-started/)<br>[Docker Desktop install guide](https://docs.docker.com/desktop/)<br>[Claude docs: Get your API key](https://platform.claude.com/docs/en/get-api-key)<br>[Claude Console: API keys](https://platform.claude.com/settings/keys)<br>[JSON introduction](https://www.json.org/json-en.html)<br>[JSON Schema: Getting started](https://json-schema.org/learn/getting-started-step-by-step)<br>[MDN: An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)<br>[The Twelve-Factor App: Config](https://12factor.net/config) |
| Interlude: The Python You'll Need | [The official Python tutorial](https://docs.python.org/3/tutorial/)<br>[Python for Everybody](https://www.py4e.com)<br>[CS50's Introduction to Programming with Python](https://cs50.harvard.edu/python/)<br>[Automate the Boring Stuff with Python](https://automatetheboringstuff.com)<br>[Python Tutor](https://pythontutor.com/visualize.html)<br>[Exercism: Python track](https://exercism.org/tracks/python)<br>[Real Python: Primer on decorators](https://realpython.com/primer-on-python-decorators/)<br>[Python docs: dataclasses](https://docs.python.org/3/library/dataclasses.html)<br>[mypy: Type hints cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) |
| Chapter 1: What an Agent Is (and Isn't) | [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)<br>[Claude docs: Get started](https://platform.claude.com/docs/en/get-started)<br>[Claude docs: Messages API reference](https://platform.claude.com/docs/en/api/messages)<br>[Claude docs: Models overview](https://platform.claude.com/docs/en/models/overview)<br>[Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) |
| Interlude: Testing with pytest | [pytest: Get started](https://docs.pytest.org/en/stable/getting-started.html)<br>[Real Python: Effective testing with pytest](https://realpython.com/pytest-python-testing/)<br>[pytest: How to parametrize tests](https://docs.pytest.org/en/stable/how-to/parametrize.html)<br>[pytest: How to monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) |
| Chapter 2: Tool Calling (Function Calling) | [Claude docs: Tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)<br>[Claude docs: How to implement tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use)<br>[Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)<br>[Python docs: ast module](https://docs.python.org/3/library/ast.html)<br>[OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) |
| Chapter 3: Tool Selection, Routing and Tool Search | [Claude docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)<br>[Pydantic documentation](https://pydantic.dev/docs/validation/latest/get-started/)<br>[Claude docs: How to implement tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use)<br>[Python docs: zoneinfo](https://docs.python.org/3/library/zoneinfo.html)<br>[Claude docs: Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) |
| Chapter 4: The Agent Loop | [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)<br>[Claude docs: Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)<br>[Claude docs: Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)<br>[Claude docs: Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming)<br>[ReAct paper (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)<br>[Claude docs: Migrating to Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/migration-guide) |
| Chapter 5: State and Short-Term Memory | [Claude docs: Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)<br>[Python docs: json module](https://docs.python.org/3/library/json.html)<br>[Claude docs: Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)<br>[Claude docs: Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) |
| Interlude: Regular Expressions | [RegexOne](https://regexone.com)<br>[regex101](https://regex101.com)<br>[Python docs: Regular expression HOWTO](https://docs.python.org/3/howto/regex.html)<br>[Python docs: re module](https://docs.python.org/3/library/re.html) |
| Chapter 6: Agentic Search: Exploring an Environment | [Python docs: pathlib](https://docs.python.org/3/library/pathlib.html)<br>[Claude docs: Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)<br>[Claude Code overview](https://code.claude.com/docs/en/overview)<br>[OWASP: Path traversal](https://owasp.org/www-community/attacks/Path_Traversal) |
| Chapter 7: Real APIs | [Open-Meteo API documentation](https://open-meteo.com/en/docs)<br>[MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)<br>[HTTPX documentation](https://www.python-httpx.org)<br>[AWS: Exponential backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)<br>[MDN: Retry-After header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After)<br>[Claude docs: Rate limits](https://platform.claude.com/docs/en/api/rate-limits)<br>[Public APIs list](https://github.com/public-apis/public-apis) |
| Interlude: SQL in One Sitting | [SQLBolt](https://sqlbolt.com)<br>[W3Schools SQL tutorial](https://www.w3schools.com/sql/)<br>[SQLite: SQL as understood by SQLite](https://www.sqlite.org/lang.html)<br>[Python docs: sqlite3](https://docs.python.org/3/library/sqlite3.html) |
| Chapter 8: Self-Correction: A Text-to-SQL Agent | [Uber: QueryGPT](https://www.uber.com/us/en/blog/query-gpt/)<br>[Claude docs: Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)<br>[OWASP: SQL injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)<br>[Reflexion paper (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366) |
| Chapter 9: Human-in-the-Loop Approval | [Google PAIR: People + AI Guidebook](https://pair.withgoogle.com/guidebook/)<br>[Claude Code: permission modes](https://code.claude.com/docs/en/permission-modes)<br>[NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) |
| Chapter 10: Feedback Loops | [Python docs: subprocess](https://docs.python.org/3/library/subprocess.html)<br>[Docker: Engine security](https://docs.docker.com/engine/security/)<br>[SWE-bench](https://www.swebench.com)<br>[Claude Code: Security](https://code.claude.com/docs/en/security) |
| Interlude: Asynchronous Python | [Real Python: Async IO in Python](https://realpython.com/async-io-python/)<br>[Python docs: asyncio](https://docs.python.org/3/library/asyncio.html)<br>[Claude docs: Python SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) |
| Chapter 11: Multi-Agent Systems | [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)<br>[Cognition: Don't build multi-agents](https://cognition.com/blog/dont-build-multi-agents)<br>[Claude Code: Subagents](https://code.claude.com/docs/en/sub-agents)<br>[Agent2Agent (A2A) protocol](https://a2a-protocol.org/latest/) |
| Chapter 12: MCP Fundamentals and Your First Server | [MCP: Introduction](https://modelcontextprotocol.io/docs/getting-started/intro)<br>[MCP: Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server)<br>[Anthropic Academy: Introduction to MCP](https://anthropic.skilljar.com/introduction-to-model-context-protocol)<br>[MCP blog: The 2026-07-28 specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/)<br>[DeepLearning.AI: MCP, Build Rich-Context AI Apps with Anthropic](https://www.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic)<br>[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)<br>[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)<br>[Hugging Face MCP Course](https://huggingface.co/learn/mcp-course)<br>[MCP blog: MCP Apps](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)<br>[MCP blog: The new MCP roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/) |
| Chapter 13: Build Your Own MCP Client | [MCP: Build an MCP client](https://modelcontextprotocol.io/docs/develop/build-client)<br>[MCP: Architecture overview](https://modelcontextprotocol.io/docs/learn/architecture)<br>[MCP specification](https://modelcontextprotocol.io/specification)<br>[Claude docs: MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) |
| Chapter 14: Using Servers You Didn't Write | [MCP reference servers](https://github.com/modelcontextprotocol/servers)<br>[MCP Registry](https://registry.modelcontextprotocol.io)<br>[MCP: Security best practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)<br>[GitHub MCP server](https://github.com/github/github-mcp-server) |
| Chapter 27: Agent Evaluation: Dimensions, Trajectories and Scorecards | [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)<br>[Claude docs: Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)<br>[LangChain: State of Agent Engineering](https://www.langchain.com/state-of-agent-engineering)<br>[Hamel Husain: Your AI product needs evals](https://hamel.dev/blog/posts/evals/)<br>[Claude docs: Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)<br>[Wikipedia: Binomial proportion confidence interval](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval) |
| Chapter 16: Context Engineering | [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)<br>[Redis: The state of context engineering 2026](https://redis.io/resources/state-of-context-engineering-2026/)<br>[Claude docs: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)<br>[Claude docs: Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing)<br>[Claude docs: Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)<br>[Claude docs: Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)<br>[Claude docs: Compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) |
| Chapter 18: Agentic RAG and Knowledge Systems | [Anthropic: Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)<br>[Claude docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)<br>[Claude docs: Citations](https://platform.claude.com/docs/en/build-with-claude/citations)<br>[Wikipedia: Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25)<br>[model2vec](https://github.com/MinishLab/model2vec)<br>[MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)<br>[Singh et al.: Agentic Retrieval-Augmented Generation, a survey](https://arxiv.org/abs/2501.09136) |
| Chapter 24: Skills, Frameworks and Agent Runtimes | [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)<br>[Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python)<br>[Agent Skills specification](https://agentskills.io/specification)<br>[LangChain documentation](https://docs.langchain.com)<br>[Pydantic AI](https://pydantic.dev/docs/ai/overview/)<br>[Hugging Face smolagents](https://huggingface.co/docs/smolagents)<br>[Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)<br>[Agent2Agent (A2A) protocol](https://a2a-protocol.org/latest/) |
| Chapter 30: Deploying Agents: From One Service to an Agent Platform | [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)<br>[MDN: Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)<br>[Docker Compose documentation](https://docs.docker.com/compose/)<br>[MCP: Authorization](https://modelcontextprotocol.io/docs/tutorials/security/authorization)<br>[OAuth 2.0 Simplified](https://www.oauth.com)<br>[OWASP API Security Top 10](https://owasp.org/API-Security/) |
| Capstone Projects | [Capstone 1: Intercom Help, Fin AI Agent](https://www.intercom.com/help/en/collections/6485365-fin-ai-agent)<br>[Capstone 2: Uber, QueryGPT](https://www.uber.com/us/en/blog/query-gpt/)<br>[Capstone 3: Google SRE book, Managing incidents](https://sre.google/sre-book/managing-incidents/)<br>[Capstone 3 extension: Gil Tene, How NOT to measure latency](https://www.infoq.com/presentations/latency-response-time/)<br>[Capstone 4: SWE-bench](https://www.swebench.com)<br>[Capstone 5: Anthropic, multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)<br>[Capstone 6: Anthropic, Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)<br>[Capstone 6: Playwright for Python](https://playwright.dev/python/) |
| Chapter 17: Agent Memory Engineering | [Claude docs: Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)<br>[OWASP GenAI: Memory is a feature. It is also an attack surface](https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/)<br>[OWASP Top 10 for Agentic Applications](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/)<br>[Torra and Bras-Amorós: Memory poisoning and secure multi-agent systems](https://arxiv.org/abs/2603.20357)<br>[SQLite: FTS5 full-text search](https://www.sqlite.org/fts5.html) |
| Chapter 21: Multi-Agent Orchestration | [Microsoft: Multi-agent patterns](https://learn.microsoft.com/en-us/agents/architecture/multi-agent-patterns)<br>[Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)<br>[Cemri et al.: Why do multi-agent LLM systems fail?](https://arxiv.org/abs/2503.13657)<br>[jsonschema for Python](https://python-jsonschema.readthedocs.io/)<br>[Agent2Agent (A2A) protocol](https://a2a-protocol.org/latest/)<br>[A2A Python SDK (a2a-sdk)](https://pypi.org/project/a2a-sdk/)<br>[A2A samples](https://github.com/a2aproject/a2a-samples) |
| Chapter 19: Long-Running Agents | [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)<br>[AWS Builders' Library: Timeouts, retries and backoff with jitter](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter)<br>[Stripe: Idempotent requests](https://docs.stripe.com/api/idempotent_requests)<br>[microservices.io: The Saga pattern](https://microservices.io/patterns/data/saga.html)<br>[Temporal documentation](https://docs.temporal.io/) |
| Chapter 20: Planning and Model Routing | [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)<br>[Python docs: graphlib](https://docs.python.org/3/library/graphlib.html)<br>[Yao et al.: ReAct](https://arxiv.org/abs/2210.03629)<br>[Chen, Zaharia and Zou: FrugalGPT](https://arxiv.org/abs/2305.05176)<br>[Ong et al.: RouteLLM](https://arxiv.org/abs/2406.18665) |
| Chapter 22: Hybrid Architectures: Probabilistic Intelligence, Deterministic Control | [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)<br>[Salesforce: AI agent trends for 2026](https://www.salesforce.com/blog/ai-agent-trends-2026/)<br>[Python docs: sqlite3 set_authorizer](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.set_authorizer) |
| Chapter 23: Computer-Use Agents | [Playwright for Python](https://playwright.dev/python/)<br>[Claude docs: Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)<br>[OWASP GenAI: Prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) |
| Chapter 25: Agentic Security | [Simon Willison: The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)<br>[OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)<br>[Simon Willison: The Dual LLM pattern](https://simonwillison.net/2023/Apr/25/dual-llm-pattern/)<br>[Debenedetti et al.: Defeating prompt injections by design (CaMeL)](https://arxiv.org/abs/2503.18813)<br>[OWASP: SSRF prevention cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)<br>[NSA: MCP security design considerations](https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/nsa-releases-security-design-considerations-for-ai-driven-automation-leveraging/) |
| Chapter 26: Agent Identity and Authorization | [MCP: Authorization](https://modelcontextprotocol.io/docs/tutorials/security/authorization)<br>[PyJWT documentation](https://pyjwt.readthedocs.io/)<br>[OAuth 2.0 Token Exchange (RFC 8693)](https://www.rfc-editor.org/rfc/rfc8693)<br>[OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) |
| Chapter 28: AgentOps: Observability, Telemetry and SLOs for Agents | [OpenTelemetry GenAI semantic conventions (repository)](https://github.com/open-telemetry/semantic-conventions-genai)<br>[OpenTelemetry: GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/)<br>[Google SRE book: Service level objectives](https://sre.google/sre-book/service-level-objectives/)<br>[LangChain: State of Agent Engineering](https://www.langchain.com/state-of-agent-engineering)<br>[Moffatt v. Air Canada, 2024 BCCRT 149](https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html)<br>[Invariant Labs: GitHub MCP exploited](https://invariantlabs.ai/blog/mcp-github-vulnerability)<br>[AI Incident Database](https://incidentdatabase.ai/) |
| Chapter 29: Agent Performance Engineering: Latency, Throughput and Cost | [Claude docs: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)<br>[Claude docs: Rate limits](https://platform.claude.com/docs/en/api/rate-limits)<br>[Gil Tene: How NOT to measure latency](https://www.infoq.com/presentations/latency-response-time/)<br>[Wikipedia: Little's law](https://en.wikipedia.org/wiki/Little%27s_law) |
| Chapter 15: MCP in 2026: From Tool Calling to Agent Infrastructure | [MCP blog: The 2026-07-28 specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/)<br>[MCP: Tasks extension](https://modelcontextprotocol.io/extensions/tasks)<br>[The MCP Registry](https://modelcontextprotocol.io/registry/about)<br>[MCP: Enterprise-Managed Authorization](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization)<br>[MCP blog: The new MCP roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/)<br>[MCP joins the Agentic AI Foundation](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/) |

## Appendix H: Run the Book Free with a Local Model

You don't have to pay for API calls to learn from this book. The course kit can run an open-source model, **`qwen3.5:9b`**, in a Docker container on your own computer, and the book's code uses it without any changes. This appendix explains how to set it up, what to expect, and which exercises still need Claude. The same instructions, with every command in one place, are in the course kit's repository as **`LOCAL_MODEL.md`** (github.com/sbittla/building-agentic-ai/blob/main/LOCAL_MODEL.md); check it for updates if a command here doesn't work.

### Why qwen3.5:9b

- **It's good at tool calling, which is what agents do.** Every agent in this book depends on the model choosing the right tool and filling in its arguments. Among open models small enough for an ordinary computer, the Qwen 3.5 family scores at the top on tool-calling benchmarks (the 9B model scores 66.1 on BFCL-V4 and 79.1 on TAU2-Bench, ahead of much larger older models).
- **It fits.** The download is about 6.6 GB. With a 32k-token context it needs roughly 10–12 GB of memory in total, leaving room for Docker, the course container and your other programs on a 16 GB machine, and plenty on 32 GB.
- **It runs with or without a GPU.** With an NVIDIA GPU with 8 GB of video memory or more, it runs entirely on the GPU. Without one, it runs on the CPU, slower but usable.
- **It's free and open.** Apache 2.0 licence: use it for learning and for anything you build.
- **It thinks before it answers,** like Claude with thinking on, so the book's lessons about thinking blocks apply unchanged.

### What you need

| | Minimum | Recommended |
| --- | --- | --- |
| Memory (RAM) | 16 GB | 32 GB |
| Free disk space | 10 GB | 15 GB |
| GPU | None (CPU works) | NVIDIA with 8 GB or more of video memory |
| Software | Docker, as in "How to Use This Book" | the same |

**Windows:** Docker Desktop runs Linux containers inside WSL 2, which usually gets about half of your RAM. That's enough for `qwen3.5:9b`. If the model stops with an out-of-memory error, give WSL more: create a file named `.wslconfig` in your user folder containing the two lines `[wsl2]` and `memory=12GB` (or more), run `wsl --shutdown`, then restart Docker Desktop.

**macOS:** Docker can't use a Mac's GPU, so the model would run on the CPU only. On Apple Silicon Macs it's much faster to install Ollama as a normal Mac app instead (see "On a Mac" below).

**Linux:** nothing extra. For an NVIDIA GPU, install the NVIDIA Container Toolkit.

### Set it up (about 15 minutes, plus the download)

1. Run `./course.sh setup` and choose option **2**, or add the line `PROVIDER=local` to your `.env` file.
2. Start the model server and download the model (only the first time):

```bash
./course.sh local up          # Windows: .\course.cmd local up
./course.sh local up --gpu    # the same, using an NVIDIA GPU
```

3. Check that it answers:

```bash
./course.sh local status      # the model server is running and qwen3.5:9b is downloaded
./course.sh check --api       # one tiny call: the reply comes from qwen3.5:9b
```

That's all. Every `./course.sh` command now uses the local model: exercises, chapter files, `ask`, capstones, the Chapter 30 agent API and `live-check`. The model stays loaded for 30 minutes after its last use, so later runs start quickly. When you've finished for the day, `./course.sh local down` stops it and frees the memory. The download stays in a Docker volume, so you don't download it again.

**On a Mac (faster):** install Ollama from ollama.com, run `ollama pull qwen3.5:9b` in Terminal, and set the context length to 32k in Ollama's settings. Then add two lines to `.env`, `PROVIDER=local` and `OLLAMA_URL=http://host.docker.internal:11434`, and run `./course.sh local up --native`. It starts only the kit's adapter and uses your Mac's Ollama.

### Switching between Claude and the local model

One line in `.env` decides which model every command uses:

| `.env` line | Model |
| --- | --- |
| `PROVIDER=claude`, or no `PROVIDER` line | Claude, through the Claude API, with your `ANTHROPIC_API_KEY` |
| `PROVIDER=local` | `qwen3.5:9b` on your computer; no key needed |

You can switch as often as you like, for example to run one **Claude only** exercise. `./course.sh check` shows which one is active. Other settings you can add to `.env`:

| Setting | Default | What it does |
| --- | --- | --- |
| `LOCAL_MODEL` | `qwen3.5:9b` | The local model to use. The book is tested with this one. |
| `LOCAL_CONTEXT` | `32768` | The context window in tokens. Lower it to `16384` if you run short of memory. |
| `LOCAL_THINKING` | `auto` | `off` skips the model's reasoning step: much faster on a CPU, a little less accurate. |
| `OLLAMA_URL` | the kit's container | Where Ollama runs; only for the Mac setup above. |

### What the kit does for you

Ollama speaks the same Messages API as Claude for everything the chapters use most: messages, system prompts, tools, tool results, streaming and thinking. A few Claude features have no local equivalent, so the kit runs a small **adapter** (`course/local_adapter.py`) between the book's code and Ollama. It fills the gaps so your code doesn't have to change:

| Claude feature | Chapters | What the adapter does |
| --- | --- | --- |
| Forcing a tool (`tool_choice`) | 3, 11, capstones 3, 5 and 6 | Tells the model to call the tool, and asks again (up to twice) if it answers in text instead |
| Structured outputs (`output_config` with a JSON schema) | 3, 11, 15 | Turns the schema into a tool, checks the model's answer against the schema, and returns it as JSON text |
| Prompt caching (`cache_control`) | 16 | Removes it. The code runs, but nothing is cached, so exercise 16.5 shows no savings |
| Counting tokens | 16 | Returns an estimate (about four characters per token) |
| Server-side features: tool search, code execution, Agent Skills, Managed Agents | 3, 16, 18 | Returns a clear error saying the exercise needs Claude |

It's worth reading `local_adapter.py` once you've finished Chapter 11. At about 300 lines, it's a small, real example of the model-provider layer that section 24.6 describes.

### What to expect

The local model is a capable learning partner, but it isn't Claude. It picks the wrong tool more often, gives up on self-correction sooner (Chapters 8 and 10), and scores lower on the evaluation exercises. That's a lesson in itself: the evals in Chapters 3, 8 and 15 measure exactly this difference, and exercises that compare approaches (11.7, 18.7) become more interesting.

Speed depends mostly on your hardware:

| Setup | A short answer | A typical agent exercise (3–6 model calls) |
| --- | --- | --- |
| NVIDIA GPU with 8 GB or more | 1–3 seconds | 10–40 seconds |
| Apple Silicon Mac with Ollama as an app | 2–5 seconds | 20–60 seconds |
| CPU only | 10–30 seconds | 1–5 minutes |

The first call after `local up` takes longer while the model loads. To speed up a CPU-only machine: set `LOCAL_THINKING=off`; run evaluation exercises with one trial instead of three; and use fewer users and shorter runs in the load tests (15.7 and 19.7), for example 3 users for 1 minute. Queueing and rate limits still show clearly.

### When something goes wrong

| Symptom | Fix |
| --- | --- |
| "Can't reach the local model" | Start it: `./course.sh local up`. Check with `./course.sh local status`. |
| "The model 'qwen3.5:9b' isn't downloaded yet" | Run `./course.sh local up` again; it resumes the download. |
| The model stops, or Docker says it ran out of memory | Close other programs, set `LOCAL_CONTEXT=16384`, or give Docker more memory (Windows: see `.wslconfig` above). |
| Very slow | Use `--gpu` if you have an NVIDIA GPU; set `LOCAL_THINKING=off`; see the speed tips above. |
| "The local model didn't call … correctly after 3 tries" | Run the exercise again (answers vary from run to run), make the prompt or tool description clearer (Chapter 3), or use Claude for that run. |
| "… needs Claude, not the local model" | The exercise uses a Claude-only feature. Set `PROVIDER=claude` for it. |
| `--gpu` fails, or the GPU isn't used | Update the NVIDIA driver. On Windows, use Docker Desktop with WSL 2; on Linux, install the NVIDIA Container Toolkit. `./course.sh local logs` shows whether Ollama found the GPU. |
| Port 11434 is already in use | Ollama is already running as an app on your computer. Quit it, or use it: set `OLLAMA_URL=http://host.docker.internal:11434` and run `./course.sh local up --native`. |

### Which exercises need which model

Every exercise box shows one of four labels. Of the book's {{exercises:all}} exercises, {{exercises:none}} need **no model**, {{exercises:any}} run on **qwen3.5:9b or Claude**, {{exercises:claude-rec}} are **Claude recommended** and {{exercises:claude-only}} are **Claude only**. `./course.sh list` shows the labels too, and `./course.sh ex <id>` warns you before running a Claude-only exercise on the local model.

| Chapter | No model | qwen3.5:9b or Claude | Claude |
| --- | --- | --- | --- |
| Chapter 0: Foundations | 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7 | — | — |
| Interlude: The Python You'll Need | P.1, P.2, P.3, P.4, P.5 | — | — |
| Chapter 1: What an Agent Is (and Isn't) | 1.1, 1.2, 1.7, 1.8 | 1.3, 1.4, 1.5, 1.6 | — |
| Interlude: Testing with pytest | T.1, T.2, T.3, T.4 | — | — |
| Chapter 2: Tool Calling (Function Calling) | 2.1, 2.2 | 2.3, 2.4, 2.5, 2.6 | — |
| Chapter 3: Tool Selection, Routing and Tool Search | 3.1, 3.2 | 3.3, 3.4, 3.5, 3.6 | 3.7 (only) |
| Chapter 4: The Agent Loop | 4.1 | 4.2, 4.3, 4.4, 4.5 | — |
| Chapter 5: State and Short-Term Memory | 5.1, 5.2 | 5.3, 5.4, 5.5, 5.6, 5.7 | — |
| Interlude: Regular Expressions | R.1, R.2, R.3, R.4 | — | — |
| Chapter 6: Agentic Search: Exploring an Environment | 6.1, 6.4 | 6.2, 6.3, 6.5, 6.6 | — |
| Chapter 7: Real APIs | 7.1, 7.2 | 7.3, 7.4, 7.5, 7.6 | — |
| Interlude: SQL in One Sitting | S.1, S.2, S.3, S.4 | — | — |
| Chapter 8: Self-Correction: A Text-to-SQL Agent | 8.1, 8.2 | 8.3, 8.4, 8.5, 8.6, 8.7 | — |
| Chapter 9: Human-in-the-Loop Approval | 9.1, 9.2 | 9.3, 9.4, 9.5, 9.6 | — |
| Chapter 10: Feedback Loops | 10.1, 10.2 | 10.3, 10.4, 10.5, 10.6, 10.7 | — |
| Interlude: Asynchronous Python | A.1, A.2, A.3, A.4 | — | — |
| Chapter 11: Multi-Agent Systems | 11.1, 11.2 | 11.3, 11.4, 11.5, 11.6, 11.7 | — |
| Chapter 12: MCP Fundamentals and Your First Server | 12.1, 12.2, 12.3, 12.4, 12.6, 12.7 | — | 12.5 (only) |
| Chapter 13: Build Your Own MCP Client | 13.1, 13.2 | 13.3, 13.4, 13.5, 13.6, 13.7, 13.8 | — |
| Chapter 14: Using Servers You Didn't Write | 14.1, 14.2 | 14.3, 14.4, 14.5 | — |
| Chapter 15: MCP in 2026: From Tool Calling to Agent Infrastructure | 15.1, 15.2, 15.3, 15.4, 15.5, 15.6 | 15.7 | — |
| Chapter 16: Context Engineering | 16.1, 16.2, 16.6 | 16.3, 16.4, 16.8 | 16.5 (recommended), 16.7 (only) |
| Chapter 17: Agent Memory Engineering | 17.1, 17.2, 17.4, 17.6, 17.7 | 17.3, 17.5, 17.8 | — |
| Chapter 18: Agentic RAG and Knowledge Systems | 18.1, 18.2, 18.3, 18.4 | 18.5, 18.6, 18.7, 18.8, 18.9 | — |
| Chapter 19: Long-Running Agents | 19.1, 19.2, 19.4 | 19.3, 19.5, 19.6 | — |
| Chapter 20: Planning and Model Routing | 20.1, 20.2, 20.3 | 20.4, 20.5, 20.6 | — |
| Chapter 21: Multi-Agent Orchestration | 21.1, 21.2 | 21.3, 21.4, 21.5 | 21.6 (recommended) |
| Chapter 22: Hybrid Architectures: Probabilistic Intelligence, Deterministic Control | 22.1, 22.2 | 22.3, 22.4, 22.5, 22.6 | — |
| Chapter 23: Computer-Use Agents | 23.1, 23.2, 23.3 | — | 23.4 (recommended), 23.5 (recommended), 23.6 (recommended) |
| Chapter 24: Skills, Frameworks and Agent Runtimes | 24.1, 24.2, 24.9 | 24.8 | 24.3 (recommended), 24.4 (recommended), 24.5 (recommended), 24.6 (only), 24.7 (only) |
| Chapter 25: Agentic Security | 25.1, 25.2, 25.5 | 25.3, 25.4, 25.6 | — |
| Chapter 26: Agent Identity and Authorization | 26.1, 26.2, 26.3, 26.5 | 26.4, 26.6 | — |
| Chapter 27: Agent Evaluation: Dimensions, Trajectories and Scorecards | 27.1, 27.2, 27.7 | 27.3, 27.4, 27.5, 27.6, 27.8 | — |
| Chapter 28: AgentOps: Observability, Telemetry and SLOs for Agents | 28.1, 28.2, 28.4, 28.5, 28.6, 28.7 | 28.3 | — |
| Chapter 29: Agent Performance Engineering: Latency, Throughput and Cost | 29.1, 29.3 | 29.2, 29.4, 29.6 | 29.5 (recommended) |
| Chapter 30: Deploying Agents: From One Service to an Agent Platform | 30.1 | 30.2, 30.3, 30.4, 30.5, 30.6, 30.7 | — |
| Capstones 1–6 | — | All six | 4 and 6 (recommended) |

The exercises that need, or work much better with, Claude:

| Exercise | Label | Why |
| --- | --- | --- |
| 3.7 Tool search at scale | Claude only | Tool search runs on Anthropic's servers. |
| 12.5 Claude Desktop | Claude only (Claude Desktop app) | Uses the Claude Desktop app (a free Claude plan works); no API key or local model is involved. |
| 16.5 Measure caching savings | Claude recommended | Prompt caching exists only on Claude; on the local model the savings are always zero. |
| 16.7 Let a program do the counting | Claude only | Programmatic tool calling runs code on Anthropic's servers. |
| 24.3 See the approval gate work | Claude recommended | The Agent SDK drives the Claude Code CLI; qwen3.5:9b runs it but often stalls or skips steps. |
| 24.4 Agent SDK with your MCP servers | Claude recommended | The Agent SDK drives the Claude Code CLI; qwen3.5:9b runs it but often stalls or skips steps. |
| 24.5 Same agent, three frameworks | Claude recommended | Includes an Agent SDK version; the other two run well on qwen3.5:9b. |
| 24.6 Write a skill | Claude only | Agent Skills run in Anthropic's code-execution container. |
| 24.7 A managed analyst | Claude only | Managed Agents are hosted by Anthropic. |
| 21.6 A mixed team | Claude recommended | Several agents, including one over A2A, must follow a multi-step brief. |
| 23.4 The injected note | Claude recommended | Operating a web page through many small steps is where the local model struggles most. |
| 23.5 Verify, don't trust | Claude recommended | Operating a web page through many small steps is where the local model struggles most. |
| 23.6 A queue that survives a crash | Claude recommended | Operating a web page through many small steps is where the local model struggles most. |
| 29.5 Halve the cost | Claude recommended | Cost per successful task is only meaningful with real prices and the model you ship. |

To check that everything works on your machine, run every exercise that uses a model, with its reference solution:

```bash
./course.sh live-check exercises --yes       # all of them (several hours on a CPU)
./course.sh live-check exercises 4 --yes     # just Chapter 4
```

It writes `workspace/live_exercises_report.md`. **PASS** means the solution ran without errors; read the answers to judge their quality. The kit's own checks never call a model: `./course.sh selftest` and `./course.sh check-solutions` are free with either choice.

## Appendix I: Reference Cards

The book's frameworks on a few pages, for design reviews and on-call. Each card points to the chapter that explains it.

### Card 1: Do you need an agent? (section 1.3)

| Option | Choose it when |
| --- | --- |
| Function | The rules are exact and known |
| Workflow | The steps are known in advance |
| State machine | The process has stages, rules and audits |
| RAG | The job is answering from documents |
| Single LLM call | One prompt does the job |
| Agent | The steps depend on what you find along the way |
| Multi-agent system | The work splits into independent parts, and the cost is worth it |

Ask: can I draw the flowchart first? What does a wrong step cost? Can I tell when it's done and right? Is the flexibility worth the cost and latency?

### Card 2: The dimensions of agency (section 1.4)

Autonomy, state, planning, tool use, environmental interaction, persistence, feedback, delegation, adaptation. Turn up only the dimensions the task needs; each one adds a way to fail and needs its own controls.

### Card 3: The agent architecture reference model (sections 1.7 and 30.9)

User / API → agent runtime (planning, memory, context, tools, policies) → model → MCP, APIs, A2A → environment, with evaluation and observability across every layer.

### Card 4: MCP, A2A, API or workflow? (section 21.8)

| You need to... | Use |
| --- | --- |
| Connect a model to a tool or to data | A tool; an MCP server to share it |
| Let independent agents collaborate across a boundary | A2A |
| Let one service call another, conventionally | An API |
| Run a deterministic business process | A workflow or state machine |
| Get a person's decision before acting | Human in the loop |
| Run work that takes hours and survives crashes | A durable workflow |
| Search and retrieve knowledge | A retrieval system |
| Do something local and simple | A plain tool |
| Share one front door for many tools, with policy | An MCP gateway |

### Card 5: The agent failure taxonomy (section 28.8)

For each class: how you detect it, how you mitigate it and how you evaluate the fix.

| Failure | First place to look |
| --- | --- |
| 1. Wrong tool | Tool descriptions (Chapter 3); trajectory checks (Chapter 27) |
| 2. Wrong arguments | Schemas and validation (Chapter 3); argument checks (Chapter 27) |
| 3. Tool failure | Retries, timeouts and errors as data (Chapters 2, 7, 19) |
| 4. Tool-result misinterpretation | Smaller, clearer results; answer checks (Chapters 8, 27) |
| 5. Hallucination | Grounding and citations (Chapters 6, 18); groundedness checks (Chapter 27) |
| 6. Context overflow | Trimming, compaction, isolation (Chapter 16) |
| 7. Context contamination | Untrusted-content handling and quarantine (Chapters 14, 25) |
| 8. Planning failure | Plans as data, checked before running (Chapter 20) |
| 9. Infinite loop | Step caps and progress checks (Chapters 4, 10); loop detection (Chapter 28) |
| 10. Memory poisoning | A memory write gate and audits (Chapters 17, 25) |
| 11. Authorization failure | Scoped tokens checked at the tool (Chapter 26) |
| 12. Cost or latency runaway | Budgets in code, SLOs and alerts (Chapters 28, 29) |

### Card 6: The agent scorecard (section 27.6)

Success rate · reliability (pass^k) · tool accuracy · argument accuracy · task completion · safety violation rate · average steps · p50 and p95 latency · cost per task · cost per successful task. One scorecard per release, compared with the last; hard limits gate the release.

### Card 7: Agent SLOs (section 28.10)

Example targets to adapt, not universal truths: task success ≥ 95%; p95 latency < 8 s; cost per task < $0.05; tool-selection accuracy ≥ 98%; unsafe-action rate < 0.01%; human-escalation accuracy ≥ 95%; retrieval recall ≥ 90%. Each needs a named data source: traces, the eval suite or human review.

### Card 8: The agent performance model (section 29.1)

Total latency = model + tool + retrieval + orchestration + queueing + serialization.
Cost per task = model + tools + retrieval + infrastructure + retries + human review.
Measure under load: throughput and goodput, p50/p95/p99, tokens per request, cache hit rate, steps per task, cost per task and success rate, at rising concurrency, to find the knee.

### Card 9: Durable concepts and fast-changing details

| Durable concepts (this book's core) | Fast-changing details (marked **API-dependent**) |
| --- | --- |
| The agent loop, state, tools, context | Model names and prices |
| Evaluation, guardrails, authorization | SDK syntax and API field names |
| Observability, memory, reliability | Framework APIs and managed services |
| Performance and cost engineering | MCP specification versions |

Sections whose details change quickly carry an **API-dependent** note under their heading. Learn the concept from the section; take the parameter names from the current documentation.

## Appendix J: The Same Concepts on Other Platforms

This book's code uses the Claude API, plus a free local model through Ollama (Appendix H). Every concept carries over to other providers and to open-source stacks; only the names change. Use this table to find each concept elsewhere. It was checked in September 2026, and the names in it are the most perishable facts in the book: confirm them in each provider's current documentation before you rely on them.

| Concept | Claude API (this book) | OpenAI API | Google Gemini API | Open source |
| --- | --- | --- | --- | --- |
| Tool calling (Chapter 2) | `tools` with `input_schema`; `tool_use` and `tool_result` blocks | Function calling: `function_call` and `function_call_output` items (Responses API) | Function calling | Tool calling in Ollama and vLLM, through OpenAI-compatible APIs |
| Controlling tool choice (Chapter 3) | `tool_choice`: `auto`, `any`, a named tool or `none` | `tool_choice`: `auto`, `required`, `none` or a named function | A function-calling mode setting | `tool_choice` in vLLM's OpenAI-compatible server |
| Structured outputs (Chapter 3) | JSON Schema output format; strict tools | Structured outputs with a JSON schema | Structured output with a JSON schema | Ollama's `format` with a JSON schema; vLLM structured outputs |
| Reasoning controls (Chapter 4) | Adaptive thinking and `effort` | `reasoning.effort` | Thinking settings, which vary by model | Ollama's `think` option; reasoning parsers in vLLM |
| Prompt caching (Chapter 16) | `cache_control` breakpoints, or automatic caching | Automatic caching, with an optional cache key | Implicit (automatic) and explicit context caching | Prefix caching in inference servers such as vLLM |
| Many tools: tool search (Chapter 3) | Tool search tool with `defer_loading` | Tool search with deferred loading | No direct equivalent found | Build it: search your own tool catalog (section 15.5) |
| Code execution (Chapter 16) | Code execution tool; programmatic tool calling | Code Interpreter tool | Code execution tool | Your own sandbox (Chapter 10) |
| Computer and browser use (Chapter 23) | Computer use and browser use tools | Computer use tool | Computer Use tool | Playwright and your own harness (Chapter 23) |
| Batch processing (Chapter 27) | Message Batches API | Batch API | Batch API | Offline batch inference in vLLM |
| Token counting (Chapter 16) | Token counting endpoint | Input token counting endpoint | Token counting method | Token counts returned with each response |
| MCP (Part 5) | MCP connector in the API; Claude apps are MCP hosts | Remote MCP servers as a tool | Remote MCP support | The MCP SDKs; LangChain MCP adapters; MCP gateways |
| Agent runtimes (Chapter 24) | Claude Agent SDK; Claude Managed Agents | Agents SDK; AgentKit | Agent Development Kit (ADK); Agent Engine | LangGraph, self-hosted or managed |
| Agent-to-agent (Chapter 21) | Through the A2A SDK, not an API feature | Through the A2A SDK | A2A support in Agent Engine; A2A began at Google and is now a Linux Foundation project | The `a2a-sdk` package; A2A endpoints in LangGraph's agent server |

When you read a chapter, keep three layers apart: the **concept** (tool calling), the **implementation** you run (the Claude API, or the local model through the kit's adapter) and the **equivalent** on the platform you use at work. Chapter 24 shows one agent on several runtimes, and section 24.6 shows the same loop on another provider's SDK.
