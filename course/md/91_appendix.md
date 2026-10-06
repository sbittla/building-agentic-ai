# Appendices

The appendices are reference material for when you need a fact quickly. They cover how to run the course kit, fixes for common errors, a glossary, sources, costs, the solutions folder, where to learn more, the free local model, one-page reference cards and the same concepts on other platforms. You don't need to read them in order: keep them open while you work through the chapters and capstones.

## Appendix A: Running the Course Kit with Docker

Every exercise runs in the course kit's Docker image. You type commands on your own computer; Docker runs them in the container, against the files in your `workspace` folder. On Windows, use `.\course.cmd` wherever this book shows `./course.sh`.

### What's in the kit

Table: Files and folders in the kit
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

Table: Course kit commands
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

Table: How `ex` runs each kind of exercise
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

Table: Common errors and how to fix them
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

Table: Symptoms and where to look first
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

Table: Glossary
| Term | Meaning |
| --- | --- |
| A2A (Agent2Agent) | An open protocol for independent agents to find each other (through agent cards) and hand off tasks; complements MCP (section 21.7) |
| Adaptive thinking | The model decides how much to reason before each answer or tool call; on by default on current Claude models |
| Agent | An LLM that chooses and calls tools in a loop until a task is done |
| Agent architecture reference model | The layers of every agent system: user/API, runtime, planning, memory, context, tools, policies, model, MCP/APIs/A2A, environment, with evaluation and observability across (section 1.7) |
| Agent card | An A2A agent's public JSON description of its skills, endpoint and security, at `/.well-known/agent-card.json` |
| Agent inventory | One record per agent: its owner, kind, model, tools and scopes, the data it touches, its risk tier and current version; the starting point of agent governance (section 30.12) |
| Agent lifecycle | The stages every agent goes through: decide, design, build, evaluate, release, operate, improve and, finally, retire (sections 1.10 and 30.13) |
| Agent SDK | The Claude Agent SDK: the agent runtime behind Claude Code, as a library |
| Agent Skill | A folder with a `SKILL.md` (name, description, instructions) and optional files, loaded only when a task needs it; an open format |
| Agent version | The whole bundle that sets an agent's behavior, released together: model id, system prompt, tool definitions and server versions, skills, policies and the eval suite that approved it (section 30.13) |
| Agentic search | Finding information by letting the model list, search and read |
| Approval gate | Code that asks a human before a risky tool runs |
| Audit log | An append-only record of every action an agent took |
| Blackboard (shared board) | A shared record of a team's tasks and results that agents read and only the orchestrator writes (section 21.3) |
| BM25 | A classic keyword-ranking formula that weights rare words more |
| Cache hint (MCP) | `ttlMs` and `cacheScope` on a list result: how long a client may reuse it, and whether it may be shared across users (section 15.3) |
| Canary release | Sending a small share of real traffic, say 1% and then 10%, to a new version and comparing its SLOs with the current one before going further (section 30.13) |
| Cascade | Trying a cheaper model first and escalating to a stronger one only when a check fails (section 20.8) |
| Checkpoint | Saving a step's status and result before the next step starts, so a crashed job can resume (section 19.3) |
| Compaction | Replacing older conversation turns with a summary to save context |
| Compensation | Undoing completed steps, newest first, when a long job is abandoned; the saga pattern (section 19.7) |
| Computer-use agent | An agent that operates a user interface, a web page or a desktop, instead of calling an API (Chapter 23) |
| Confidence interval (95%) | The range that very likely contains the real pass rate, given how many runs you measured; the kit computes it with the Wilson formula (measurement interlude, Chapter 27) |
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
| Episodic, semantic and procedural memory | Long-term memory of what happened, durable facts and how to do things, each with its own policy (section 17.2) |
| Error budget | How much failure an SLO allows over a window; spending it fast triggers alerts (section 28.10) |
| Evaluation (eval) suite | A set of test cases with checks, run after every change |
| Exfiltration | Getting private data out of a system, for example inside a URL the agent fetches |
| Extension (MCP) | An optional, named protocol feature, such as Tasks or MCP Apps, used only when client and server both declare it (section 15.4) |
| Failure taxonomy | The 12 classes of agent failure, each with detection, mitigation and evaluation (section 28.8) |
| Flaky case | A test case that passes on some runs and fails on others: a sign the agent is guessing (measurement interlude) |
| Gateway (MCP) | A server in front of other MCP servers that allow-lists tools, checks tokens, rate-limits and audits every call (section 30.9) |
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
| Pass rate | The share of runs that pass their checks; report it with its interval (measurement interlude) |
| Pass^k | The share of eval cases that pass on every one of k repeated runs |
| Plan (as data) | A list of steps with tools, dependencies and done conditions that code can check before running (section 20.2) |
| Programmatic tool calling | The model writes a program that calls your tools in a sandbox, so bulky results stay out of the context |
| Progressive discovery | Offering tools through search instead of listing them all at once (section 30.9) |
| Prompt (MCP) | A reusable prompt template a server exposes |
| Prompt caching | Reusing the processed form of an unchanged prompt prefix, at a tenth of the input price |
| Prompt injection | Text in data (web pages, files, issues) that tries to give the model instructions |
| RAG | Retrieval-augmented generation: fetch similar document chunks, then call the model |
| Rate limit | A cap on how many requests a caller may make in a period (HTTP 429 when exceeded) |
| Recall@k / MRR | Retrieval metrics: is the right document in the top k, and how high does it rank |
| Reciprocal rank fusion | Merging several rankings by adding 1/(60 + rank) for each result |
| Resource (MCP) | Read-only data a server exposes by URI |
| Risk tier | How much harm an agent could do, which sets how much review it needs before launch; the EU AI Act sorts AI systems into tiers in the same spirit (section 30.12) |
| Rollback | Switching traffic back to the previous version by configuration, without a deploy; automatic when a canary burns its error budget (section 30.13) |
| Routing | A cheap decision before an expensive one; this book uses it for four choices: a tool (Chapter 3), an agent (Chapter 11), context sources (Chapter 16) and a model (Chapter 20) |
| Scorecard (agent) | One table of quality, safety, cost and latency metrics for a release, compared with the last (section 27.6) |
| Server tool | A tool that runs on the provider's servers (web search, code execution, tool search), not in your code |
| Shadow mode | Running a new version on a copy of real traffic without showing its answers or taking its actions, to compare it with the current version (section 30.13) |
| SLO (service-level objective) | A target for a measured behavior, such as task success ≥ 95% over 30 days (section 28.10) |
| SSE (Server-Sent Events) | A simple way for a server to stream events to a client over one HTTP response |
| SSRF | Server-side request forgery: tricking a server or agent into fetching an internal address |
| Stateless protocol | Each request carries everything the server needs, so any copy of the server can answer it; MCP since 2026-07-28 (section 15.2) |
| stdio / Streamable HTTP | The two standard MCP transports: local subprocess or web service |
| Stop reason | Why the model stopped: `end_turn`, `tool_use`, `max_tokens` and others |
| Structured outputs | An API feature that makes the model's reply match a JSON Schema |
| System prompt | Instructions that set the model's behavior for a whole conversation |
| Tasks (MCP) | An MCP extension for long-running calls: the server returns a task id that the client polls with `tasks/get` (section 30.8) |
| Thinking block | A content block holding the model's reasoning, returned before its answer; send it back unchanged |
| Token | A chunk of text the model reads or writes; the unit of cost |
| Token bucket | A rate-limit method: each caller's bucket refills at a steady rate and each request takes one token |
| Tool | A function the model can ask your code to run, described by name, description and schema |
| Tool search | Deferring most tool definitions and letting the model search for the ones it needs |
| Trace | The step-by-step record of one agent run |
| Workflow | A fixed sequence of LLM calls and code, with steps decided by the developer |
| Working memory | What the agent holds during one task: the conversation, the plan and tool results; also called short-term memory (Chapters 5, 16 and 17) |

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

