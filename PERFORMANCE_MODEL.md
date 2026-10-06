# Performance model

This is the reference for how an agent spends time and money, and how to measure, budget and plan for it: latency, throughput, tokens, concurrency, queueing, capacity and cost. It's for an engineer who has the repository but not the book open, and who needs to answer "why is it slow?", "what does a task cost?" or "how many deployments do we need?" with measurements instead of guesses. It distills Chapter 29, with the profiling from section 28.13 and the team overhead from section 21.10. Learner costs for working through the book are a separate question, answered in `COST_MODEL.md`.

Everything here runs offline first: the sweep, the load test, the benchmark and the profiler all have free simulators. **Every number quoted below from the benchmark is a simulator number**: it follows from the latency and error-rate assumptions written in `SIM_MODELS`, so it shows the mechanics of each design exactly and nothing about how good a real model is. No measured Claude run has been published yet (`benchmarks/README.md`).

## 1. The two sums

Every agent task spends its time and money in a few places (section 29.1, Card 8 in Appendix I):

```
Total latency  = model + tool + retrieval + orchestration + queueing + serialization
Cost per task  = model + tools + retrieval + infrastructure + retries + human review
```

When a task is slow or expensive, compute both sums from a trace and attack the biggest term.

### Latency terms

| Term | What it is | How to measure it |
| --- | --- | --- |
| Model | Request leaving your process to the last token arriving: time to first token plus output time. Timed at the client, it includes the network | `chat` spans (Chapter 28) |
| Tool | Tools that compute or act (calculator, send email) | `execute_tool` spans |
| Retrieval | Tools that fetch data (search, SQL, vector lookup); they scale with data size, not with the model | `execute_tool` spans, sorted by name with `is_retrieval` |
| Orchestration | Your own code between calls: loop, guards, prompt assembly, logging, any untraced hop | The remainder: total minus every other term |
| Queueing | Waiting for a turn: a gateway slot, a connection, a provider rate limit | A `queue` span around the wait. Unrecorded, it hides inside the model term and you blame the model |
| Serialization | Encoding requests, decoding replies, copying the history | `serialize` spans, or `measure_serialization` × steps |

`latency_model` in `course/code/ch29/ch29_perf.py` takes a trace's spans or a dict of components and returns the six terms and their total. The terms add up only if steps run one after another: **a negative orchestration term means spans overlapped** (parallel tool calls), so read the trace instead of the sum.

### Cost terms

| Term | Formula | Source |
| --- | --- | --- |
| Model | Tokens × price. Cache reads cost 10% of the input price, cache writes 125% (Chapter 16) | Token counts on `chat` spans; `PRICES` in `ch20_router.py` |
| Tools | Paid tool calls × their price | `execute_tool` spans, invoices |
| Retrieval | Paid search or vector queries × their price | Same |
| Infrastructure | Server $/hour ÷ tasks finished in that hour. It falls as throughput rises, so idle servers make every task dearer | Cloud bill, throughput |
| Retries | Thrown-away calls (timeouts, malformed replies), each priced as an average call of the task | Traces |
| Human review | Share of tasks reviewed × minutes × hourly rate. The term teams forget, and often one of the largest | Review queue |

`cost_per_task` in `ch29_perf.py` computes it. The book's worked example (section 29.1): a 6-step run, 53,100 input tokens on Claude Sonnet 5 (30,000 cache reads, 6,000 cache writes), 1,800 output tokens, three $0.002 retrievals, one retry, a $2/hour server at 600 tasks/hour, and 2% of tasks reviewed for 3 minutes at $60/hour costs **$0.155**: model 47%, **human review 39%**, retries 8%, retrieval 4%, infrastructure 2%. The prices are assumptions; put in your own.

### Cost per successful task

The cost that decides between designs is **cost per successful task**: total spend ÷ tasks that succeeded. Failed and escalated tasks were paid for too and bought nothing. A lever that saves 40% of the cost but loses 10% of the successes can raise it (section 29.3). For a deployed agent's business case (section 29.9, Card 14, `ch29_economics.py`):

