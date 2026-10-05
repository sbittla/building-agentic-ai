# Migration notes

What to change in your own code, or in your reading, when you move from one tag of this repository to the next. Versions are in [COMPATIBILITY.md](COMPATIBILITY.md); the full list of changes is in [CHANGELOG.md](CHANGELOG.md).

## edition-1.0 → edition-1.1

Code from the first printing runs unchanged on edition-1.1's versions; the library pins didn't change. What moved:

| In edition-1.0 | In edition-1.1 |
| --- | --- |
| Sections 15.4–15.7 (long-running work, gateways, registries, company authorization) | Sections 30.8–30.11 |
| Section 15.8, extensions and the road ahead | Section 15.4 |
| `ch15_gateway.py`, `ch15_jobs_server.py` | `ch30_gateway.py`, `ch30_jobs_server.py` |
| Exercises 15.5, 15.6, 15.7 | Exercises 30.9, 30.10, 30.11 |
| `solutions/exercises/ch00/sol_chNN_*.py` (and `ch01/`, `ch03/`) | `solutions/exercises/chNN/sol_chNN_*.py` |
| `ch03_tool_search.py` imported tools from Chapters 4–8 | It uses only Chapter 3's tools and a catalogue of stand-ins; exercise 3.7 changed to match |

If you're reading the first printing, stay on `edition-1.0` for exercise numbers that match your book, or use the table above.
