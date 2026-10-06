# Migration notes

What to change in your own code, or in your reading, when you move from one tag of this repository to the next. Versions are in [VERSION_MATRIX.md](VERSION_MATRIX.md); the full list of changes is in [CHANGELOG.md](CHANGELOG.md).

## edition-1.0 → edition-1.1

Code from the first printing runs unchanged on edition-1.1's versions; the library pins didn't change. What moved:

| In edition-1.0 | In edition-1.1 |
| --- | --- |
| Sections 15.4–15.7 (long-running work, gateways, registries, company authorization) | Sections 30.8–30.11 |
| Section 15.8, extensions and the road ahead | Section 15.4 |
| `ch15_gateway.py`, `ch15_jobs_server.py` | `ch30_gateway.py`, `ch30_jobs_server.py` |
| Exercises 15.5, 15.6, 15.7 | Exercises 30.9, 30.10, 30.11 |
| Section 30.8, from one agent to an agent platform | Section 30.12 |
| Section 30.9, the end-to-end reference architecture | Section 30.15 |
| Section 24.10, where the field is going | The Afterword; 24.10 is now "Skills as software" |
| `solutions/exercises/ch00/sol_chNN_*.py` (and `ch01/`, `ch03/`) | `solutions/exercises/chNN/sol_chNN_*.py` |
| `ch03_tool_search.py` imported tools from Chapters 4–8 | It uses only Chapter 3's tools and a catalogue of stand-ins; exercise 3.7 changed to match |

If you're reading the first printing, stay on `edition-1.0` for exercise numbers that match your book, or use the table above.

### New in edition-1.1 (nothing to change in your code)

These are additions; code written against edition-1.0 keeps working:

| New section | New module | New exercise |
| --- | --- | --- |
| 17.10 Memory is a security boundary | `ch17_memory_security.py` | 17.9 |
| 21.10 Does the team pay for itself? | `ch21_coordination.py` | 21.7 |
| 23.9 Reliability engineering for computer use | `ch23_reliability.py` | 23.7 |
| 24.10 Skills as software | `ch24_skill_registry.py` | 24.10 |
| 25.11 Sizing the risk of an agent | `ch25_risk.py` | 25.7 |
| 26.9 Discovery, 26.10 Trust across organizations | `ch26_discovery.py` | 26.7 |
| 28.13 Continuous profiling | `ch28_profile.py` | 28.8 |
| 29.8 A reproducible benchmark, 29.9 Agent economics | `ch29_benchmark.py`, `ch29_economics.py` | 29.7, 29.8 |
| 30.14 The agent improvement loop | `ch30_improvement_loop.py` | 30.12 |