Costs depend on the model, how often you rerun exercises, and how long your conversations get. The estimates below come from one cost model, `dev/cost_model.py` in the course kit, which also writes the kit's `COST_MODEL.md`; every cost figure in this book and the kit's README comes from it. It assumes Claude Sonnet 5 at $2 per million input tokens and $10 per million output tokens (2026 prices), and an *agent run* (one task) of 3–4 model calls with 2,500–3,000 input and 500–700 output tokens per call, about {{cost:run}}. It counts how many agent runs each paid exercise makes: most make one, but evaluation suites, benchmarks and load tests make dozens. One clean pass of every paid exercise is {{cost:first}}; a learner reruns while debugging and tries variations, so the table doubles that. Check current prices on the provider's pricing page.

Table: Estimated cost by part, for a learner (twice the first pass, for reruns)
| Part | Paid exercises | Agent runs, first pass | Estimated cost | Biggest items |
| --- | ---: | ---: | --- | --- |
| 0. Foundations | 0 | 0 | $0 | — |
| 1. Your first agent | 17 | 124 | $7.4–13 | 4.5 (50 runs), 3.4 (20 runs), 3.6 (20 runs) |
| 2. State and environment | 9 | 42 | $2.5–4.4 | 6.6 (30 runs), 6.2 (3 runs), 6.5 (3 runs) |
| 3. Real-world tools | 14 | 118 | $7.1–12 | M.3 (72 runs), 8.7 (15 runs), 7.6 (10 runs) |
| 4. Autonomy | 10 | 61 | $3.7–6.3 | 10.7 (30 runs), 11.6 (20 runs), 11.7 (4 runs) |
| 5. MCP and interoperability | 9 | 11 | $0.66–1.1 | 13.8 (3 runs) |
| 6. Context, memory and knowledge | 13 | 49 | $2.9–5.1 | 16.5 (15 runs), 18.6 (10 runs), 18.5 (8 runs) |
| 7. Advanced agent architectures | 23 | 133 | $8–14 | 24.5 (72 runs), 20.5 (24 runs), 21.6 (10 runs) |
| 8. Trust | 5 | 22 | $1.3–2.3 | 25.6 (18 runs) |
| 9. Production engineering | 17 | 378 | $23–39 | 30.6 (200 runs), 29.2 (50 runs), 29.5 (48 runs) |
| **All chapters** | **117** | **938** | **About $55–100** | First pass alone: $28–49 |
| Each capstone | — | about 120 | $7.2–12 | Evaluation runs and a load test |
| Cloud deployment (30.7) | — | — | Usually $0 on a free tier | The host's own charges; set a budget alert and delete the service afterward |