| Metric | Formula |
| --- | --- |
| Cost per task | (tokens + tools + infrastructure + upkeep) per month ÷ tasks |
| Cost per successful task | The same total ÷ tasks completed correctly |
| Cost per user per month | The same total ÷ distinct users a month |
| Net saving | Human baseline (people's time and their own failures) − (running cost + takeovers + reviews + the agent's failures) |
| Payback | Build cost ÷ net monthly saving |

In the support-agent example, tokens are 0.4% of the monthly cost, cost per task is $0.255 and per successful task $0.392, and payback is 3.8 months; the assumption that moves payback most is how long a person takes per conversation today, not anything about the model. Compare with the human baseline, never with zero, and present break-even points (`break_even`) and `sensitivity`, not one payback figure.

## 2. Where it goes: history dominates

Each model call resends the whole conversation: system prompt and tools (the prefix), the question, every earlier reply and tool result. So cost and latency grow faster than the number of steps (section 29.2). A 6-step run with a 6,000-token prefix sends about 53,000 input tokens, 36,000 of them the same prefix six times: about $0.12 on Sonnet 5, $0.07 with caching, $0.04 on Haiku 4.5 with caching. `estimate` in `ch29_costs.py` does the arithmetic (`./course.sh python ch29_costs.py`). Output tokens are the slow part of latency; a longer history also raises time to first token, which is why caching helps latency as well as cost.

## 3. The levers

Each lever shrinks one term (section 29.3). Measure first, pull the lever for the biggest term, change one thing, and remeasure **on your evaluation suite** (see `EVALUATION_MODEL.md`).

| Lever | Saves | Cost to you | Chapter |
| --- | --- | --- | --- |
| Prompt caching | Up to ~90% of the repeated prefix's input cost; time to first token | Keep the prefix stable | 16 |
| Trimming and compaction | Input tokens from old turns and results | Some risk of losing detail | 16 |
| Routing to a smaller model | Half or more of the price on easy steps | A router, and evals proving quality holds | 20 |
| Lower `effort` / less thinking | Output tokens and time on routine steps | Quality on hard steps | 4 |
| Fewer steps | Whole model calls | Design work | 2, 3 |
| Parallel tool calls | Wall time within a step | Care with shared state | 7 |
| Caching tool results | Slow external calls | Staleness | 7, 16 |
| Batch API | Half the price of work that can wait | Minutes to hours of delay | 27 |
| Streaming | Perceived latency | None | 30 |

## 4. Budgets in code

A budget in a prompt is a wish; a budget in code is a limit (section 29.4, `ch29_costs.py`):

- **Per request:** `request_budget(dollars)` returns a `should_stop` hook for the Chapter 4 loop; the run stops with a clear reason before it overspends.
- **Per user per day:** `DailyBudget` refuses new runs once a user's allowance is spent (`allow`) and charges each run's actual cost when it ends (`charge`).
- **Per job:** long-running jobs carry their own budget (exercise 19.5).
- **Alerts:** cost per successful run has an alert threshold (section 28.11).

## 5. Metrics to report under load

Report these at every load level (sections 29.5 and 29.6, Card 8):

| Metric | Why |
| --- | --- |
| p50, p95, p99 latency | The tail is what users complain about; never report only the mean |
| Throughput | Tasks finished per second |
| **Goodput** | Tasks that *succeeded* per second. Fast failures inflate throughput exactly when the system is overloaded, so judge levels by goodput |
| Success rate | A system that stays fast by failing hasn't scaled |
| Tokens and steps per task | If they change with load, the agent behaves differently, not just slower |
| Model, tool, retrieval and queueing time per task | Shows which term grows |
| Cache hit rate | Share of input read from the prompt cache; it falls under load |
| Cost per successful task | The number to compare |
| Errors (429s, timeouts) | They appear only when you push |

## 6. Finding the knee: closed-loop sweep

The **knee** is the concurrency where adding tasks in flight stops buying throughput and starts buying queueing (section 29.5). `experiment` in `ch29_perf.py` runs a closed-loop sweep (fixed workers, each starting a new task when the last ends) at 1, 2, 4, 8 and 16 in flight. Each level gets a fresh `Backend` with its own model slots and prompt cache; `Backend.slot` measures the wait and raises `QueueTimeout` (what a gateway turns into HTTP 429) past a deadline. Task *i* draws the same random numbers at every level (common random numbers), so row differences come from concurrency, not luck. `knee` picks the lowest concurrency reaching 90% of the best goodput; `interpret` and `format_experiment` print the verdict and table.

