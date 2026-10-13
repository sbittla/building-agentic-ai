# Benchmark results

Published runs of `course/code/ch29/ch29_benchmark.py` (section 29.8 of the book). Each folder is one run:

| File | What it holds |
| --- | --- |
| `config.json` | Everything needed to rerun it: commit, backend, model ids, simulator assumptions, prompts hash, data fingerprint, seed, repetitions, warm-up, tool latency, hardware, Python, the exact command |
| `raw.jsonl` | One line per task: experiment, configuration, question, right or wrong, latency by part, model calls, tokens, cost, errors |
| `summary.json`, `summary.md` | The tables, with 95% intervals for success |

| Run | Backend | What it tells you |
| --- | --- | --- |
| `sim-book-v1.0/` | Simulator | The mechanics of each design, exactly: same seed, same numbers on any machine. Not how good a real model is. The book's Tables 29.x come from this run. |

## Adding a run with a real model

From the kit folder, with your key in `.env` (Claude) or the local model started (`./course.sh local up`):

```bash
./course.sh python ch29_benchmark.py --backend claude --budget 10   # about $10 for the full run
./course.sh python ch29_benchmark.py --backend local                # free; hours on a CPU
./course.sh python ch29_benchmark.py --backend claude --quick       # about $1: one repetition, 8 questions
```

Each writes `workspace/benchmarks/<backend>-<time>/`. To publish one, copy the folder here, rename it (`claude-book-v1.0/`), and add a row to the table above. Compare runs only when their `config.json` matches on everything but what you changed, and read differences against the confidence intervals: a difference inside the overlap isn't one.

## Conditions behind the book's numbers

The book prints a short note on the conditions behind each set of numbers. The full conditions are here, one subsection per chapter.

### Chapter 21: team economics (section 21.10, `ch21_coordination.py`)

| Condition | In `ch21_coordination.py` |
| --- | --- |
| Model or simulator | The section 29.8 simulator, standing in for Claude Sonnet 5 on every call. Its speeds and error rates (650 ms to the first token, 4% broken and 3% wrong SQL) are assumptions in `SIM_MODELS`; cost uses Sonnet 5's list prices |
| Prompt and output sizes | Input is counted from the text sent (about four characters per token). Output is fixed per kind of call, such as 40 tokens per query |
| Concurrency | One task at a time, on a virtual clock; inside a task the workers run at once. Tools take about 250 ms (3 s in the slow rows) and never fail. Rate limits and queueing: not modelled |
| Trials or tasks | 20 one-part questions × 5 repetitions = 100 tasks per design; 6 multi-part × 5 = 30, with the same seeds for both designs |
| Cache conditions | Not modelled: no token counts as cached, and every call pays the full input price |
| Uncertainty | A 95% Wilson interval on success rates; calls, tokens, p95 and cost are single values |
| Measured, estimated or illustrative | Measured on the simulator: exact for mechanics, illustrative for model quality. The $0.05 per right answer and 97% per step are assumptions. Without the simulator, the script prints stand-in numbers and says so |

### Chapter 27: the demo scorecard (section 27.6, `ch27_eval.py`)

| Condition | In this demo |
| --- | --- |
| Model | None. `_canned` builds six runs as `grade` would return them |
| Size | 2 cases × 3 trials = 6 runs |
| Concurrency and cache | None: no model is called |
| Latency and cost | Illustrative: each run's `ms` and its $0.004 cost are typed into the demo |
| Rates and percentiles | Computed by the real `scorecard` code from those runs |
| Uncertainty | Not reported. p95 of six runs is the slowest run |

### Chapter 28: the profiling demo (section 28.13, `ch28_profile.py`)

| Condition | In this demo |
| --- | --- |
| Model | Simulated. No model runs; each `chat qwen-32b` span lasts 250 ms plus about 12 ms per output token |
| Size | 292 runs in 10 minutes, 2,044 spans, 600 resource samples (one per second), 58,494 stack samples (20 per second) |
| Concurrency | A run starts about every 2 seconds, so runs overlap. Only the injected incidents create contention |
| Trials | One generated run, `seed=28`, deterministic |
| Cache | None modeled |
| Uncertainty | Not reported as intervals: p50 and p95 per group, Spearman's r and lift, with `diagnose`'s thresholds |
| Numbers | Illustrative. The traffic and both incidents are generated, so you know the right answer in advance |