Claude Sonnet 5 uses a new tokenizer that counts about 30% more tokens for the same text than earlier models, and thinking is billed as output, so compare costs by measuring your own runs rather than by reusing older token counts. With Claude Haiku 4.5 ($1 input, $5 output per million tokens), the totals are roughly half. Prompt caching (Chapter 16) and smaller tool outputs cut them further. Running `./course.sh check-solutions` is always free.

**Or pay nothing:** with the free local model (`PROVIDER=local`, Appendix H), every exercise except the {{exercises-word:claude-only}} marked **Claude only** costs nothing. A sensible budget plan is to do the book locally and buy a few dollars of Claude credit for those {{exercises-word:claude-only}} and the {{exercises-word:claude-rec}} marked **Claude recommended**. If you use Claude throughout, the table's biggest items (the load tests and evaluation suites) are the ones worth running on the local model or Claude Haiku 4.5 first.

### Estimate a run yourself

```
cost ≈ (input tokens × input price + output tokens × output price) ÷ 1,000,000
```

Every agent in this book reports its input and output tokens, so you can apply this after any run. Chapter 16's `cost()` function does it for you, including cached tokens.

## Appendix F: The Solutions Folder

The `solutions` folder sits next to `course.sh`. Inside the container it's mounted read-only at `/solutions`, so you can read and run it but never change it by accident.