`./course.sh python ch29_perf.py` runs `simulated_agent` with four model slots and 48 tasks per level, on a clock 100 times faster than real time, so rows at high concurrency vary a little from run to run. The book's run: perfect scaling to 4 in flight (0.16, 0.32, 0.64 tasks/s, p50 5.7 s); at 8, throughput 0.68 but p50 11.3 s, with about 5 s of queueing per task; at 16, throughput 1.03 but only 40% succeed, goodput 0.41, cost per success $0.0655. The knee is at 4, the number of model slots; cache hit rate falls from 86% to 74%. Cost per success is lowest at the knee.

Pass `real_agent` instead to sweep the Chapter 8 analyst on a real model (exercise 29.6); `model_slots=2` shows a client-side knee.

Then act:

- **Cap concurrency at the knee**; queue a few more with a deadline and refuse the rest quickly.
- **Plan capacity from goodput at the knee** (section 7 below).
- **Name the limiting resource** (provider rate limit, your slots, a tool) and raise it deliberately.
- **Set SLOs from the knee**: p95 and cost per success there are realistic targets (section 28.10). Rerun after every model, prompt or tool change; a knee that moves left is a regression.

## 7. What users feel: open-loop load test

A closed-loop test sends *less* traffic as the agent slows, so it can't tell you what happens at a forecast arrival rate (section 29.6). `open_loop` in `ch29_loadtest.py` sends requests at random times averaging `rate` per second regardless of what's in flight, and **starts the clock when the request was due**, including any wait for a slot. Starting it when work begins hides the queue: *coordinated omission*. With `fake_agent` and 20 slots, capacity is about 9 requests/s; at 12/s p50 jumps to about 6 s while a clock started after the slot still says about 2.5 s (exercise 29.1). Watch p95 and max, errors under load, and throughput against offered load: when throughput flattens and latency climbs, you've hit the limit.

## 8. Capacity planning with Little's law

Two formulas answer most capacity questions (section 29.7, `ch29_costs.py`):

```
tasks in flight = arrival rate × time per task               concurrency_needed(arrivals_per_s, latency_s)
requests/min    = min(RPM ÷ calls per request,
                      TPM ÷ tokens per request)              rate_limited_capacity(rpm, tpm, calls, tokens)
```

Steps:

1. **Measure one task.** Latency and tokens from traces at concurrency 1 (no queueing mixed in), and calls per task.
2. **Find the knee** with the sweep: goodput and p95 per deployment at its concurrency limit.
3. **Apply Little's law to your forecast peak.** 10 requests/s × 8 s each = 80 in flight. If one deployment's knee is at 20, you need at least four.
4. **Check the provider's limits.** The token limit usually binds first: with 4,000 requests and 2 million tokens a minute, 6-call runs of 60,000 tokens fit about 33 times a minute, whatever the request limit allows.
5. **The limit is the scarcest** of model slots, rate limits and workers (Card 8).
6. **Fail gracefully past it:** queue with a limit, answer "busy, try again" (HTTP 429 or 503) rather than time out, prioritize interactive users over background jobs.
7. **Raise capacity** with the levers that cut tokens per run, or ask the provider for higher limits; then sweep again.

## 9. Teams of agents: coordination overhead

A lead with workers pays costs one agent doesn't (section 21.10, Card 14, `ch21_coordination.py`): extra model calls, duplicated context, inter-agent messages, synchronization (waiting for the slowest worker), retries, latency, failure propagation and total cost.

```
team cost     = sum of worker costs + lead planning + lead synthesis + duplicated context + messages
team latency  = lead planning + max(worker latencies) + synthesis
p(task right) = p(lead steps) × p(step) ^ n
```

A team is worth it only when (team success − single success) × value of a success > extra cost per task, with the gain outside the confidence-interval overlap, or when it meets a latency or quality requirement one agent can't. Compare it with the best single agent you can build: on the simulator, one agent with parallel tool calls beat the team's p95 at the single agent's price.

## 10. The reproducible benchmark

`course/code/ch29/ch29_benchmark.py` (section 29.8) compares designs the same way every time, on the Chapter 27 SQL questions with known answers:

