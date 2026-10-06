# Decision guide

The architecture decisions that come up in almost every agent project, with the book's default for each, the conditions that overturn it, and the evidence behind it. It's for an engineer or architect choosing a design with the repository open but not the book: start with the quick table, then read the section for the decision in front of you. The defaults come from the architecture decision records in Appendix K, reference cards 1 and 4 in Appendix I, and the chapters cited in each section. Numbers appear only where the book gives them; most come from the benchmark simulator of section 29.8, whose latencies and error rates are stated assumptions, so they show the mechanics of each design exactly and nothing about how good a real model is. Rerun `ch29_benchmark.py` with a real backend before deciding on numbers alone.

## Quick decision table

| Decision | Default | Switch when | Read |
| --- | --- | --- | --- |
| Workflow, agent or team | A **workflow** (or state machine) | The steps depend on what the tools return: agent. The work splits into independent parts and the gain is measured and worth it: team | ADR-1, ADR-2; section 1.3, section 21.10 |
| Direct tools, MCP, A2A or API | **Direct tools** in the agent's code | A second consumer needs the tools: MCP. The other side is an agent another team or company runs: A2A | ADR-3; section 21.8; card 4 |
| RAG, agentic search or agentic retrieval | **One retrieval step** when one search usually finds the answer | Small, changing collections and exact terms: agentic search over files. Several sources or follow-up searches: agentic retrieval | ADR-4; section 6.6, section 18.8 |
| Hosted or local model | **Hosted**, the smallest that clears your eval bar | Data can't leave your network, the step is simple enough on your suite, or volume makes your own hardware cheaper | ADR-5; Appendix H |
| Small or large model | **Route**: small for easy steps, large for hard ones, judged by cost per successful task | Never "small everywhere" because it's cheaper per call | Section 20.7 to section 20.9; section 29.9 |
| Synchronous or durable | **Synchronous** while the task finishes well inside a timeout and has no side effect you'd regret repeating | It can outlive a process, waits for a person, or has an external side effect: durable job | ADR-6; Chapter 19, section 30.8 |
| One tenant or many | **Shared compute, never shared data**: memory, sessions, private caches and tokens per tenant | Contract or regulation demands physical separation, one tenant dominates load, or tenants need different models or residency: dedicated deployment | ADR-7; section 17.10, section 30.12 |
| Your own loop or a runtime | **Your own loop** while learning or while the agent is small | You need sessions, compaction, subagents, hooks, sandboxes or durability you'd otherwise build | Section 24.5, section 24.9 |

## 1. A function, workflow, state machine, agent or team

**Default: the least autonomy that does the job.** Before choosing an agent, section 1.3 asks four questions: can I draw the flowchart before the task starts? What does a wrong step cost? Can I tell when it's done and right? Is the flexibility worth several times the cost and latency? Reference card 1 lines up the options:

| Option | Choose it when |
| --- | --- |
| Function | The rules are exact and known |
| Workflow | The steps are known in advance |
| State machine | The process has stages, rules and audits |
| RAG | The job is answering from documents |
| Single LLM call | One prompt does the job |
| Agent | The steps depend on what you find along the way |
| Multi-agent system | The work splits into independent parts, and the cost is worth it |

**Switch to an agent when** the number or order of steps depends on intermediate results, the request space is open-ended, or a person would otherwise choose the next step (ADR-1). Section 1.9 then asks which kind (assistant, knowledge agent, analyst, action agent behind approvals, feedback loop, research team, planner, long-running, computer use), because the kind names the controls a part needs. Even at the agent end, section 22.8 keeps preconditions, approvals, output validation and a budget around each tool; where mistakes are costly or regulated, move toward the workflow end.

**Switch to a team only when** the parts don't need each other's context, parallelism matters for a latency target, or the measured success gain, valued per task, exceeds the extra cost (ADR-2, section 21.9). Section 21.10's rule: (team success − single success) × value of a success > team cost per task − single cost per task, with a gain outside the overlap of the two confidence intervals; or the team meets a latency or quality requirement one agent can't. Try the cheaper fixes first: parallel tool calls, context engineering (Chapter 16), a workflow.

