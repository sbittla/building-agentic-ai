# Appendices

Reference material for when you need a fact quickly. Keep it open while you work; there's no need to read it in order.

## Appendix A: Running the Course Kit with Docker

Every exercise runs in the course kit's Docker image: you type commands on your computer, and Docker runs them against your `workspace` folder. On Windows, use `.\course.cmd` wherever this book shows `./course.sh`.

### What your computer needs

Table: What your computer needs, by model
| | Claude | Free local model |
| --- | --- | --- |
| Software | Docker Desktop (Windows, macOS) or Docker Engine with Compose (Linux) | The same |
| Memory (RAM) | 16 GB recommended | 16 GB minimum, 32 GB recommended |
| Disk | About 15 GB for the image and data | About 25 GB: the image, data and the 6.6 GB model |
| Graphics card | Not needed | Optional: an NVIDIA GPU with 8 GB or more makes it fast |
| Network | To build the image once, then to reach the Claude API | To build the image and download the model once; then none |
| Money | An API key with a few dollars of credit; about {{cost:learner}} for the whole book | Nothing |

You can start with no model: the quick start, the self-test and the 100-plus *No model* exercises need neither a key nor the download.

:::warn Before you start: can this computer run Docker?
- **Installing** Docker Desktop needs administrator rights; on a work laptop, ask IT first.
- **Windows** needs WSL 2 and hardware virtualization switched on (the installer checks both).
- **Licensing:** Docker Desktop is free for personal use, education and small businesses; larger companies need a paid subscription.
- **No Docker possible?** Use a cloud environment that includes Docker, such as GitHub Codespaces.
:::

:::tip If the first commands fail
- **"Docker is not running"**: start Docker Desktop and wait until it says it's running.
- **`check --api` shows `AuthenticationError`**: the key in `.env` is missing or mistyped; run `./course.sh setup` again.
- **"Can't reach the local model"**: run `./course.sh local up`, then `./course.sh local status`.

Appendix B has the full list.
:::

### What's in the kit

Table: Files and folders in the kit
| File or folder | Purpose |
| --- | --- |
| `Dockerfile` | Builds the image: Ubuntu 24.04, Python 3.12, Node.js 24, the MCP SDK and Inspector, reference servers, GitHub's server, the Claude Agent SDK, LangChain, FastAPI and a small embedding model |
| `compose.yaml` | The `course` service, the network-less `sandbox`, and for the local model `local-model` (Ollama) and `local-adapter` |
| `compose.gpu.yaml` | Adds an NVIDIA GPU to the local model (`./course.sh local up --gpu`) |
| `course.sh`, `course.ps1`, `course.cmd` | The launchers for macOS/Linux and Windows |
| `.env.example` | Template for your `.env` (API key or `PROVIDER=local`, model, GitHub token) |
| `workspace/` | Created on first run: your copy of the kit's code and sample data, where everything you write lives |
| `solutions/` | Solutions for every exercise, sample answers for concept exercises, and the reference capstones |

### Commands

Table: Course kit commands
| Command | What it does |
| --- | --- |
| `./course.sh setup` | First-time setup: checks Docker, creates `.env`, asks for your model (and Claude API key), generates Chapter 30's secrets |
| `./course.sh build` | Build (or rebuild) the image |
| `./course.sh selftest` | Free offline check of the whole setup |
| `./course.sh check --api` | Show installed tools and make one tiny model call |
| `./course.sh check <id>` | Check an exercise answer (Chapter 0, the interludes and 3.3) |
| `./course.sh list [chapter]` | List exercises (`list 4`; interludes are `list P`, `T`, `R`, `S` and `A`) |
| `./course.sh ex <id> [--info]` | Show an exercise and run it |
| `./course.sh ask <module> ["question"]` | Chat with a chapter's tools, e.g. `ask ch08_sql_tools` |
| `./course.sh python <file.py>` / `pytest <path>` | Run a workspace file, or tests |
| `./course.sh shell` | Open a terminal inside the container |
| `./course.sh data <kind>` | Regenerate `notes`, `library`, `messy`, `repo` or `db` sample data (`--count`, `--out`, `--fresh`) |
| `./course.sh reset <file>` | Restore an original kit file |
| `./course.sh solution <id>` | Show the solution for an exercise |
| `./course.sh check-solutions` | Run every solution and capstone offline, free |
| `./course.sh live-check [part]` | Run every chapter's main file against the model; writes `live_report.md` (about $1 on Claude) |
| `./course.sh live-check exercises [chapter]` | Run every model exercise's reference solution; writes `live_exercises_report.md` |
| `./course.sh local up [--gpu\|--native]` | Start the free local model, downloading `qwen3.5:9b` the first time (Appendix H) |
| `./course.sh local status` / `down` | Check the local model is running and downloaded, or stop it to free memory |
| `./course.sh capstone <1-7> [args]` | Run a reference capstone, creating its sample data |
| `./course.sh inspector <server.py>` | MCP Inspector web UI at http://localhost:6274 |
| `./course.sh serve <server.py>` | MCP server over HTTP at http://localhost:8000/mcp |
| `./course.sh desktop-config` | Print the Claude Desktop config for your server |
| `./course.sh mcp python <server.py>` | Run a stdio MCP server for any MCP host |
| `./course.sh serve-api` | The Chapter 30 agent API at http://localhost:8080 (docs at `/docs`) |
| `./course.sh serve-mcp` | The Chapter 30 token-protected MCP server at http://localhost:8000/mcp |
| `./course.sh serve-a2a` | The Chapter 21 A2A analyst agent; card at http://localhost:9999/.well-known/agent-card.json |
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

The `course` container can reach the internet (the model API, Open-Meteo, web pages for the Fetch server). The `sandbox` container, where Chapter 10 runs model-written code, has **no network**, no API keys and a read-only file system outside the workspace. Published ports (6274–6275 for the Inspector, 8000 for MCP over HTTP, 8080 for the agent API) are bound to 127.0.0.1, so only your computer can reach them.

`serve-api`, `serve-mcp` and `serve-a2a` run in containers named `agentic-ai-api`, `agentic-ai-mcp` and `agentic-ai-a2a`, which other kit containers reach by name: `ch30_client.py` finds the first two itself, and `ch21_a2a_client.py --url http://agentic-ai-a2a:9999` reaches the third. Your `.env` is read by Docker Compose and never copied into the image.

## Appendix B: Troubleshooting

First, the most common errors. Then a playbook for the harder case: the agent runs, but does the wrong thing.