### Chapter 29: performance, load, benchmark and economics

#### Section 29.5, the concurrency sweep (`ch29_perf.py`)

It runs on any machine, because it's a simulator, but on real threads and a real (scaled) clock, so thread scheduling makes the rows at high concurrency vary a little from run to run. The simulated model is priced as Claude Sonnet 5 (`PRICES`). Each call sends a 3,000-token prefix, a 60-token question and the history so far, and writes 60–240 output tokens; each tool result adds 300–900 tokens. The test is a closed loop at 1, 2, 4, 8 and 16 in flight on four model slots, with 48 tasks per level, no warm-up and no fixed duration: a level ends when its 48 tasks do. Every level starts with a cold, fresh prompt cache. Cost per success includes $2 an hour of infrastructure and a person reviewing 0.5% of tasks for 3 minutes at $60 an hour. Each level runs once, so p50, p95, p99, throughput and cost are point estimates with no interval; the error rate is the share of tasks that gave up (the `ok` column). The numbers are measured on the simulator and illustrate the mechanics; they predict nothing about a real model.

#### Section 29.6, the open-loop load test (`ch29_loadtest.py`)

`fake_agent` runs on any machine on a real `asyncio` clock: 2–4 waits of 0.3–1.2 seconds each, standing in for model calls, with no model, tokens, cache or cost modelled. Requests arrive open-loop at random (Poisson) times averaging the offered rate, for 20 seconds by default, with 20 slots and a 60-second timeout. There's no warm-up and each rate runs once. Arrival times are seeded, but the fake agent's waits aren't, so numbers move a little between runs. The report gives p50, p95, max, mean, achieved throughput and the error count, without intervals. The figures in section 29.6 are illustrative: they show how the harness behaves, not how any agent performs.

#### Section 29.8, the four benchmark experiments (`ch29_benchmark.py`, simulator)

| Condition | E1, E2 and E3 | E4 |
| --- | --- | --- |
| Hardware | Simulator on a virtual clock, any machine (`config.json` records the one used) | The same |
| Model and pricing | Simulated models priced as Claude Sonnet 5 (`PRICES`); E3 adds a smaller one priced as Claude Haiku 4.5 | Sonnet-priced simulated model |
| Tokens | Whatever each design sends: about 300 to 1,300 per task; 20–120 output tokens per call; E3's long rows add an 8,000-token system prompt (about 25,000 per task) | About 1,200 per task (1,300 with tool failures) |
| Tools | 250 ms median latency, no failures | 250 ms median; 0% and 10% transient failures; a turn's calls run at the same time |
| Concurrency and arrivals | One task at a time, one after another | Closed loop at 1, 2, 4, 8 and 16 in flight on four model slots; 10 s deadline for a slot |
| Warm-up and duration | First task of each configuration discarded; a fixed number of tasks, no fixed duration | No warm-up; a fixed number of tasks per level |
| Cache | Not modelled: every token is priced as uncached input | Not modelled |
| Trials | 20 one-part questions × 5 repetitions = 100 per row (E1, E3); 6 multi-part × 5 = 30 (E2) | 20 questions (14 one-part, 6 multi-part) × 3 draws = 60 per level |
| Reported | Success, error rate (0% in every row), p50/p95/p99, model calls, tokens, $ per task and per success | The same, plus throughput, goodput and time waiting for a slot |
| Cost per success | Simulated at list prices; nothing billed | The same |
| Uncertainty | 95% Wilson interval on success; latency and cost are point estimates; reruns are identical | The same |
| Status | Measured on the simulator; illustrative for a real model | The same |

#### Section 29.9, the business case (`ch29_economics.py`)

The conditions are simpler than a benchmark's, because nothing runs under load. There's no hardware, concurrency, arrival pattern, warm-up or trial count: the case is arithmetic on one month of 18,000 conversations. The model cost per turn is E3's cost per task for the Sonnet-priced simulated model, with no prompt caching; tools, infrastructure, people and failures are assumptions. Latency isn't modelled. Uncertainty is shown as break-even points and a ±20% sensitivity table rather than intervals, and every result is illustrative.