**Evidence.**
- E1, single-part questions (section 29.8): workflow, one agent and a lead with workers all reached 97% (92–99%). Cost per success was $0.0012, $0.0032 and $0.0043; p50 latency 2.5 s, 3.9 s and 6.2 s. The workflow matched the agent at 37% of the cost per success.
- Section 21.10, multi-part questions: the team cost 2.2 times as much and was 1.8 seconds slower for a gain inside the intervals (93% against 97%). With 3-second tools and a 16-second p95 SLO, only the team met it (15.7 s against 17.4 s) until one agent ran its tool calls in parallel (13.5 s at the single agent's price).
- Reliability compounds: with 97% per step, a lead plus three workers gets every part right about 86% of the time; one retry per contained failure lifts it back to 94% (section 21.10).
- Section 11.1 cites Anthropic's measurement of orchestrator–worker at about 15× the tokens of chat, worth it on broad research where one context can't hold every source.
- The case study chose a workflow for order status, a state machine for returns and refunds, one agent with retrieval for everything else, and rejected a team.

Code: `ch22_guarded.py` (state machine), `ch04_agent.py` (agent), `ch11_research_team.py` and `ch21_orchestrator.py` (teams), `ch21_coordination.py` (`coordination_report`, `decide`).

## 2. Direct tools, MCP, A2A or a plain API

**Default: direct tools** in the agent's own code (Chapters 2–11). Move a tool set to an **MCP server** when a second consumer needs it.

**Switch to MCP when** more than one agent, app or team uses the tools, the tools belong to another team, or you want to swap hosts without rewriting integrations (ADR-3, section 12.1). MCP adds a process boundary, a protocol version to track (`VERSION_MATRIX.md`) and a supply chain to vet (Chapter 14, section 30.10). In return one server serves every client and policy can sit in one place, an MCP gateway (section 30.9).

**Switch to A2A when** the other side is an agent that owns a task, not a set of tools: owned by another team or company, built with a framework you don't control, or running long enough that the caller needs progress (section 21.7). Section 21.8's rule: **MCP inside your system, A2A at its boundary.** An agent your team runs is usually best exposed as an MCP tool or called in code.

Reference card 4, for the rest of the connections:

| You need to... | Use |
| --- | --- |
| Connect a model to a tool or data | A tool; an MCP server to share it |
| Let independent agents collaborate across a boundary | A2A |
| Let one service call another, conventionally | An API |
| Run a deterministic business process | A workflow or state machine |
| Get a person's decision before acting | Human in the loop: an approval gate |
| Run work that takes hours and survives crashes | A durable workflow |
| Search and retrieve knowledge | A retrieval system |
| Do something local and simple | A plain tool |
| Share one front door for many tools, with policy | An MCP gateway |

**Evidence.** Chapters 12–15 and the gateway in section 30.9 (ADR-3). Whatever you choose, a remote server or agent is untrusted: authenticate both ways, treat its answers as untrusted content, and remember that discovering it isn't trusting it (section 26.9).

Code: `ch03_tools.py` (direct), `ch12_weather_server.py` and `ch13_mcp_agent.py` (MCP), `ch30_gateway.py`, `ch21_a2a_server.py` and `ch21_a2a_client.py` (A2A).

## 3. RAG, agentic search or agentic retrieval

**Default: one retrieval step (RAG)** when one search usually finds the answer (ADR-4).

**Choose agentic search over files** (Chapter 6) for small, changing collections and exact terms such as error codes; choose a vector index for millions of documents and fuzzy meaning. Section 6.6 compares them:

| | Agentic search | RAG |
| --- | --- | --- |
| Setup | None | Chunking, embedding, a vector store |
| Freshness | Always current | Re-index when files change |
| Exact terms | Excellent (regex) | Can miss them |
| Fuzzy meaning | Needs good search terms | Excellent |
| Scale | Thousands of files | Millions of documents |
| Cost per question | More model steps | One retrieval plus one call |

Many production systems combine them: RAG becomes one tool (`semantic_search`) next to exact search and read tools.

**Switch to agentic retrieval when** questions need several sources, follow-up searches or a decision about whether the evidence is enough (section 18.8). The agent decides what to retrieve, from where (section 18.9: each source described like a tool), whether it's sufficient and whether to search again; code bounds the loop and verifies the answer (every factual sentence cited, every citation retrieved, every number present in its evidence; section 18.11). It costs more model calls per question.

**Evidence.** Section 18.6 measures retrieval quality. The case study's first test run answered four of ten policy questions from the model's general knowledge until citations were checked in code; the rerun got nine right with citations and handed off the tenth. Putting the whole 8,000-token handbook in the system prompt instead cost 16 times as much per success (E3).

Code: `ch06_notes_tools.py`, `ch18_rag.py`, `ch18_agentic.py` (`plan_needs`, `assess`, `verify`).

## 4. A hosted model or a local one

**Default: a hosted model** for quality and tool use, the smallest one that clears your evaluation bar (ADR-5).

**Switch to local when** data residency or privacy rules forbid a hosted API, the step is simple enough for a small model on your evaluation suite, or the volume makes per-token pricing more expensive than your own hardware. Local models are free per call but slower on ordinary hardware, pick the wrong tool more often and need you to run and patch the serving stack. Hosted models change on the provider's schedule: pin dated ids and rerun your suite on every model change (section 30.13).

**Evidence.** Appendix H's speed table for `qwen3.5:9b`: a typical 3–6-call agent exercise takes 10–40 seconds on an NVIDIA GPU with 8 GB or more, 20–60 seconds on Apple Silicon with Ollama as an app, and 1–5 minutes on CPU only; it needs 16 GB of RAM at minimum. Section 29.9 supplies the cost per successful task that decides the volume question.

Code: `course/local_adapter.py` lets the same code run on the local model; `LOCAL_MODEL.md` has the setup.

## 5. A small model or a large one

**Default: route by difficulty** and judge by cost per successful task (section 20.9). Section 20.7's options: a small model (Claude Haiku 4.5, $1 in and $5 out per million tokens) for lookups, classification, formatting and simple tool calls; a larger model (Claude Sonnet 5, $2 and $10) for multi-step reasoning and judgment; more `effort` on the same model for the hardest steps; the local model for learning, private data or high volume where quality allows.

**Three routers** (section 20.8): rules (free, predictable, blunt), a classifier model (one small call, can be wrong both ways), and a cascade that accepts the small model's answer only if a check in code passes. A cascade is only as good as its check. Fallback routing to another provider is a reliability feature and needs the fallback evaluated too.

**Don't switch to "small everywhere"** because it's cheaper per call. If the small model costs half as much but succeeds on 50% of tasks where the large one succeeds on 95%, it isn't cheaper per success, and failures have their own costs.

**Evidence.**
- E3 (section 29.8): small model 93% (86–97%) at $0.0017 per success; large model 98% (93–99%) at $0.0032. Half the price per success, but the small model's interval reaches well below the large one's.
- Section 29.9: in the support agent's business case, tokens are 0.4% of the monthly cost, and exercise 29.8 finds Claude Haiku 4.5's $81-a-month token saving wiped out by 0.02 more percentage points of failures. Spend effort where the failure cost is.
- The case study uses a small model to classify messages, sending anything unclear to the most capable path, and the large model for answers.

Code: `ch20_router.py` (`by_rules`, `by_model`, `cascade`, `report`, `PRICES`), `ch29_economics.py`.

## 6. Synchronous calls or durable execution

**Default: synchronous** while the whole task finishes well inside a request timeout and has no side effect you'd regret repeating (ADR-6).

**Switch to a durable job when** a task can outlive a process or a deploy, a person must approve a step, or any step has an external side effect such as a refund or an email. Durable jobs need checkpoints, retries with limits, idempotency keys and leases (Chapter 19), plus storage, a worker, status endpoints and compensation (section 19.7, section 30.8). For a slow tool, return a job id at once and let the caller check (`start_report` and `job_status` in `ch30_jobs_server.py`), which matches MCP's Tasks extension. In production, build on a durable-execution platform and check that model outputs are recorded and reused on replay and every side effect is idempotent or escalated (section 19.9).

**Evidence.** Section 19.2 to section 19.5 show what breaks without checkpoints and idempotency; scenarios S13 and S15 in section 25.10 test it. Code: `ch19_durable.py`, `ch19_harness.py`, `ch30_jobs_server.py`.

## 7. One tenant or many

**Default: share compute, never share data.** Memory, sessions, private caches and tokens are per tenant; every record and every trace carries a tenant id (ADR-7, section 30.12). Give each tenant its own keys, rate limits and budgets so one tenant's spike or looping agent can't exhaust another's allowance. Recall filters by tenant before ranking (section 17.10).

**Switch to a dedicated deployment per tenant when** a contract or regulation demands physical separation, one tenant's load would dominate the others, or tenants need different model or data-residency choices. Dedicated deployments cost more to run and upgrade.

**Evidence.** Section 17.10's demo refuses a recall across tenants with `PermissionError`; scenarios S5 and S6 test memory and session isolation. Code: `ch17_memory_security.py`, `ch30_service.py`.

## 8. Your own loop or a framework, SDK or managed runtime

**Default: your own loop** while you're learning, the agent is small, you need full control of every request or dependencies must be minimal (section 24.5).

**Switch to a framework or runtime when** the agent needs sessions, compaction, subagents or hooks you'd otherwise write, you want well-tested plumbing and fewer lines to maintain, or your team already uses one. Section 24.9 compares the options:

| Runtime | What you get | What stays your job |
| --- | --- | --- |
| Your own loop | Full control, no dependencies | Everything in Chapters 19–23 |
| The tool runner | The loop, with less code | Durability, teams, controls |
| The Claude Agent SDK | Sessions, subagents, hooks, permissions, built-in tools | Hosting, durability across machines, evaluation |
| LangGraph and similar | Graphs of steps, checkpointers, many providers | Choosing and operating storage, controls |
| A durable-execution platform with your loop inside | Crash-proof steps, retries, timers, waiting for people | The agent logic |
| Claude Managed Agents | Sandboxes, sessions, permissions, budgets, memory stores on Anthropic's servers | Tools that must stay local, evaluation |

Ask of any option: where does state live and does a session survive a crash? How are approvals and hard rules expressed, and can the model get around them? Can you see every step and its cost? Where does code run and what can it reach? What does it cost at your volume, and what would leaving cost? A common path: prototype with your own loop, move to an SDK or framework once the design settles, and put anything long-running inside a durable runner. For platform components generally, section 30.12 asks whether you can keep it running for three years without the core team becoming its on-call; buy or rent what isn't your advantage and keep the interfaces your own (OpenTelemetry, MCP, your eval cases).

Code: `ch04_agent.py`, `ch24_tool_runner.py`, `ch24_agent_sdk.py`, `ch24_langchain.py`, `ch24_managed_agent.py`.

## Recording a decision

Write each decision down in the Design stage (section 1.10) using Appendix K's template: title as "X or Y", status, context, decision, alternatives, consequences, evidence, and **revisit when**. Revisit when its evidence changes: a new model can make the single agent good enough, a price change can move a routing decision. To read a benchmark for a decision (section 29.8): drop every configuration whose success interval is below what you need, prefer the simplest design and then the lowest cost per success, check p95 at your concurrency against your SLO, and set concurrency at the knee. A difference smaller than the overlap of two intervals isn't a difference.

## Where this comes from

- Appendix K (ADR-1 to ADR-7 and the template); Appendix I, card 1 and card 4; Appendix H
- Section 1.3, section 1.9; section 6.6; section 11.1; section 18.8 to section 18.11
- Section 20.7 to section 20.9; section 21.7 to section 21.10; section 22.8; section 24.5, section 24.9
- Section 29.8 (benchmark E1–E4), section 29.9 (economics); section 30.12, section 30.13; the case study
- Code: `course/code/ch29/ch29_benchmark.py`, `course/code/ch21/ch21_coordination.py`, `course/code/ch20/ch20_router.py`, `course/code/ch18/ch18_agentic.py`, `course/code/ch19/ch19_durable.py`; published runs in `benchmarks/`