Table: Common errors and how to fix them
| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `AuthenticationError` or 401 | API key not set in this shell | Export `ANTHROPIC_API_KEY` again, or load `.env` |
| `NotFoundError` for the model | Model name retired or misspelled | Set `MODEL` to a current name (models overview page) |
| 400 error mentioning `tool_use` ids | A `tool_use` block has no matching `tool_result` | Return a result for every `tool_use` block, in one user message (section 4.3) |
| `AttributeError: ... has no attribute 'text'` on `content[0]` | Current models start the reply with a thinking block | Select blocks by `type` (section 1.1) |
| `stop_reason` is `max_tokens` and there's no answer | Thinking used up a small `max_tokens` | Raise `max_tokens` (2,000 or more); you pay only for what's used (section 4.8) |
| 400 error about `temperature`, prefill or `budget_tokens` | Settings current models no longer accept | Remove them; use instructions, structured outputs and `effort` (sections 3.3 and 4.8) |
| 400 error about `tool_choice` on the newest models | Forced tools aren't allowed on Opus 5.5 and the 5.1 models | Use structured outputs, or a strict tool with `tool_choice` `auto` (section 3.3) |
| 429 rate-limit errors | Too many requests at once | Retry with backoff; lower concurrency (section 29.7) |
| Image build fails on `ghcr.io/github/github-mcp-server` | Your network blocks ghcr.io | Add `GITHUB_MCP_IMAGE=nogithub` to `.env` and rebuild (only 14.3, 14.4 and Capstone 4 need it) |
| Port 6274 or 8000 is already in use | Another program, or an Inspector you didn't stop | Stop it (Ctrl+C), or change the left-hand port in `compose.yaml` |
| A kit file is broken beyond repair | Edits went wrong | `./course.sh reset <file>`; your version is kept as `.bak` |
| MCP server "disconnected" right away | A crash at start-up, or (outside Python's SDK) output written to stdout | Run the server by itself to see the error; log to stderr |
| Claude Desktop doesn't show your tools | Wrong path in the config, or the app wasn't restarted | Use absolute paths; fully quit and restart the app |
| `Couldn't reach the agent API` (Chapter 30) | `serve-api` isn't running | Run `./course.sh serve-api` in another terminal |
| "... needs Claude, not the local model" | A **Claude only** exercise run with `PROVIDER=local` | Set `PROVIDER=claude` and add an API key with credit; this is paid usage (Appendix H) |
| "This exercise needs GITHUB_PERSONAL_ACCESS_TOKEN" | Exercises 14.3 and 14.4 use your own GitHub account | Add a read-only, fine-grained token to `.env`; it costs nothing |
| "This exercise needs the isolated test sandbox" | Exercise 10.7 runs code in the network-less sandbox | Run `./course.sh sandbox up` first |

Some of these aren't bugs: the exercise needs something your setup doesn't have yet. Before you debug, read the exercise's label with `./course.sh ex <id> --info`. Of the {{exercises:all}} exercises, {{exercises:none}} need no model, {{exercises:any}} run free on `qwen3.5:9b`, the {{exercises-word:claude-rec}} **Claude recommended** ones also run free but work much better on paid Claude, and the {{exercises-word:claude-only}} **Claude only** ones need paid Claude usage or, for 12.5, the Claude Desktop app. Appendix H's *Which exercises need which model* lists them, with the few that need an account, an app or a person.

### When your agent doesn't work: a debugging playbook

Most agent bugs aren't crashes: the agent runs, then does the wrong thing. Work through these steps in order; most problems turn up by the third.

1. **Read the trace, not the answer.** Print every model call, tool call and result (Chapter 4's `verbose=True`, or Chapter 28's spans). The trace shows *where* it went wrong.
2. **Check the stop reason.** `max_tokens`: the reply was cut off. `refusal`: the model declined. `max_iterations`: a tool keeps failing or the model can't see how to finish (Chapter 4's `next_action` names each case).
3. **Run the tool by itself** with the exact arguments from the trace. If it fails or returns something confusing on its own, the model isn't the problem.
4. **Read the tool result as the model does.** Is it too long, is the key fact buried, does an error say how to fix the call? Shorten it and put the answer first (Chapters 2, 3 and 6).
5. **Check the description.** Would a new colleague know *when* to call this tool from the description alone? Most wrong-tool bugs are description bugs (section 3.2).
6. **Shrink the context.** Try the question in a fresh conversation; if it works there, you have a context problem (Chapter 16).
7. **Turn the bug into a test case.** Add the failing question to your evaluation suite (Chapter 27), fix it, and run the suite several times: a fix that works once may not hold.

Table: Symptoms and where to look first
| Symptom | First place to look |
| --- | --- |
| Answers without calling a tool it should use | The tool description (section 3.2); a "no tool" eval case (section 3.4) |
| Calls the wrong tool | Overlapping descriptions; merge or rename tools (Chapter 3) |
| Invents a value it should ask for | Ambiguity handling (section 7.4), or elicitation for MCP servers (exercise 13.7) |
| Repeats the same failing tool call | The tool's error message: does it say how to fix the call? (section 2.6) |
| Works in testing, fails for real users | Several trials of the eval suite; the production model name and limits (Chapter 27) |
| Gets slower and more expensive over a session | Context growth: trimming, compaction and caching (Chapter 16) |
| Follows instructions hidden in a web page or file | Prompt injection: the policy layer (Chapter 14), and guards and quarantined reading (Chapter 25) |
| Works locally, fails once deployed | The smoke test, secrets and instance limits (section 30.6) |

## Appendix C: Glossary

