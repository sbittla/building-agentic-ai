# Benchmark: sim backend

Model `claude-sonnet-5` (small: `claude-haiku-4-5`), commit `679be0321037`, data `2b4e6000ed680c6a`, prompts `44cf983056924987`, seed 29, 5 repetitions after 1 discarded warm-up tasks, tool latency 250 ms, Linux-6.18.44-fc-v70-x86_64-with-glibc2.39, 2 CPUs, Python 3.13.16, 2026-10-05 01:38:56 UTC. Total spent: $11.42.

Rerun: `python ch29_benchmark.py --quiet`

Simulated model: these numbers follow from the assumptions in `SIM_MODELS` (latency, error rates), so they show the mechanics of each design exactly, not how good a real model is. Same seed, same numbers, on any machine.

## E1. Architecture: workflow, one agent, a team

| Configuration | Tasks | Success (95% CI) | Errors | p50 s | p95 s | p99 s | Model calls | Tokens | $/task | $/success |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| workflow | 100 | 97% (92%–99%) | 0% | 2.5 | 3.7 | 4.2 | 2.1 | 304 | $0.0012 | $0.0012 |
| agent | 100 | 97% (92%–99%) | 0% | 3.9 | 4.6 | 5.6 | 3.0 | 1,109 | $0.0031 | $0.0032 |
| multi-agent | 100 | 97% (92%–99%) | 0% | 6.2 | 7.1 | 7.7 | 5.0 | 1,325 | $0.0041 | $0.0043 |

## E2. Tool execution: one after another, or at the same time

| Configuration | Tasks | Success (95% CI) | Errors | p50 s | p95 s | p99 s | Model calls | Tokens | $/task | $/success |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| tools sequential | 30 | 93% (79%–98%) | 0% | 4.9 | 5.5 | 6.0 | 3.0 | 1,229 | $0.0038 | $0.0041 |
| tools parallel | 30 | 93% (79%–98%) | 0% | 4.6 | 5.2 | 5.5 | 3.0 | 1,229 | $0.0038 | $0.0041 |

## E3. Model size and context length

| Configuration | Tasks | Success (95% CI) | Errors | p50 s | p95 s | p99 s | Model calls | Tokens | $/task | $/success |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-haiku-4-5, base context | 100 | 93% (86%–97%) | 0% | 2.0 | 2.8 | 3.0 | 3.1 | 1,145 | $0.0016 | $0.0017 |
| claude-haiku-4-5, +8,000 tokens context | 100 | 93% (86%–97%) | 0% | 2.6 | 3.6 | 3.8 | 3.1 | 25,772 | $0.0262 | $0.0282 |
| claude-sonnet-5, base context | 100 | 98% (93%–99%) | 0% | 3.9 | 4.4 | 5.4 | 3.0 | 1,110 | $0.0031 | $0.0032 |
| claude-sonnet-5, +8,000 tokens context | 100 | 98% (93%–99%) | 0% | 5.0 | 5.5 | 6.8 | 3.0 | 25,259 | $0.0514 | $0.0525 |

## E4. Load: tasks in flight, workload mix and transient failures

| Configuration | Tasks | Success (95% CI) | Errors | p50 s | p95 s | p99 s | Model calls | Tokens | $/task | $/success | Throughput /s | Goodput /s |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 in flight, 0% tool failures | 60 | 95% (86%–98%) | 0% | 3.9 | 4.9 | 6.8 | 3.0 | 1,157 | $0.0033 | $0.0035 | 0.24 | 0.23 |
| 2 in flight, 0% tool failures | 60 | 95% (86%–98%) | 0% | 3.9 | 4.9 | 6.8 | 3.0 | 1,157 | $0.0033 | $0.0035 | 0.48 | 0.45 |
| 4 in flight, 0% tool failures | 60 | 95% (86%–98%) | 0% | 3.9 | 4.9 | 6.8 | 3.0 | 1,157 | $0.0033 | $0.0035 | 0.94 | 0.89 |
| 8 in flight, 0% tool failures | 60 | 95% (86%–98%) | 0% | 6.8 | 8.2 | 10.6 | 3.0 | 1,157 | $0.0033 | $0.0035 | 1.11 | 1.05 |
| 16 in flight, 0% tool failures | 60 | 95% (86%–98%) | 0% | 13.5 | 15.2 | 20.3 | 3.0 | 1,157 | $0.0033 | $0.0035 | 1.11 | 1.05 |
| 1 in flight, 10% tool failures | 60 | 95% (86%–98%) | 0% | 4.0 | 7.1 | 7.8 | 3.3 | 1,295 | $0.0037 | $0.0039 | 0.22 | 0.21 |
| 2 in flight, 10% tool failures | 60 | 95% (86%–98%) | 0% | 4.0 | 7.1 | 7.8 | 3.3 | 1,295 | $0.0037 | $0.0039 | 0.44 | 0.41 |
| 4 in flight, 10% tool failures | 60 | 95% (86%–98%) | 0% | 4.0 | 7.1 | 7.8 | 3.3 | 1,295 | $0.0037 | $0.0039 | 0.85 | 0.81 |
| 8 in flight, 10% tool failures | 60 | 95% (86%–98%) | 0% | 7.1 | 11.3 | 12.7 | 3.3 | 1,295 | $0.0037 | $0.0039 | 0.98 | 0.93 |
| 16 in flight, 10% tool failures | 60 | 95% (86%–98%) | 0% | 13.9 | 20.7 | 23.4 | 3.3 | 1,295 | $0.0037 | $0.0039 | 1.01 | 0.96 |