| Experiment | Compares |
| --- | --- |
| E1 Architecture | Fixed workflow, one agent (Chapter 8 analyst), lead with parallel workers (Chapter 11) |
| E2 Tool execution | A turn's tool calls one after another vs at the same time |
| E3 Model and context | Small vs large model, each with base context and +8,000 tokens of system prompt |
| E4 Load | 1–16 tasks in flight on four model slots, mixed questions, with and without 10% transient tool failures |

Why the numbers are trustworthy: success means a right answer, checked against the database with `contains_value`; every configuration draws the same random numbers (keyed by experiment, question and repetition); one warm-up task per configuration is discarded and each question repeats (5 on the simulator, 3 on a real model); success comes with a 95% Wilson interval.

```bash
./course.sh python ch29_benchmark.py                          # simulator: free, ~2 seconds, identical everywhere
./course.sh python ch29_benchmark.py --quick                  # one repetition, fewer questions
./course.sh python ch29_benchmark.py --backend claude --quick # about $1
./course.sh python ch29_benchmark.py --backend claude --budget 10   # full run, about $10, stops at the budget
./course.sh python ch29_benchmark.py --backend local          # free local model; slow on a CPU
```

Other flags: `--experiments E1,E3`, `--reps`, `--slots`, `--concurrency 1,2,4`, `--long-context 0`, `--tool-ms`, `--fail-rate`, `--quiet`. Each run writes a folder (`workspace/benchmarks/<backend>-<time>/`) with `config.json` (commit, model ids, prompts hash, data fingerprint, seed, repetitions, warm-up, tool latency, hardware, Python), `raw.jsonl` (one line per task), `summary.json` and `summary.md`. Compare runs only when their configs match on everything but what you changed.

### Published simulator results (`benchmarks/sim-edition-1.1/`)

Simulated model, seed 29, 5 repetitions after 1 warm-up, 250 ms tools. Dollar figures are token counts at list prices; nobody was billed.

| E1 (one-part questions) | Success (95% CI) | p50 s | p95 s | Calls | Tokens | $ per success |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Workflow | 97% (92–99%) | 2.5 | 3.7 | 2.1 | 304 | 0.0012 |
| One agent | 97% (92–99%) | 3.9 | 4.6 | 3.0 | 1,109 | 0.0032 |
| Lead with workers | 97% (92–99%) | 6.2 | 7.1 | 5.0 | 1,325 | 0.0043 |

| E2 / E3 | Success (95% CI) | p50 s | p95 s | Tokens | $ per success |
| --- | --- | ---: | ---: | ---: | ---: |
| Multi-part, tools sequential | 93% (79–98%) | 4.9 | 5.5 | 1,229 | 0.0041 |
| Multi-part, tools parallel | 93% (79–98%) | 4.6 | 5.2 | 1,229 | 0.0041 |
| Small model, base context | 93% (86–97%) | 2.0 | 2.8 | 1,145 | 0.0017 |
| Small model, +8,000 tokens | 93% (86–97%) | 2.6 | 3.6 | 25,772 | 0.0282 |
| Large model, base context | 98% (93–99%) | 3.9 | 4.4 | 1,110 | 0.0032 |
| Large model, +8,000 tokens | 98% (93–99%) | 5.0 | 5.5 | 25,259 | 0.0525 |

| E4 in flight | Tool failures | p50 s | p95 s | Waiting for a slot, s | Throughput /s | Goodput /s |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0% | 3.9 | 4.9 | 0.0 | 0.24 | 0.23 |
| 4 | 0% | 3.9 | 4.9 | 0.0 | 0.94 | 0.89 |
| 8 | 0% | 6.8 | 8.2 | 2.8 | 1.11 | 1.05 |
| 16 | 0% | 13.5 | 15.2 | 9.2 | 1.11 | 1.05 |
| 4 | 10% | 4.0 | 7.1 | 0.0 | 0.85 | 0.81 |
| 16 | 10% | 13.9 | 20.7 | 10.0 | 1.01 | 0.96 |