Table: Glossary
| Term | Meaning |
| --- | --- |
| A2A (Agent2Agent) | An open protocol for independent agents to find each other and hand off tasks; complements MCP (section 21.7) |
| Acceptance criteria | Thresholds a customer signs before a pilot, applied by a gate in code (section 31.5) |
| Adaptive thinking | The model decides how much to reason before each step; on by default on current Claude models |
| Agent | An LLM that chooses and calls tools in a loop until a task is done |
| Agent architecture reference model | The layers of every agent system, with evaluation and observability across them (section 1.7) |
| Agent card | An A2A agent's public JSON description, at `/.well-known/agent-card.json` |
| Agent engineering lifecycle | Decide; design, build, secure, evaluate, optimize, deploy, operate, improve; retire (section 1.10) |
| Agent improvement loop | Failures become eval cases; each change passes evaluation, shadow and canary (section 30.14) |
| Agent inventory | One record per agent: owner, model, tools, data, risk tier and version (section 30.12) |
| Agent risk model | Risk = capability × autonomy × access × persistence × blast radius (how much damage it can do), each 1–3 (section 25.11) |
| Agent SDK | The Claude Agent SDK: the runtime behind Claude Code, as a library |
| Agent Skill | A folder with a `SKILL.md` and optional files, loaded only when needed |
| Agent version | Model id, prompt, tools, skills, policies and eval suite, released together (section 30.13) |
| Agentic search | Finding information by letting the model list, search and read |
| Approval gate | Code that asks a human before a risky tool runs |
| Architecture decision record (ADR) | A short record of one design decision and its evidence (Appendix K) |
| Audit log | An append-only record of every action an agent took |
| Blackboard (shared board) | A team's shared task record; agents read it, only the orchestrator writes |
| BM25 | A classic keyword-ranking formula that weights rare words more |
| Break-even value | What a right answer must be worth for a team to pay off (section 21.10) |
| Business case | Monthly cost against the human baseline, with payback and assumptions |
| Cache hint (MCP) | `ttlMs` and `cacheScope`: how long, and for whom, a client may reuse a list result |
| Canary release | Sending a small share of traffic to a new version and comparing SLOs |
| Cascade | Trying a cheaper model first, escalating only when a check fails |
| Checkpoint | A step's saved status and result, so a crashed job can resume |
| Compaction | Replacing older turns with a summary to save context |
| Compensation | Undoing completed steps, newest first, when a job is abandoned |
| Computer-use agent | An agent that operates a web page or desktop instead of an API |
| Confidence interval (95%) | The range that very likely contains the real pass rate (measurement interlude) |
| Content block | One part of a model message: text, `tool_use` or `tool_result` |
| Context engineering | Choosing what goes into the model's context on each call |
| Context window | The maximum tokens a model can consider in one call |
| Continuous profiler | An always-on sampler showing where production code spends its time |
| Contract (between agents) | A schema for what one agent hands another, checked in code |
| Coordinated omission | Measuring latency only after a request gets service, hiding queueing time |
| Coordination overhead | What a team adds over one agent: calls, context, messages, waiting, failures (section 21.10) |
| Descriptor (capability) | The signed, hashed record of a discovered server, agent or skill |
| Deterministic control plane | Code that enforces identity, policy, budgets, approvals and audit; the model only proposes (section 22.1) |
| Deterministic shell | A workflow in code, with model calls only at chosen steps |
| Dimensions of agency | The nine properties that make a system more or less agentic (section 1.4) |
| Discovery | Finding capabilities at run time; finding one is not trusting it |
| Durable execution | Running a job so its progress survives crashes and restarts |
| Effort | A request setting (`low` to `max`) trading quality for cost and speed |
| Elicitation | An MCP feature that lets a server ask the user for missing input mid-call |
| Embedding | A vector representing a text's meaning; similar texts get similar vectors |
| Episodic, semantic and procedural memory | Long-term memory of events, facts and skills |
| Error budget | How much failure an SLO allows over a window |
| Evaluation (eval) suite | Test cases with checks, run after every change |
| Exfiltration | Getting private data out, for example inside a URL the agent fetches |
| Explicit delegation | Handing another agent a narrower token naming who delegated what |
| Extension (MCP) | An optional protocol feature used only when both sides declare it |
| Failure taxonomy | The 12 classes of agent failure (section 28.8; Card 5) |
| Flaky case | A case that passes on some runs and fails on others: the agent is guessing |
| Forward-deployed engineer (FDE) | An engineer who ships inside one customer's business until it delivers (Chapter 31) |
| Gateway (MCP) | A server in front of MCP servers that filters tools, checks tokens and audits (section 30.9) |
| Goodput | Successful tasks per second; unlike throughput, it ignores failures |
| Harness | The code around the model (loop, tools, checks, limits) that decides what's allowed |
| Host | The application that runs the model and connects to MCP servers |
| Human baseline | What the work costs today with people doing it |
| Idempotency key | A stable key sent with a side effect so the receiver ignores repeats |
| Idempotent | Safe to repeat: calling twice has the same effect as once |
| JSON Schema | A standard way to describe the structure of JSON data |
| Knee (of a load curve) | The load where throughput stops rising and latency climbs |
| Lease | A time-limited claim on a job; when it expires, another worker may take it |
| Lethal trifecta | Private data + untrusted content + a way out: together, an agent can be made to leak |
| LLM (large language model) | A model trained on huge amounts of text to predict the next token |
| Managed agent | An agent whose loop and sandbox run on the provider's servers |
| MCP | Model Context Protocol: an open standard connecting AI applications to tools and data |
| MCP Apps | An MCP extension that lets a tool show an interactive interface in the chat |
| MCP client | A connection inside a host to one MCP server |
| MCP server | A program that offers tools, resources and prompts over MCP |
| Model routing | Choosing which model handles each task or step |
| Multi round-trip request | Since MCP 2026-07-28: a tool asks for input and the client calls again with it |
| Orchestrator–worker | A lead agent that delegates subtasks to parallel subagents |
| Output guard | A code check on model output, with a safe fallback |
| OWASP Agentic Top 10 | OWASP's ten most critical security risks of agentic applications (ASI01 to ASI10) |
| p50 / p95 | The latency that 50% / 95% of requests beat |
| Pass rate | The share of runs that pass; report it with its interval |
| Pass^k | The share of cases that pass on all k repeated runs |
| Payback period | Build cost ÷ net monthly saving |
| Plan (as data) | Steps, tools and done conditions that code checks before running |
| Problem brief | The output of discovery: users, job, metric, baseline, target, owner, constraints (section 31.2) |
| Programmatic tool calling | The model writes a program that calls your tools in a sandbox |
| Progressive discovery | Offering tools through search instead of all at once |
| Prompt (MCP) | A reusable prompt template a server exposes |
| Prompt caching | Reusing an unchanged prompt prefix at a tenth of the input price |
| Prompt injection | Text in data that tries to give the model instructions |
| Provenance (memory, skill) | Where a memory or skill came from and who vouched for it |
| Quality scorecard | The eleven qualities a release is judged on (section 27.6; Card 6) |
| RAG | Retrieval-augmented generation: fetch relevant chunks, then call the model |
| Rate limit | A cap on a caller's requests per period (HTTP 429 when exceeded) |
| Recall@k / MRR | Is the right document in the top k, and how high does it rank |
| Reciprocal rank fusion | Merging rankings by adding 1/(60 + rank) per result |
| Resource (MCP) | Read-only data a server exposes by URI |
| Risk tier | How much harm an agent could do, setting the review it needs |
| Rollback | Switching traffic back to the previous version by configuration |
| Routing | A cheap decision before an expensive one: a tool, agent, context source or model |
| Scorecard (agent) | One table of a release's quality, safety, cost and latency, compared with the last |
| Server tool | A tool that runs on the provider's servers, not in your code |
| Shadow mode | Running a new version on copied traffic without showing or acting on its output |
| Skill registry | A catalog of versioned skills with permissions, trust and rollback |
| SLO (service-level objective) | A target for measured behavior, such as task success ≥ 95% over 30 days |
| Smallest valuable slice | The first piece to ship: most metric movement for least effort and risk (section 31.3) |
| SSE (Server-Sent Events) | A server streaming events to a client over one HTTP response |
| SSRF | Server-side request forgery: tricking a server into fetching an internal address |
| Stateless protocol | Each request carries everything needed, so any server copy can answer |
| stdio / Streamable HTTP | The two standard MCP transports: local subprocess or web service |
| Stop reason | Why the model stopped: `end_turn`, `tool_use`, `max_tokens` and others |
| Structured outputs | An API feature that makes the reply match a JSON Schema |
| System prompt | Instructions that set the model's behavior for a whole conversation |
| Tasks (MCP) | An MCP extension for long calls: the client polls a task id with `tasks/get` |
| Thinking block | The model's reasoning before its answer; send it back unchanged |
| Token | A chunk of text the model reads or writes; the unit of cost |
| Token bucket | A rate limit where each caller's bucket refills steadily and each request takes a token |
| Tool | A function the model can ask your code to run, with a name, description and schema |
| Tool search | Deferring most tool definitions and letting the model search for what it needs |
| Trace | The step-by-step record of one agent run |
| Trust store | Which organizations and keys you trust, for what, until when |
| Workflow | A fixed sequence of LLM calls and code, with steps set by the developer |
| Working memory | What the agent holds during one task; also called short-term memory |

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

Every cost figure in this book and the kit's README comes from one cost model, `dev/cost_model.py`, which also writes the kit's `COST_MODEL.md`. It assumes Claude Sonnet 5 at $2 per million input tokens and $10 per million output tokens (2026 prices), and an *agent run* (one task) of 3–4 model calls with 2,500–3,000 input and 500–700 output tokens per call: about {{cost:run}}. Most paid exercises make one run; evaluation suites, benchmarks and load tests make dozens. One clean pass of every paid exercise is {{cost:first}}; since you'll rerun while debugging, the table doubles that.

Three more assumptions sit behind the table. It prices every exercise that calls a model as if you ran it on Claude, including the ones that also run free on the local model; the Claude Desktop exercise (12.5) uses the app's own plan and isn't counted. It assumes no prompt caching, which would lower the input term. And it counts each model call once, with no automatic retries by the client (section 19.4): the doubling stands for your own repeated attempts while debugging, not for those.

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
| 10. In the field | 1 | 1 | $0.06–0.10 | — |
| **All chapters** | **118** | **939** | **About $55–100** | First pass alone: $28–49 |
| Each capstone | — | about 120 | $7.2–12 | Evaluation runs and a load test |
| Cloud deployment (30.7) | — | — | Usually $0 on a free tier | The host's own charges; set a budget alert and delete the service afterward |

Claude Sonnet 5's tokenizer counts up to about 35% more tokens than earlier models, depending on the content, and thinking is billed as output, so measure your own runs rather than reuse old token counts. Claude Haiku 4.5 ($1 input, $5 output per million tokens) roughly halves the totals, and prompt caching (Chapter 16) and smaller tool outputs cut them further.

**Or pay nothing:** with the free local model (`PROVIDER=local`, Appendix H), every exercise except the {{exercises-word:claude-only}} marked **Claude only** costs nothing. A sensible plan: do the book locally, and buy a few dollars of Claude credit for those {{exercises-word:claude-only}} and the {{exercises-word:claude-rec}} marked **Claude recommended**. On Claude throughout, try the table's biggest items on the local model or Haiku first.

### Estimate a run yourself

```
cost ≈ (input tokens × input price + output tokens × output price) ÷ 1,000,000
```

Every agent in this book reports its tokens, and Chapter 16's `cost()` function applies this for you, including cached tokens.