Table: What's in the solutions folder
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

### How the solutions are verified, and what that does and doesn't prove

Two kinds of evidence back the solutions, and the repository keeps them apart:

- **Deterministic checks.** `./course.sh check-solutions` runs every reference solution, capstone and exercise command against a scripted stand-in model, with no API key. The same commit gives the same result on any machine, so it proves the code runs and the checks pass, not that a real model will make the same choices. Every push runs it in the course image on GitHub, and `python dev/verify.py` writes the result with the commit, the hash of `requirements.lock` and the environment to `verification/offline.json`. A test that needs a program only the image has is reported as *skipped, needs …*, never as a pass.
- **Runs with a real model.** `./course.sh run-chapter` runs each exercise's reference solution with the free local model or Claude, and records the model, the commit and the package versions in each chapter's `summary.json`. A model's answers vary between runs, so a pass shows the exercise works end to end, not that it always will; that's what the measurement interlude's repeated trials are for.

The README's *Verified results* section shows both, with passed, failed, written answers, exercises that need a person and exercises not run yet counted separately. Each tagged release (section "Book editions and code versions" in the README) carries its results as files you can download.

## Appendix G: Where to Learn More

Nobody learns this field from one book. This appendix lists where to get help when you're stuck, free courses that complement this one, and how to keep up as models and tools change. Each chapter's **Learn more** section lists the resources for its own topics; the last table here gathers all of them by chapter so you can find any link again.

### When you're stuck: where to ask

Before asking, search the exact error message, and include your code, the full error and what you expected. Never paste your API key or `.env` file into a question.

Table: Where to ask for help
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