What the simulator shows: on questions one query answers, the workflow matches the agent's success in two thirds of the time for less than half the cost (section 1.3's rule, measured). Parallel tools save about 300 ms here. A long uncached system prompt makes each success about 16 times as expensive on either model with no accuracy gain. The knee is between four and eight in flight, at the four model slots. Retried transient tool failures cost no answers but 2 s at p95: watch the tail.

**Reading a benchmark to decide:** (1) drop configurations whose success is too low, judging by the interval; (2) of the rest, prefer the simplest design, then the lowest cost per success; (3) check its p95 at your concurrency against your SLO (section 28.10); (4) set the concurrency limit at the knee. A difference inside the overlap of two intervals isn't a difference. Then run it on your model: the simulator's error rates and latencies are assumptions until a real backend replaces them.

## 11. Diagnosing slowness with the profiler

A trace says *where* time went; it doesn't say *why* (section 28.13). `ch28_profile.py` joins spans with what the machine was doing:

1. **Attribute.** `attribute` gives each span the time-weighted mean of CPU, memory, GPU, database query time and network round trip over its window (`resources_during`), and the milliseconds spent while each was **saturated** (`SATURATION`: 85% CPU, 90% memory, 90% GPU, 250 ms per query, 100 ms network; starting points, set your own). A span saturated for half its time is marked `saturated_by` that resource.
2. **Correlate.** `correlate` computes Spearman rank correlation (`rank_corr`) of latency with each signal per group, and the **lift**: p50 while saturated ÷ p50 while not. `diagnose` blames a resource only when lift ≥ 1.5 *and* r ≥ 0.3; either alone misleads (load makes everything correlate). Span signals (output tokens, rows) at r ≥ 0.5 explain latency on their own.
3. **Profile.** `top_frames` counts the leaf frame of stack samples in the slowest spans; `slowest(..., unexplained=True)` keeps the tail no saturation explains. Profile wall-clock time for latency (py-spy `--idle`); starvation looks like a normal profile, only longer, so record the thread's CPU time on the span and compare it with wall time.

Run `./course.sh python ch28_profile.py`. In its synthetic ten minutes: model calls are 90% of the time and follow output tokens (r = 0.99), so the levers are fewer output tokens and steps; `run_sql` is slow when the database is busy (lift 12.5, r = 0.90, 91% of samples in `socket.recv`), a ticket for the database owner; `render_chart` is slow when the CPU is saturated (lift 3.3) though its profile looks normal; and the unexplained `run_sql` tail returned a median 41,655 rows with 87% of time in `json.dumps`, so cap and aggregate in SQL. Averaged over ten minutes, both incidents vanish; only the per-span join sees them. Prove the diagnosis with an experiment: reproduce the load and change one thing.

A time join is only as good as its resolution (sample at least as often as spans are short), shared clocks and place (join on the host, pod or GPU the span ran on).

## Limits of the kit's code

From `course/code_maturity.json`: `ch29_perf.py` is a Learning demo; `ch29_benchmark.py` and `ch29_loadtest.py` are Prototypes; `ch29_costs.py`, `ch29_economics.py`, `ch28_profile.py` and `ch21_coordination.py` are Production patterns. None is production-hardened. A production version adds:

- Profiling and joins inside your observability backend over streams, joining on host and pod as well as time, using window maxima as well as means, and comparing spans at similar load.
- A business case with ramp-up, volume growth, intervals on every measured rate, re-evaluation cost after model upgrades, and discounting.
- Load tests against the real agent with spend limits set in the provider console first, and measured (not simulated) benchmark runs published next to the simulator's.

## Where this comes from

- Section 29.1 (the two sums), 29.2 (history), 29.3 (levers), 29.4 (budgets), 29.5 (the knee), 29.6 (open-loop load), 29.7 (Little's law and rate limits), 29.8 (benchmark), 29.9 (economics); exercises 29.1–29.8
- Section 28.13 (continuous profiling); section 21.10 (coordination overhead); Cards 8 and 14 in Appendix I
- `course/code/ch29/ch29_perf.py`, `ch29_costs.py`, `ch29_loadtest.py`, `ch29_benchmark.py`, `ch29_economics.py`; `course/code/ch28/ch28_profile.py`; `course/code/ch21/ch21_coordination.py`
- `benchmarks/README.md`, `benchmarks/sim-edition-1.1/summary.md`