## Appendix F: The Solutions Folder

The `solutions` folder sits next to `course.sh`. The container mounts it read-only at `/solutions`, so you can't change it by accident.

Table: What's in the solutions folder
| Path | What it holds |
| --- | --- |
| `exercises/ch<NN>/`, `exercises/interlude_*/` | One folder per chapter or interlude with the programs that solve its exercises, such as `ch04/ex4_4_tracer.py` |
| `sol_chNN_*.py` (in those folders) | An improved chapter file that solves exercises, such as `sol_ch08_sql_tools.py` for 8.5 and 8.6 |
| `*.json`, `*.jsonl` (in those folders) | Extra configuration and evaluation data, such as `servers_remote.json` (30.5) and `eval_sql_more.jsonl` (27.3) |
| `ANSWERS.md` | Written answers for concept exercises, and *what you should see* for exercises that run a chapter file |
| `tests/test_ex*.py` | Solutions that are themselves tests (T.2–T.4, 6.3, 9.6, 12.7, 16.6) |
| `tests/test_ch*.py`, `tests/test_capstones.py` | The checks behind `check-solutions`; examples of testing agents with a scripted model |
| `capstones/common.py` | The shared host for all capstones: MCP hub, policy layer and approvals |
| `capstones/c1_support/` … `c7_engagement/` | The seven reference capstones (see the end of each capstone) |
| `SOLUTIONS.md` | Every exercise with its solution file and what it shows |
| `index.json` | Which files solve which exercise; `./course.sh solution` reads it |

### Running a solution yourself

Solutions build on the chapter files, so run them from your workspace with the solutions on Python's path:

```bash
./course.sh shell
export PYTHONPATH=/solutions/exercises/ch04:/solutions/exercises:$PYTHONPATH
python /solutions/exercises/ch04/ex4_4_tracer.py
```

To use a solution as a starting point, copy it into `workspace/exercises` and edit the copy.

### How the solutions are verified, and what that does and doesn't prove

Two kinds of evidence back the solutions, kept apart.

**Deterministic checks.** `./course.sh check-solutions` runs every reference solution, capstone and exercise command against a scripted stand-in model, with no API key. It gives the same result on any machine, so it proves the code runs and the checks pass, not that a real model will choose the same way. Every push runs it on GitHub, and `python dev/verify.py` records the result, commit, `requirements.lock` hash and environment in `verification/offline.json`. A test that needs a program only the image has is reported as *skipped, needs …*, never as a pass.

**Runs with a real model.** `./course.sh run-chapter` runs each exercise's reference solution with the local model or Claude, recording model, commit and package versions in each chapter's `summary.json`. A pass shows the exercise works end to end, not that it always will; that's what repeated trials are for.

The README's *Verified results* section shows both, with each outcome counted separately, and each tagged release carries its results as files.

## Appendix G: Where to Learn More

Nobody learns this field from one book. Here's where to get help, free courses that complement this one, and how to keep up. `RESOURCES.md` in the kit has the full lists from every chapter's **Learn more** section, with links checked weekly.

### When you're stuck: where to ask

Search the exact error first. When you ask, include your code, the full error and what you expected, and never your API key or `.env`.

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

Model names, prices and SDK features change every few months. First check that your book, code and environment match:

Table: This edition and the code it was tested with
| Book | Repository tag | Exercises | Python | Default models | MCP specification | Verified |
| --- | --- | ---: | --- | --- | --- | --- |
| First edition | `book-v1.0.0` | {{exercises:all}} | 3.12 | `claude-sonnet-5`, `claude-haiku-4-5`, `qwen3.5:9b` | 2026-07-28 | October 2026 |

`git describe --tags` prints your tag, and `./course.sh check` prints the image's Python and library versions. The *Verified* column has a narrow meaning, explained at the end of this appendix. Four kit files track later changes:

Table: How the course kit tracks change
| File | What it tells you |
| --- | --- |
| `VERSION_MATRIX.md` | The exact tested versions of every library, server, model and protocol, and which sections depend on them; also how to tell a protocol change (behavior differs) from an SDK change (code breaks) |
| `CHANGELOG.md` | What changed between tags of the repository |
| `MIGRATION.md` | What to change in your own code when you move to a newer tag |
| `ERRATA.md` | Corrections for this edition; its tag never moves, so its code always matches your book |

Changes in the wider world appear first on these pages:

