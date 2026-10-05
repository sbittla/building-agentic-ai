# Changelog

What changed in the book and this repository, newest first. Each book printing is matched by a tag; see "Book editions and code versions" in [README.md](README.md). Corrections to a printed edition are listed in [ERRATA.md](ERRATA.md).

## edition-1.1: corrected printing (October 2026)

### Book
- **New material:** sections 1.9 (kinds of agents), 1.10 (the agent lifecycle), 4.10 (writing the system prompt), 30.12 governance and 30.13 (the agent lifecycle in production); the interlude *Measuring an Agent* (after Chapter 8, exercises M.1–M.3); an Afterword; reference cards 10 and 11.
- **Moved:** Chapter 15's long-running tools, gateways, registries and company authorization are now sections 30.8–30.11, after the chapters they depend on. Exercises 15.5–15.7 became 30.9–30.11; `ch15_gateway.py` and `ch15_jobs_server.py` became `ch30_gateway.py` and `ch30_jobs_server.py`. Section 24.10 moved to the Afterword.
- **Section 3.6** (tool search) no longer imports code from later chapters.
- **Continuity:** "The support agent so far" in 21 chapters; a prompt-injection caution in Chapter 6; back-links where topics return; "routing" and "memory" disambiguated.
- **Signposts:** prerequisites, Architect's Takeaways and reading paths corrected; exercise counts are computed from `course/exercises.json`.
- **Captions:** every table, figure and listing in the chapters and interludes is numbered; Lists of Figures and Tables after the Contents; alt text for every figure.

### Repository
- Exercises: 231 → 236 (M.1–M.3, 1.9 and 30.8 added).
- `sol_chNN_*.py` solution files moved into their own chapter folders (they had been filed under `ch00`, `ch01` and `ch03`).
- `dev/check_references.py`: checks every exercise id, file, command and cross-reference in the book and docs; runs in CI.
- README counts and EXERCISE_INDEX.md are generated from `course/exercises.json`, and CI fails if they're stale.

## edition-1.0: first printing (September 2026)
- 31 chapters, 5 interludes, 231 exercises, 6 capstones.
