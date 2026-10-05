# Changelog

What changed in the book and this repository, newest first. Each book printing is matched by a tag; see "Book editions and code versions" in [README.md](README.md). Corrections to a printed edition are listed in [ERRATA.md](ERRATA.md).

## edition-1.1: corrected printing (October 2026)

### Book
- **New material:** sections 1.9 (kinds of agents), 1.10 (the agent lifecycle), 4.10 (writing the system prompt), 30.12 governance and 30.13 (the agent lifecycle in production); the interlude *Measuring an Agent* (after Chapter 8, exercises M.1–M.3); an Afterword; reference cards 10 and 11.
- **Moved:** Chapter 15's long-running tools, gateways, registries and company authorization are now sections 30.8–30.11, after the chapters they depend on. Exercises 15.5–15.7 became 30.9–30.11; `ch15_gateway.py` and `ch15_jobs_server.py` became `ch30_gateway.py` and `ch30_jobs_server.py`. Section 24.10 moved to the Afterword.
- **Section 3.6** (tool search) no longer imports code from later chapters.
- **Continuity:** "The support agent so far" in 21 chapters; a prompt-injection caution in Chapter 6; back-links where topics return; "routing" and "memory" disambiguated.
- **Signposts:** prerequisites, Architect's Takeaways and reading paths corrected; exercise counts are computed from `course/exercises.json`.
- **Captions:** every table, figure and listing in the chapters and interludes is numbered, with alt text for every figure.
- **Opening pages:** a two-page Contents at a Glance before the full Contents; Acknowledgments and About the Author moved to the back; "How to Use This Book" reordered so who it's for, what you'll build and the reading paths come first, then setup and your first agent.
- **Security regression scenarios (section 25.10):** fifteen attacks, each with the control that stops it, a deterministic test, its result and the residual risk; which defenses are deterministic and which depend on the model.
- **Benchmark (section 29.8, exercise 29.7):** workflow vs agent vs multi-agent, sequential vs parallel tools, small vs large model and context, concurrency and failures, with p50/p95/p99, throughput, success, tokens and cost per success. The published run is reproducible from its seed.
- **Case Study: The Support Agent in Production**, before the capstones: requirements, threat model, design per request type, evaluation data, test findings, load test, deployment, an incident and its rollback.
- **Getting started:** a free five-minute quick start (`./course.sh quickstart`, no key and no download), what your computer needs, what to do when the first commands fail, a path from first agent to production, and why your results may differ on the local model. Chapters 0, 1 and 4 show the output you should see and the common errors.
- **Durability:** the copyright page and preface name the matching tag; this changelog, [ERRATA.md](ERRATA.md), [COMPATIBILITY.md](COMPATIBILITY.md) and [MIGRATION.md](MIGRATION.md) are referenced from Appendix G.

### Repository
- Exercises: 231 → 237 (M.1–M.3, 1.9, 29.7 and 30.8 added).
- `./course.sh quickstart` and `course/code/quickstart.py`.
- `course/code/ch29/ch29_benchmark.py` with a simulator backend (no key, exact replay) and `claude` and `local` backends; the published simulator run is in `benchmarks/sim-edition-1.1/`.
- Verification evidence: `dev/verify.py` records passed, failed, error and skipped tests separately, each with the commit, the hash of `requirements.lock` and the environment, in `verification/`. Tests that need the course image are skipped with a reason outside it instead of failing.
- Security: `solutions/tests/security_scenarios.json` and `test_security_scenarios.py`; `dev/security_mutations.py` removes each security control in turn and checks that a test fails (`verification/SECURITY.md`).
- CI: the reference check and the generated docs run on every branch; the full suite runs in the course image and uploads its results; an `edition-*` tag publishes a release with them.
- [COMPATIBILITY.md](COMPATIBILITY.md): a dated matrix of every pinned version, model, price and protocol version, checked against `requirements.lock`, the `Dockerfile` and the code by `dev/check_references.py`.
- `sol_chNN_*.py` solution files moved into their own chapter folders (they had been filed under `ch00`, `ch01` and `ch03`).
- `dev/check_references.py`: checks every exercise id, file, command and cross-reference in the book and docs; runs in CI.
- README counts and EXERCISE_INDEX.md are generated from `course/exercises.json`, and CI fails if they're stale.

## edition-1.0: first printing (September 2026)
- 31 chapters, 5 interludes, 231 exercises, 6 capstones.