Table: Where changes appear first
| Resource | What you'll find | Level |
| --- | --- | --- |
| **Claude Platform release notes**<br>[platform.claude.com/docs/en/release-notes/overview](https://platform.claude.com/docs/en/release-notes/overview) | New models, API features and deprecations, as they ship | Start here |
| **Claude docs: Models overview**<br>[platform.claude.com/docs/en/models/overview](https://platform.claude.com/docs/en/models/overview) | Current model names and prices; check before changing MODEL in .env | Start here |
| **Anthropic Engineering blog**<br>[anthropic.com/engineering](https://www.anthropic.com/engineering) | In-depth posts on agents, tools, evals and context | Go deeper |
| **MCP blog**<br>[blog.modelcontextprotocol.io](https://blog.modelcontextprotocol.io) | Protocol changes and new specification versions | Go deeper |
| **Simon Willison's weblog**<br>[simonwillison.net](https://simonwillison.net) | A well-known independent developer's daily notes on LLMs and agent security | Go deeper |
| **MCP roadmap**<br>[modelcontextprotocol.io/development/roadmap](https://modelcontextprotocol.io/development/roadmap) | The protocol's priorities and upcoming changes | Go deeper |

### What "verified" means

"Verified" in this appendix's edition table covers two kinds of evidence, and leaves out a third that only you can produce. Keep them apart when you read a result or quote one:

1. **Deterministic tests with a scripted stand-in model.** `./course.sh check-solutions` replays fixed model replies, so it runs offline, needs no key and gives the same result on every machine. It proves that the code paths and the controls work: the approval gate stops an unapproved call, the policy refuses a hidden tool, the checkpoint skips a finished step. It says nothing about whether a real model will make the same choices. The record of each run, with its commit and environment, is `verification/offline.json`.
2. **Live-model exercise runs**, on the free local model or on paid Claude. `./course.sh run-chapter <chapter|all>` runs each exercise's reference solution against a real model and writes its logs and a `summary.json` to `solutions/outputs/`. These results vary from run to run, because the model does; a pass shows that the exercise can work end to end, and repeated trials (Chapter 27) tell you how often.
3. **Production readiness.** The kit doesn't provide it, and no number in this book claims it. It takes your own evaluation suite on your own data, a load test at your expected peak, a security review and someone to operate the system. Appendix M lists what that involves.

Appendix F describes how the first two are run for the solutions folder.

## Appendix H: Run the Book Free with a Local Model

You don't have to pay for API calls to learn from this book. The kit can run an open-source model, **`qwen3.5:9b`**, in a Docker container on your computer, and the book's code uses it unchanged. If a command here doesn't work, check the kit's **`LOCAL_MODEL.md`** (github.com/sbittla/building-agentic-ai/blob/main/LOCAL_MODEL.md) for updates.

### Why qwen3.5:9b

Agents live or die by tool calling, and among open models small enough for an ordinary computer, the Qwen 3.5 family scores at the top (the 9B model scores 66.1 on BFCL-V4 and 79.1 on TAU2-Bench, ahead of much larger older models). It's a 6.6 GB download and needs roughly 10–12 GB of memory with a 32k-token context, so it fits a 16 GB machine. It runs on an NVIDIA GPU with 8 GB or more, or more slowly on the CPU. It's Apache 2.0 licensed, and it thinks before answering, like Claude, so the lessons about thinking blocks still apply.

### What you need

Table: Hardware for the local model
| | Minimum | Recommended |
| --- | --- | --- |
| Memory (RAM) | 16 GB | 32 GB |
| Free disk space | 10 GB | 15 GB |
| GPU | None (CPU works) | NVIDIA with 8 GB or more of video memory |

On **Windows**, WSL 2 usually gets half your RAM, which is enough; if the model runs out of memory, put the two lines `[wsl2]` and `memory=12GB` in `.wslconfig` in your user folder, run `wsl --shutdown`, and restart Docker Desktop. On **macOS**, Docker can't use the GPU, so on Apple Silicon install Ollama as a Mac app instead ("On a Mac" below). On **Linux**, an NVIDIA GPU needs the NVIDIA Container Toolkit.

### Set it up (about 15 minutes, plus the download)

1. Run `./course.sh setup` and choose option **2**, or add `PROVIDER=local` to `.env`.
2. Start the model server (the first run downloads the model):

```bash
./course.sh local up          # Windows: .\course.cmd local up
./course.sh local up --gpu    # the same, using an NVIDIA GPU
```

3. Check that it answers:

```bash
./course.sh local status      # the model server is running and qwen3.5:9b is downloaded
./course.sh check --api       # one tiny call: the reply comes from qwen3.5:9b
```

Every `./course.sh` command now uses the local model. It stays loaded for 30 minutes after its last use; `./course.sh local down` frees the memory, and the download stays in a Docker volume.

**On a Mac (faster):** install Ollama from ollama.com, run `ollama pull qwen3.5:9b`, and set the context length to 32k in its settings. Add `PROVIDER=local` and `OLLAMA_URL=http://host.docker.internal:11434` to `.env`, then run `./course.sh local up --native` to start only the kit's adapter.

### Switching between Claude and the local model

One line in `.env` decides which model every command uses:

Table: Choosing the model in `.env`
| `.env` line | Model |
| --- | --- |
| `PROVIDER=claude`, or no `PROVIDER` line | Claude, through the Claude API, with your `ANTHROPIC_API_KEY` |
| `PROVIDER=local` | `qwen3.5:9b` on your computer; no key needed |

Switch whenever you like; `./course.sh check` shows which is active. Two other settings help on small machines: `LOCAL_CONTEXT=16384` when memory is short, and `LOCAL_THINKING=off`, much faster on a CPU and a little less accurate.

### What the kit does for you

Ollama speaks Claude's Messages API for messages, tools, streaming and thinking. For the few features it lacks, a small **adapter** (`course/local_adapter.py`) fills the gap so your code doesn't change:

Table: What the local-model adapter does
| Claude feature | Chapters | What the adapter does |
| --- | --- | --- |
| Forcing a tool (`tool_choice`) | 3, 11, capstones 3, 4 and 5 | Tells the model to call the tool, and asks again (up to twice) if it answers in text |
| Structured outputs (`output_config` with a JSON schema) | 3, 4, 11, 18, 20, 25, 27 | Turns the schema into a tool, validates the answer and returns it as JSON text |
| Prompt caching (`cache_control`) | 16 | Removes it: the code runs, but exercise 16.5 shows no savings |
| Counting tokens | 16 | Returns an estimate (about four characters per token) |
| Server-side features: tool search, code execution, Agent Skills, Managed Agents | 3, 16, 18, 24 | Returns a clear error saying the exercise needs Claude |

At about 300 lines, the adapter is worth reading after Chapter 11 as a real example of the model-provider layer in section 24.6.

### What to expect

The local model is a capable learning partner, but it isn't Claude. It picks the wrong tool more often, gives up on self-correction sooner (Chapters 8 and 10) and scores lower on evaluations. That's a lesson in itself: the evals in Chapters 3, 8 and 27 measure exactly this gap.

Table: Local-model speed by hardware
| Setup | A short answer | A typical agent exercise (3–6 model calls) |
| --- | --- | --- |
| NVIDIA GPU with 8 GB or more | 1–3 seconds | 10–40 seconds |
| Apple Silicon Mac with Ollama as an app | 2–5 seconds | 20–60 seconds |
| CPU only | 10–30 seconds | 1–5 minutes |

The first call after `local up` is slower while the model loads. On a CPU, set `LOCAL_THINKING=off`, run evaluations with one trial instead of three, and shrink the load tests (exercises 29.2 and 29.6) to, say, 3 users for 1 minute; queueing still shows clearly.

### When something goes wrong

Table: Local-model problems and fixes
| Symptom | Fix |
| --- | --- |
| "Can't reach the local model" | Start it: `./course.sh local up`. Check with `./course.sh local status`. |
| The model stops, or Docker says it ran out of memory | Close other programs, set `LOCAL_CONTEXT=16384`, or give Docker more memory (Windows: see `.wslconfig` above). |
| Very slow | Use `--gpu` if you have an NVIDIA GPU; set `LOCAL_THINKING=off`; see the speed tips above. |
| 8 GB GPU: the model loads partly on the CPU, or fails with "cudaMalloc failed: out of memory" | Set `LOCAL_CONTEXT=8192`: the weights and a 32K context don't both fit. With the smaller context, keep big tool results short (Chapter 16). |
| Windows + GPU: loading fails with "out of memory" though nothing else uses the GPU | `./course.sh local down`, then `local up --gpu`; if it persists, run `wsl --shutdown` and restart Docker Desktop. |
| "The local model didn't call … correctly after 3 tries" | Run it again (answers vary), make the prompt or tool description clearer (Chapter 3), or use Claude for that run. |

`LOCAL_MODEL.md` covers interrupted downloads, unused GPUs and port clashes.

### Which exercises need which model

Every exercise box shows one of four labels. Of the book's {{exercises:all}} exercises, {{exercises:none}} need **no model**, {{exercises:any}} run on **qwen3.5:9b or Claude**, {{exercises:claude-rec}} are **Claude recommended** and {{exercises:claude-only}} are **Claude only**. `./course.sh list <chapter>` shows the labels, and `./course.sh ex <id>` warns before running a Claude-only exercise locally.

Table: What each exercise needs, and what it costs
| Label | Exercises | Runs free? | Paid usage |
| --- | ---: | --- | --- |
| **No model** | {{exercises:none}} | Yes, with no model at all | Never |
| **qwen3.5:9b or Claude** | {{exercises:any}} | Yes, on `qwen3.5:9b` | Only if you choose Claude |
| **Claude recommended** | {{exercises:claude-rec}} | Yes, on `qwen3.5:9b`, with weaker results | Optional, for much better results |
| **Claude only** | {{exercises:claude-only}} | No (12.5 aside, below) | Required for 3.7, 16.7 and 24.7 |

A few exercises need something besides a model:

- **An app:** 12.5 uses the Claude Desktop app. A free Claude plan works, and no API key or local model is involved.
- **An account:** 14.3 and 14.4 read your own GitHub repositories with a read-only token (free). Exercise 30.7 deploys to a managed container host; most have a free tier, but set a budget alert and delete the service afterward.
- **A person:** exercises with an approval gate stop and wait for you to type *y* or *n*; you're the person in the loop. Exercise 3.1 asks a classmate or colleague to try to break your tool descriptions.

Table: Exercises that need, or work much better with, Claude
| Exercise | Label | Why |
| --- | --- | --- |
| 3.7 Tool search at scale | Claude only | Tool search runs on Anthropic's servers. |
| 12.5 Claude Desktop | Claude only (Claude Desktop app) | Uses the Claude Desktop app; a free plan works. |
| 16.5 Measure caching savings | Claude recommended | Prompt caching exists only on Claude; locally the savings are always zero. |
| 16.7 Let a program do the counting | Claude only | Programmatic tool calling runs code on Anthropic's servers. |
| 24.3 See the approval gate work | Claude recommended | The Agent SDK drives the Claude Code CLI; qwen3.5:9b often stalls. |
| 24.4 Agent SDK with your MCP servers | Claude recommended | As 24.3. |
| 24.5 Same agent, three frameworks | Claude recommended | Includes an Agent SDK version; the other two run well on qwen3.5:9b. |
| 24.6 Write a skill | Claude recommended | Runs through your own loop; the small model often skips a skill it should load. |
| 24.7 A managed analyst | Claude only | Managed Agents are hosted by Anthropic. |
| 21.6 A mixed team | Claude recommended | Several agents, including one over A2A, must follow a multi-step brief. |
| 23.4 The injected note | Claude recommended | Many small web-page steps: where the local model struggles most. |
| 23.5 Verify, don't trust | Claude recommended | As 23.4. |
| 23.6 A queue that survives a crash | Claude recommended | As 23.4. |
| 29.5 Halve the cost | Claude recommended | Cost needs real prices and the model you ship. |

To check your machine, run every model exercise's reference solution:

```bash
./course.sh live-check exercises --yes       # all of them (several hours on a CPU)
./course.sh live-check exercises 4 --yes     # just Chapter 4
```

It writes `workspace/live_exercises_report.md`. **PASS** means the solution ran without errors; read the answers to judge quality.

## Appendix I: Reference Cards

The book's frameworks on a few pages, for design reviews and on-call.

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

Ask: can I draw the flowchart first? What does a wrong step cost? Can I tell when it's done and right? Is the flexibility worth the cost?

### Card 2: The dimensions of agency (section 1.4)

Autonomy, state, planning, tool use, environmental interaction, persistence, feedback, delegation, adaptation. Turn up only what the task needs; each adds a way to fail.

### Card 3: The agent architecture reference model (sections 1.7 and 30.15)

User / API → agent runtime (planning, memory, context, tools, policies) → model → MCP, APIs, A2A → environment, with evaluation and observability across every layer.

### Card 4: MCP, A2A, API or workflow? (section 21.8)

Table: What to use for each need
| You need to... | Use |
| --- | --- |
| Connect a model to a tool or data | A tool; an MCP server to share it |
| Independent agents collaborating across a boundary | A2A |
| One service calling another | An API |
| A deterministic business process | A workflow or state machine |
| A person's decision before acting | Human in the loop |
| Work that takes hours and survives crashes | A durable workflow |
| Search over knowledge | A retrieval system |
| Something local and simple | A plain tool |
| One front door for many tools, with policy | An MCP gateway |

### Card 5: The agent failure taxonomy (section 28.8)

Table: Failure classes and where to look first
| Failure | First place to look |
| --- | --- |
| 1. Wrong tool | Tool descriptions (Chapter 3); trajectory checks (Chapter 27) |
| 2. Wrong arguments | Schemas and validation (Chapter 3); argument checks (Chapter 27) |
| 3. Tool failure | Retries, timeouts and errors as data (Chapters 2, 7, 19) |
| 4. Tool-result misinterpretation | Smaller, clearer results; answer checks (Chapters 8, 27) |
| 5. Hallucination | Grounding and citations (Chapters 6, 18); groundedness checks (Chapter 27) |
| 6. Context overflow | Trimming, compaction, isolation (Chapter 16) |
| 7. Injection (context contamination) | Untrusted-content handling and quarantine (Chapters 14, 25) |
| 8. Planning failure | Plans as data, checked before running (Chapter 20) |
| 9. Infinite loop | Step caps and progress checks (Chapters 4, 10); loop detection (Chapter 28) |
| 10. Memory poisoning | A memory write gate and audits (Chapters 17, 25) |
| 11. Authorization failure | Scoped tokens checked at the tool (Chapter 26) |
| 12. Cost or latency runaway | Budgets in code, SLOs and alerts (Chapters 28, 29) |

### Card 6: The agent scorecard (section 27.6)

**Per run:** success rate · reliability (pass^k) · tool and argument accuracy · task completion · safety violation rate · average steps · p50 and p95 latency · cost per task and per successful task.

**Per release, the eleven qualities:** outcome · trajectory · safety · tool correctness · groundedness · latency · reliability · cost · observability · security · maintainability. Compare each release with the last; safety and security get no slack, and any quality below its floor holds the release.

### Card 7: Agent SLOs (section 28.10)

Example targets to adapt: task success ≥ 95%; p95 latency < 8 s; cost per task < $0.05; tool-selection accuracy ≥ 98%; unsafe-action rate < 0.01%; human-escalation accuracy ≥ 95%; retrieval recall ≥ 90%. Each needs a data source: traces, the eval suite or human review.

### Card 8: The agent performance model (section 29.1)

Total latency = model + tool + retrieval + orchestration + queueing + serialization.
Cost per task = model + tools + retrieval + infrastructure + retries + human review.
Measure at rising concurrency to find the knee: goodput, p50/p95/p99, tokens, cache hit rate, steps, cost and success.
Tasks in flight = arrival rate × latency (Little's law), limited by the scarcest of model slots, rate limits and workers. Report cost per *successful* task.

### Card 9: Durable concepts and fast-changing details

Table: Durable concepts and fast-changing details
| Durable concepts (this book's core) | Fast-changing details (marked **API-dependent**) |
| --- | --- |
| The agent loop, state, tools, context | Model names and prices |
| Evaluation, guardrails, authorization | SDK syntax and API field names |
| Observability, memory, reliability | Framework APIs and managed services |
| Performance and cost engineering | MCP specification versions |

Sections marked **API-dependent** teach a lasting concept with perishable names: take parameter names from current documentation. `VERSION_MATRIX.md` lists them with their tested versions.

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

Real systems combine kinds; name each part's kind to find its controls.

### Card 11: The agent engineering lifecycle (sections 1.10 and 30.13)

Decide once; then design → build → secure → evaluate → optimize → deploy → operate → improve, looping for each version; retire at the end.

Table: Lifecycle stages and when to move on
| Stage | Before you move on |
| --- | --- |
| Decide | You can say why a simpler option won't do |
| Design | Tools, context, rules in code and checks written down; decisions recorded (Appendix K) |
| Build | Each step works and has a test |
| Secure | Threat model, risk tier and its controls, passing regression scenarios |
| Evaluate | A case file, several trials, intervals and a scorecard |
| Optimize | Cost per successful task and p95 within budget, quality unchanged |
| Deploy | CI gate passed, checklist done, shadow and canary planned, rollback ready |
| Operate | Traces, SLOs, alerts, budgets and a named owner |
| Improve | Every failure becomes a case; one change at a time |
| Retire | Kill switch, identity revoked, routes removed, data handled by policy, audit log kept |

### Card 12: The agent risk model (section 25.11)

**Risk = capability × autonomy × access × persistence × blast radius**, each factor scored 1–3, so 1–243.

Table: Risk tiers at a glance
| Tier | Score | Adds (each tier keeps the ones below) |
| --- | --- | --- |
| 1 Low | 1–8 | A named owner, an evaluation suite that gates changes, an audit log |
| 2 Moderate | 9–27 | A threat model, scoped tokens, budgets in code, monitoring and alerts |
| 3 High | 28–81 | Approval gates, a deterministic control plane, regression scenarios, a kill switch; monthly trace review |
| 4 Critical | 82–243 | Isolation, step-up tokens, a red-team run before launch, a security sign-off; weekly trace review |

Any factor at 3 adds its own controls whatever the total. To lower risk, cut a factor (an approval step, narrower access, shorter memory) and re-score. It's a judgment aid, not a probability.

### Card 13: The deterministic control plane (sections 22.1 and 25.11)

The model **proposes**; deterministic code **enforces** identity, policy and permissions, validation, budgets, approvals, state transitions, audit and rollback. The model may choose among allowed tools and propose values, actions and next steps. It never names the user, writes its own audit record or approves its own action, and five decisions are never its own: authorization, security policy, tenant isolation, financial limits and permission for destructive actions. The test: if this decision were wrong 1 time in 50, would that be acceptable? If not, code owns it.

### Card 14: Agent and team economics (sections 21.10 and 29.9)

Cost per successful task = monthly running cost ÷ tasks completed correctly. Compare with the human baseline, not zero: net saving = baseline (people's time and their failures) − (running cost + takeovers + reviews + the agent's failures). Payback = build cost ÷ net monthly saving; show its sensitivity, not one number. A team pays only when (team success − single success) × value of a success > extra cost per task, or when it meets a latency or quality requirement one agent can't.

## Appendix J: The Same Concepts on Other Platforms

Every concept in this book carries over to other providers and open-source stacks; only the names change. The table was checked in September 2026, and its names are the book's most perishable facts, so confirm them in current documentation.

Table: The same concepts on other platforms
| Concept | Claude API (this book) | OpenAI API | Google Gemini API | Open source |
| --- | --- | --- | --- | --- |
| Tool calling (Chapter 2) | `tools` with `input_schema`; `tool_use` and `tool_result` blocks | `function_call` and `function_call_output` items (Responses API) | Function calling | Ollama and vLLM, through OpenAI-compatible APIs |
| Controlling tool choice (Chapter 3) | `tool_choice`: `auto`, `any`, a named tool or `none` | `tool_choice`: `auto`, `required`, `none` or a named function | A function-calling mode setting | `tool_choice` in vLLM's OpenAI-compatible server |
| Structured outputs (Chapter 3) | JSON Schema output format; strict tools | Structured outputs (JSON schema) | Structured output (JSON schema) | Ollama's `format`; vLLM structured outputs |
| Reasoning controls (Chapter 4) | Adaptive thinking and `effort` | `reasoning.effort` | Thinking settings, which vary by model | Ollama's `think` option; reasoning parsers in vLLM |
| Prompt caching (Chapter 16) | `cache_control` breakpoints, or automatic caching | Automatic, with an optional cache key | Implicit and explicit context caching | Prefix caching in servers such as vLLM |
| Many tools: tool search (Chapter 3) | Tool search tool with `defer_loading` | Tool search with deferred loading | No direct equivalent found | Build it: search your own tool catalog (section 30.9) |
| Code execution (Chapter 16) | Code execution tool; programmatic tool calling | Code Interpreter tool | Code execution tool | Your own sandbox (Chapter 10) |
| Computer and browser use (Chapter 23) | Computer use and browser use tools | Computer use tool | Computer Use tool | Playwright and your own harness (Chapter 23) |
| Batch processing (Chapter 27) | Message Batches API | Batch API | Batch API | Offline batch inference in vLLM |
| Token counting (Chapter 16) | Token counting endpoint | Input token counting endpoint | Token counting method | Counts returned with each response |
| MCP (Part 5) | MCP connector in the API; Claude apps are MCP hosts | Remote MCP servers as a tool | Remote MCP support | MCP SDKs; LangChain MCP adapters; gateways |
| Agent runtimes (Chapter 24) | Claude Agent SDK; Claude Managed Agents | Agents SDK; AgentKit | Agent Development Kit (ADK); Agent Engine | LangGraph, self-hosted or managed |
| Agent-to-agent (Chapter 21) | Through the A2A SDK, not an API feature | Through the A2A SDK | A2A support in Agent Engine (A2A began at Google; now a Linux Foundation project) | The `a2a-sdk` package; A2A endpoints in LangGraph's agent server |

Keep three layers apart: the **concept** (tool calling), the **implementation** you run (Claude, or the local model) and the **equivalent** at work. Section 24.6 shows the same loop on another provider's SDK. When the question is which runtime to use rather than what it's called, turn to the decision matrix "Choosing how to run an agent (as of October 2026)" in Chapter 24.

## Appendix K: Architecture Decision Records

The same seven decisions come up in almost every agent project. An **architecture decision record** (ADR) writes one down: the situation, the decision, when you'd decide differently, what it costs and the evidence. Write them in the Design stage (section 1.10), keep them next to the code, and revisit one when its evidence changes, for example when a new model makes a single agent good enough. Each record below gives this book's default and what overturns it.

### ADR-1: A fixed workflow or an agent

**Context.** Some requests always need the same steps; others need steps that depend on what the tools return.

**Decision.** Default to a **workflow**: code fixes the steps, and the model fills in the language (section 1.3).

**Choose an agent when** the number or order of steps depends on intermediate results, the requests are open-ended, or a person would otherwise pick the next step.

**Consequences.** Workflows are cheaper, faster and easier to test, and fail visibly when a request doesn't fit. Agents handle more but need step limits, traces and trajectory evaluation (Chapter 27).

**Evidence.** In the simulator's E1 (section 29.8), on single lookups, a workflow matched the agent's 97% success at 37% of the cost per success and about two thirds of the p50 latency.

### ADR-2: One agent or a team

**Context.** A task looks big, and splitting it across specialists is tempting.

**Decision.** Default to **one agent** with good context engineering (Chapter 16). Add agents only when the team pays for itself.

**Choose a team when** the work splits into parts that don't need each other's context, a latency target needs them in parallel, or the measured success gain, valued per task, exceeds the extra cost (section 21.10).

**Consequences.** A team adds calls, duplicated context, messages, waiting and failure modes (section 21.5), and needs contracts, limits and containment.

**Evidence.** In E1, a lead with workers matched one agent's 97% success at a third more cost per success.

### ADR-3: Direct tool calls or MCP

**Context.** Your agent needs tools, and other agents or apps may need the same ones.

**Decision.** Start with **direct tools** in the agent's code (Chapters 2–11). Move them to an **MCP server** when a second consumer needs them.

**Choose MCP when** several agents, apps or teams use the tools, another team owns them, or you want to swap hosts without rewriting integrations (section 12.1). Choose A2A when the other side is an agent that owns a task (section 21.8).

**Consequences.** MCP adds a process boundary, a protocol version to track and a supply chain to vet (section 30.10). In return, one server serves every client, with policy in one place (section 30.9).

**Evidence.** Chapters 12–15 and the gateway in section 30.9.

### ADR-4: Fixed retrieval (RAG) or agentic retrieval

**Context.** The agent must answer from documents or data it wasn't trained on.

**Decision.** Use **one retrieval step** (RAG) when one search usually finds the answer, and **agentic retrieval** when questions need several sources, follow-up searches or a judgment about whether the evidence is enough (section 18.8).

**Choose agentic search over files** for small, changing collections and exact terms such as error codes; choose a vector index for millions of documents and fuzzy meaning (section 6.6).

**Consequences.** Agentic retrieval costs more calls per question and needs bounded loops and citation checks (section 18.11). RAG needs an index pipeline and re-indexing.

**Evidence.** Section 18.6 measures retrieval quality; the case study's agent invented policy until code checked the citations.

### ADR-5: A hosted model or a local one

**Context.** Cost, privacy, latency and quality pull in different directions.

**Decision.** Default to the smallest **hosted model** that clears your evaluation bar (Chapter 20). Use a **local model** for learning, for data that must stay in your network, or for high-volume simple steps.

**Choose local when** privacy or residency rules forbid a hosted API, a small model passes your suite for the step, or volume makes per-token pricing cost more than your own hardware.

**Consequences.** Local models are free per call but slower, pick the wrong tool more often, and leave you running the serving stack (Appendix H). Hosted models change on the provider's schedule, so pin dated ids and re-run your suite on every change (section 30.13).

**Evidence.** Appendix H's speed table; section 29.9 for the cost per successful task that settles the volume question.

### ADR-6: Synchronous calls or durable execution

**Context.** Some agent work finishes in seconds; some takes hours and touches systems that mustn't be called twice.

**Decision.** Stay **synchronous** while the task finishes well inside a request timeout with no side effects you'd regret repeating. Otherwise make it a **durable job**: checkpoints, limited retries, idempotency keys and leases (Chapter 19).

**Choose durable execution when** a task can outlive a process or a deploy, a person must approve a step, or any step has an external side effect such as a refund or an email.

**Consequences.** Durable jobs need storage, a worker, status endpoints and compensation (section 19.7). Synchronous calls are simpler but lose all progress on a crash.

**Evidence.** Sections 19.2–19.5 show what breaks without checkpoints and idempotency; section 30.8 applies the pattern to slow MCP tools.

### ADR-7: One tenant or many

**Context.** The agent will serve more than one customer, business unit or team.

**Decision.** Share compute, but **never share** memory, sessions, private caches or tokens across tenants (section 30.12). Every record and trace carries a tenant id.

**Choose a dedicated deployment per tenant when** a contract or regulation demands physical separation, one tenant's load would swamp the others, or tenants need different models or data residency.

**Consequences.** Multi-tenant platforms need tenant-scoped keys, budgets and rate limits, recall filtered by tenant before ranking (section 17.10), and tests that try to cross the boundary. Dedicated deployments cost more to run and upgrade.

**Evidence.** Section 17.10's demo refuses a cross-tenant recall.

### A template for your own records

Table: An architecture decision record
| Field | What to write |
| --- | --- |
| Title | The decision as a choice: "X or Y" |
| Status | Proposed, accepted, superseded by ADR-n |
| Context | The forces: requirements, constraints, risks, what you measured |
| Decision | What you chose, in one or two sentences |
| Alternatives | What you rejected, and why |
| Consequences | What becomes easier, what becomes harder, what you must now build |
| Evidence | The evaluation, benchmark or incident that supports it, with a link |
| Revisit when | The change that would reopen the decision: a new model, a price change, a new requirement |

## Appendix L: From the Book to the Code

This map shows, for every chapter and interlude, the concept, its exercises, the folder its listings come from and the capstones that build on it. Solutions use the same folder names under `solutions/exercises/`. `CURRICULUM_MAP.md` in the kit adds each exercise's level, model and solution file. Both are generated from the manuscript, so they can't drift apart.

Table: Every chapter, its exercises, code and capstones
@@curriculum-map

To work through a row: read the chapter, run its listings with `./course.sh python <file>`, do an exercise with `./course.sh ex <id>`, check it with `./course.sh check <id>` where a checker exists, and compare with `./course.sh solution <id>`.

## Appendix M: Production Deployment Reference

Start with the limit: **the course kit is not production-hardened.** In `course/code_maturity.json`, the security, memory and durability code is labeled *Production pattern*, which means the controls and records have the real shape but the implementation is simplified: in-memory or file storage, demo keys, one process. Nothing in the kit carries the *Production-hardened* label, and Appendix G explains why passing the kit's tests doesn't make a system ready for real users. `SECURITY_MODEL.md` lists, control by control, what the kit leaves out.

This appendix is the list a platform or operations team works through before an agent from this book serves real users. Section 30.7's launch checklist asks whether you built each control; this one asks whether you can keep it running. Every row needs an owner and a date.

Table: What a production deployment adds to the kit
| Topic | What to do | Minimum bar | Where the book touches it |
| --- | --- | --- | --- |
| Multi-tenant isolation | Put a tenant id on every record, session, cache key, token and trace. Filter by tenant before ranking. Give each tenant its own keys, budgets and rate limits, and enforce isolation in the database too | A test per store (memory, sessions, vector index, caches, traces) that tries to read another tenant's data, fails, and runs in CI | Sections 17.10, 30.2 and 30.12; ADR-7 (Appendix K); scenarios S5 and S6 in `SECURITY_MODEL.md` |
| Secret rotation | Keep every secret in a secrets manager and inject it at run time. Sign tokens with your identity provider's asymmetric keys. Rotate on a schedule and on suspicion | No default keys; each secret has an owner and a rotation interval; one scheduled and one emergency rotation rehearsed without an outage | Sections 26.7, 26.8, 30.2 and 30.6 |
| Data retention and deletion | Set a retention period for each store, owned by your legal team. Purge on schedule. Make a deletion request reach every copy | An inventory of stores holding personal data; a deletion test showing the data gone from memory, indexes, embeddings, caches and traces | Sections 17.6, 17.10, 28.3, 30.12 and 30.13 |
| Dependency and container scanning | Lock dependencies with hashes, pin the base image by digest, produce an SBOM for every image, scan dependencies and images in CI and on a schedule, sign images, run as a non-root user | CI fails on a critical known vulnerability unless an exception is recorded; the running image's digest matches a signed build; nothing deployed as "latest" | Sections 14.3, 24.10, 30.6 and 30.10 |
| Backups and recovery | Back up sessions, job checkpoints, memory stores, audit logs and evaluation suites; rebuild or back up vector indexes. Write an RPO and an RTO for each | A restore into a clean environment, timed against the RTO, at least once before launch and then on a schedule | Sections 17.10, 18.1, 19.3 and 30.6 |
| Incident ownership | Name the owning team, an on-call rotation, a runbook per alert and an escalation path on both sides of any customer boundary | Every page reaches a named person within an agreed time; the kill switch has been tested; every incident ends in a postmortem and a new evaluation case | Sections 26.7, 28.11, 28.12, 30.12 and 31.6; the case study |
| Rollback criteria | Write down which signals trigger a rollback, who may decide, and the path back. Keep the previous release deployable by configuration | The rollback path rehearsed on a canary; the on-call engineer may roll back without asking anyone | Sections 27.7, 28.10 and 30.13; the case study |

**Multi-tenant isolation.** The kit's `SecureMemoryStore` checks tenant and owner in application code: right, but not enough. Add isolation that holds when application code is wrong: row-level security or a database per tenant, and per-tenant encryption keys. ADR-7 says when a tenant needs its own deployment.

**Secret rotation.** The kit signs tokens with one shared HS256 key that falls back to a built-in development key, and its API keys have no scopes or expiry. Section 26.7 shows the mechanism: tokens name their key, a scheduled rotation keeps the old key for the longest token lifetime, and an emergency rotation keeps it for none. The OWASP Secrets Management Cheat Sheet covers storage and access.

**Data retention and deletion.** Section 17.10's store shows the shape: time to live on every record, `forget_user`, and an audit log that holds hashes and metadata, never content. In production, deletion must also reach search indexes, embeddings and caches, and per-tenant keys let you make backups unreadable by destroying a key.

**Dependency and container scanning.** `requirements.lock` and section 30.6's image pin exact versions, and the image runs as an unprivileged user. The kit doesn't record hashes, pin the base image by digest, generate an SBOM, scan or sign images; those belong in your build pipeline. Treat MCP servers and skills the same way (sections 14.3 and 24.10): pinned, reviewed, re-reviewed on change. For the practices, see NIST SP 800-218, SLSA (build provenance) and the CIS Docker Benchmark.

**Backups and recovery.** The *recovery point objective* (RPO) is how much recent data you can afford to lose; the *recovery time objective* (RTO) is how long the service may be down. The kit keeps sessions in a SQLite file inside one container (section 30.6); production moves them to a shared, backed-up database. Lose job checkpoints (section 19.3) and crashed work repeats. A vector index can be rebuilt from its source documents (section 18.1); back it up only if rebuilding takes longer than your RTO. Audit logs go to append-only storage the agent can't write; check the hash chain after a restore. Keep evaluation suites, your release gate, in version control. One rule is easy to break: a restore must not bring back data a user asked you to delete. Section 17.10's rollback refuses to, and your backup process must too.

**Incident ownership.** Alerts page on symptoms users feel (section 28.11), and section 28.12's steps are the start of a runbook. Decide in advance who may flip the kill switch (section 26.7) and who calls whom at 3 a.m.; section 31.6 shows how often that's the missing piece. The Google SRE book's chapters on being on-call, managing incidents and postmortem culture describe the practice.

**Rollback criteria.** Roll back when the canary burns its error budget (section 28.10), the regression gate fails (section 27.7), a guard fires or an action is unsafe, or cost per successful task goes over budget. The on-call engineer rolls back on any one of these without a meeting; the release owner decides when the fix tries again. Version the whole agent as one release (section 30.13), so rolling back is a configuration change, as in the case study. A rollback doesn't undo what the agent did: bad memories need section 17.10's point-in-time rollback, and side effects need section 19.7's compensation steps.
