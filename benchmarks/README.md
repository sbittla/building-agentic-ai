# Benchmark results

Published runs of `course/code/ch29/ch29_benchmark.py` (section 29.8 of the book). Each folder is one run:

| File | What it holds |
| --- | --- |
| `config.json` | Everything needed to rerun it: commit, backend, model ids, simulator assumptions, prompts hash, data fingerprint, seed, repetitions, warm-up, tool latency, hardware, Python, the exact command |
| `raw.jsonl` | One line per task: experiment, configuration, question, right or wrong, latency by part, model calls, tokens, cost, errors |
| `summary.json`, `summary.md` | The tables, with 95% intervals for success |

| Run | Backend | What it tells you |
| --- | --- | --- |
| `sim-edition-1.1/` | Simulator | The mechanics of each design, exactly: same seed, same numbers on any machine. Not how good a real model is. The book's Tables 29.x come from this run. |

## Adding a run with a real model

From the kit folder, with your key in `.env` (Claude) or the local model started (`./course.sh local up`):

```bash
./course.sh python ch29_benchmark.py --backend claude --budget 10   # about $10 for the full run
./course.sh python ch29_benchmark.py --backend local                # free; hours on a CPU
./course.sh python ch29_benchmark.py --backend claude --quick       # about $1: one repetition, 8 questions
```

Each writes `workspace/benchmarks/<backend>-<time>/`. To publish one, copy the folder here, rename it (`claude-edition-1.1/`), and add a row to the table above. Compare runs only when their `config.json` matches on everything but what you changed, and read differences against the confidence intervals: a difference inside the overlap isn't one.