Table: Free courses
| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic Academy**<br>[anthropic.skilljar.com](https://anthropic.skilljar.com) | Free courses: Claude API, MCP, Claude Code, agent skills | Start here |
| **Anthropic courses on GitHub**<br>[github.com/anthropics/courses](https://github.com/anthropics/courses) | Free notebooks: prompt engineering and tool use | Start here |
| **DeepLearning.AI short courses**<br>[deeplearning.ai/courses?types=short_course](https://www.deeplearning.ai/courses?types=short_course) | One- to two-hour free courses on agents, RAG, evals and MCP | Start here |
| **Hugging Face AI Agents Course**<br>[huggingface.co/learn/agents-course](https://huggingface.co/learn/agents-course) | Free, vendor-neutral, with a certificate | Go deeper |
| **Hugging Face MCP Course**<br>[huggingface.co/learn/mcp-course](https://huggingface.co/learn/mcp-course) | Free MCP course with hands-on units | Go deeper |
| **Claude docs: Prompt engineering overview**<br>[platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) | Writing prompts that work; useful in every chapter | Start here |

### Keeping up to date

Model names, prices and SDK features change every few months. Start by checking that your book, your code and your environment belong together:

Table: This printing and the code it was tested with
| Book printing | Repository tag | Exercises | Python | Default models | MCP specification | Verified |
| --- | --- | ---: | --- | --- | --- | --- |
| Second printing, October 2026 | `edition-1.1` | {{exercises:all}} | 3.12 | `claude-sonnet-5`, `claude-haiku-4-5`, `qwen3.5:9b` | 2026-07-28 | 6 October 2026 |

`git describe --tags` in the kit folder prints the tag you have, and `./course.sh check` prints the Python and library versions in the image. Four files in the course kit track what changes after that:

Table: How the course kit tracks change
| File | What it tells you |
| --- | --- |
| `VERSION_MATRIX.md` | The exact version of every library, MCP server, model and protocol the book was tested with, the date, and which sections depend on fast-changing details. It also explains how to tell a protocol change (your agent may behave differently) from an SDK change (your code may stop running). |
| `CHANGELOG.md` | What changed between tags of the repository |
| `MIGRATION.md` | What to change in your own code when you move to a newer tag |
| `ERRATA.md` | Mistakes found in each printing, with corrections. Your printing's tag never moves, so its code always matches your book |

These pages are where changes in the wider world appear first.

Table: Where changes appear first
| Resource | What you'll find | Level |
| --- | --- | --- |
| **Claude Platform release notes**<br>[platform.claude.com/docs/en/release-notes/overview](https://platform.claude.com/docs/en/release-notes/overview) | New models, API features and deprecations, as they ship | Start here |
| **Claude docs: Models overview**<br>[platform.claude.com/docs/en/models/overview](https://platform.claude.com/docs/en/models/overview) | Current model names and prices; check before changing MODEL in .env | Start here |
| **Anthropic Engineering blog**<br>[anthropic.com/engineering](https://www.anthropic.com/engineering) | In-depth posts on agents, tools, evals and context | Go deeper |
| **MCP blog**<br>[blog.modelcontextprotocol.io](https://blog.modelcontextprotocol.io) | Protocol changes and new specification versions | Go deeper |
| **Simon Willison's weblog**<br>[simonwillison.net](https://simonwillison.net) | A well-known independent developer's daily notes on LLMs and agent security | Go deeper |
| **MCP roadmap**<br>[modelcontextprotocol.io/development/roadmap](https://modelcontextprotocol.io/development/roadmap) | The protocol's priorities and upcoming changes | Go deeper |

### Every link in this book, by chapter

Table: Every link in this book, by chapter
@@all-links-table

## Appendix H: Run the Book Free with a Local Model

You don't have to pay for API calls to learn from this book. The course kit can run an open-source model, **`qwen3.5:9b`**, in a Docker container on your own computer, and the book's code uses it without any changes. This appendix explains how to set it up, what to expect, and which exercises still need Claude. The same instructions, with every command in one place, are in the course kit's repository as **`LOCAL_MODEL.md`** (github.com/sbittla/building-agentic-ai/blob/main/LOCAL_MODEL.md); check it for updates if a command here doesn't work.

### Why qwen3.5:9b

- **It's good at tool calling, which is what agents do.** Every agent in this book depends on the model choosing the right tool and filling in its arguments. Among open models small enough for an ordinary computer, the Qwen 3.5 family scores at the top on tool-calling benchmarks (the 9B model scores 66.1 on BFCL-V4 and 79.1 on TAU2-Bench, ahead of much larger older models).
- **It fits.** The download is about 6.6 GB. With a 32k-token context it needs roughly 10–12 GB of memory in total, leaving room for Docker, the course container and your other programs on a 16 GB machine, and plenty on 32 GB.
- **It runs with or without a GPU.** With an NVIDIA GPU with 8 GB of video memory or more, it runs entirely on the GPU. Without one, it runs on the CPU, slower but usable.
- **It's free and open.** Apache 2.0 licence: use it for learning and for anything you build.
- **It thinks before it answers,** like Claude with thinking on, so the book's lessons about thinking blocks apply unchanged.

### What you need

Table: Hardware for the local model
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

Table: Choosing the model in `.env`
| `.env` line | Model |
| --- | --- |
| `PROVIDER=claude`, or no `PROVIDER` line | Claude, through the Claude API, with your `ANTHROPIC_API_KEY` |
| `PROVIDER=local` | `qwen3.5:9b` on your computer; no key needed |

You can switch as often as you like, for example to run one **Claude only** exercise. `./course.sh check` shows which one is active. Other settings you can add to `.env`:

Table: Local-model settings
| Setting | Default | What it does |
| --- | --- | --- |
| `LOCAL_MODEL` | `qwen3.5:9b` | The local model to use. The book is tested with this one. |
| `LOCAL_CONTEXT` | `32768` | The context window in tokens. Lower it to `16384` if you run short of memory. |
| `LOCAL_THINKING` | `auto` | `off` skips the model's reasoning step: much faster on a CPU, a little less accurate. |
| `OLLAMA_URL` | the kit's container | Where Ollama runs; only for the Mac setup above. |

### What the kit does for you

Ollama speaks the same Messages API as Claude for everything the chapters use most: messages, system prompts, tools, tool results, streaming and thinking. A few Claude features have no local equivalent, so the kit runs a small **adapter** (`course/local_adapter.py`) between the book's code and Ollama. It fills the gaps so your code doesn't have to change:

Table: What the local-model adapter does
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

Table: Local-model speed by hardware
| Setup | A short answer | A typical agent exercise (3–6 model calls) |
| --- | --- | --- |
| NVIDIA GPU with 8 GB or more | 1–3 seconds | 10–40 seconds |
| Apple Silicon Mac with Ollama as an app | 2–5 seconds | 20–60 seconds |
| CPU only | 10–30 seconds | 1–5 minutes |

The first call after `local up` takes longer while the model loads. To speed up a CPU-only machine: set `LOCAL_THINKING=off`; run evaluation exercises with one trial instead of three; and use fewer users and shorter runs in the load tests (15.7 and 19.7), for example 3 users for 1 minute. Queueing and rate limits still show clearly.

### When something goes wrong

Table: Local-model problems and fixes
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

Table: Exercises by chapter and the model they need
@@exercise-model-table
| Capstones 1–6 | — | All six | 4 and 6 (recommended) |

The exercises that need, or work much better with, Claude:

Table: Exercises that need, or work much better with, Claude
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

Table: Options and when to choose each
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

### Card 3: The agent architecture reference model (sections 1.7 and 30.15)

User / API → agent runtime (planning, memory, context, tools, policies) → model → MCP, APIs, A2A → environment, with evaluation and observability across every layer.

### Card 4: MCP, A2A, API or workflow? (section 21.8)

Table: What to use for each need
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

Table: Failure classes and where to look first
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

Table: Durable concepts and fast-changing details
| Durable concepts (this book's core) | Fast-changing details (marked **API-dependent**) |
| --- | --- |
| The agent loop, state, tools, context | Model names and prices |
| Evaluation, guardrails, authorization | SDK syntax and API field names |
| Observability, memory, reliability | Framework APIs and managed services |
| Performance and cost engineering | MCP specification versions |

Sections whose details change quickly carry an **API-dependent** note under their heading. Learn the concept from the section; take the parameter names from the current documentation. `VERSION_MATRIX.md` in the course kit lists these sections with the versions they were tested on.

### Card 10: Kinds of agents (section 1.9)

Table: Kinds of agents and the risk to control first
| Kind | Main risk to control first |
| --- | --- |
| Assistant with tools | Wrong tool or invented answer (Chapters 2–4) |
| Knowledge agent | Answers the sources don't support (Chapters 6, 18) |
| Data analyst | Plausible numbers from a wrong query (Chapter 8) |
| Action agent behind approvals | Damage from one wrong action (Chapters 9, 22, 26) |
| Feedback-loop agent | Gaming or editing the check (Chapter 10) |
| Research team | Cost multiplied by the number of agents (Chapters 11, 21) |
| Planner | A bad plan run faithfully (Chapter 20) |
| Long-running agent | Repeated side effects after a restart (Chapter 19) |
| Computer-use agent | A click that can't be taken back (Chapter 23) |

Real systems combine kinds; name the kind of each part to find the controls it needs.

### Card 11: The agent lifecycle (sections 1.10 and 30.13)

Decide → design → build → evaluate → release → operate → improve, and back to build; retire when the agent is no longer needed.

Table: Lifecycle stages and when to move on
| Stage | Before you move on |
| --- | --- |
| Decide | You can say why a simpler option won't do |
| Design | Tools, context, rules in code and checks are written down |
| Evaluate | A case file, several trials, intervals and a scorecard |
| Release | CI gate passed, launch checklist done, shadow and canary planned, rollback ready |
| Operate | Traces, SLOs, alerts, budgets and a named owner |
| Improve | Every failure is a new case; one change at a time |
| Retire | Kill switch, revoked identity, gateway routes removed, data handled by policy, audit log kept |

## Appendix J: The Same Concepts on Other Platforms

This book's code uses the Claude API, plus a free local model through Ollama (Appendix H). Every concept carries over to other providers and to open-source stacks; only the names change. Use this table to find each concept elsewhere. It was checked in September 2026, and the names in it are the most perishable facts in the book: confirm them in each provider's current documentation before you rely on them.

Table: The same concepts on other platforms
| Concept | Claude API (this book) | OpenAI API | Google Gemini API | Open source |
| --- | --- | --- | --- | --- |
| Tool calling (Chapter 2) | `tools` with `input_schema`; `tool_use` and `tool_result` blocks | Function calling: `function_call` and `function_call_output` items (Responses API) | Function calling | Tool calling in Ollama and vLLM, through OpenAI-compatible APIs |
| Controlling tool choice (Chapter 3) | `tool_choice`: `auto`, `any`, a named tool or `none` | `tool_choice`: `auto`, `required`, `none` or a named function | A function-calling mode setting | `tool_choice` in vLLM's OpenAI-compatible server |
| Structured outputs (Chapter 3) | JSON Schema output format; strict tools | Structured outputs with a JSON schema | Structured output with a JSON schema | Ollama's `format` with a JSON schema; vLLM structured outputs |
| Reasoning controls (Chapter 4) | Adaptive thinking and `effort` | `reasoning.effort` | Thinking settings, which vary by model | Ollama's `think` option; reasoning parsers in vLLM |
| Prompt caching (Chapter 16) | `cache_control` breakpoints, or automatic caching | Automatic caching, with an optional cache key | Implicit (automatic) and explicit context caching | Prefix caching in inference servers such as vLLM |
| Many tools: tool search (Chapter 3) | Tool search tool with `defer_loading` | Tool search with deferred loading | No direct equivalent found | Build it: search your own tool catalog (section 30.9) |
| Code execution (Chapter 16) | Code execution tool; programmatic tool calling | Code Interpreter tool | Code execution tool | Your own sandbox (Chapter 10) |
| Computer and browser use (Chapter 23) | Computer use and browser use tools | Computer use tool | Computer Use tool | Playwright and your own harness (Chapter 23) |
| Batch processing (Chapter 27) | Message Batches API | Batch API | Batch API | Offline batch inference in vLLM |
| Token counting (Chapter 16) | Token counting endpoint | Input token counting endpoint | Token counting method | Token counts returned with each response |
| MCP (Part 5) | MCP connector in the API; Claude apps are MCP hosts | Remote MCP servers as a tool | Remote MCP support | The MCP SDKs; LangChain MCP adapters; MCP gateways |
| Agent runtimes (Chapter 24) | Claude Agent SDK; Claude Managed Agents | Agents SDK; AgentKit | Agent Development Kit (ADK); Agent Engine | LangGraph, self-hosted or managed |
| Agent-to-agent (Chapter 21) | Through the A2A SDK, not an API feature | Through the A2A SDK | A2A support in Agent Engine; A2A began at Google and is now a Linux Foundation project | The `a2a-sdk` package; A2A endpoints in LangGraph's agent server |

When you read a chapter, keep three layers apart: the **concept** (tool calling), the **implementation** you run (the Claude API, or the local model through the kit's adapter) and the **equivalent** on the platform you use at work. Chapter 24 shows one agent on several runtimes, and section 24.6 shows the same loop on another provider's SDK.
