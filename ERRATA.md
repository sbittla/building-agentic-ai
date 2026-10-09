# Errata

Mistakes found in a printed edition of *Building Agentic AI Systems*, newest printing first. Each entry says where the mistake is, what's wrong, and what to do instead, so a reader of that printing can correct their copy without guessing.

How corrections work:
- A printing's tag (`edition-1.0`, `edition-1.1`, ...) never changes. If the code at a tag has a bug, the fix goes on `main` and the entry here says which commit or tag has it, so the code still matches the book you're holding.
- A correction that changes what an exercise asks for, or how the code behaves, goes into the next printing and the [CHANGELOG](CHANGELOG.md), not only into this list.
- Version changes in the world (new models, SDK releases, a new MCP specification) are not errata; [VERSION_MATRIX.md](VERSION_MATRIX.md) tracks them.

To report a mistake, open an issue on the repository with the printing, the page or section, and what you expected. Include `./course.sh check` output for anything about the code.

## Fourth printing, October 2026 (`edition-1.3`)

No errata reported yet.

## Third printing, October 2026 (`edition-1.2`)

These are fixed in the fourth printing and in `edition-1.3`.

| Where | What's wrong | Correction |
| --- | --- | --- |
| Section 25.2 | "Questions 2 and 3 together" expose the lethal trifecta | Questions 1 to 3 together: untrusted content is question 1 |
| Chapter 26, the refund note | Says every refund needs a person | Refunds up to $100 don't; above that, a person approves (as in section 25.11 and the case study) |
| Section 27.6, the scorecard lines | Cost per task and cost per success read as totals | Both are averages: total spend divided by runs, or by successful runs |
| Section 31.5 | The pilot promotes at 10.5 minutes although the brief's target is 9 | The signed pilot criterion is a 30% gain; the 9-minute target belongs to general release |
| Exercise 29.8 (kit text) | E3's figures are described as measurements of Claude models | They are simulator figures, priced as Haiku 4.5 and Sonnet 5 |
| The case study, capacity plan | A limit of twelve in flight contradicts the knee E4 measures | Two deployments of four in flight each, derived from E4 (fourth printing) |
| Section 1.8, the route table | Part 10 is missing | Part 10: can it work in someone else's business? Chapter 31 |

## Second printing, October 2026 (`edition-1.1`)

No errata reported yet.

## First printing, September 2026 (`edition-1.0`)

All of these are fixed in the second printing and in `edition-1.1`.

| Where | What's wrong | Correction |
| --- | --- | --- |
| Several chapter titles and sentences | A difficulty label leaked into the text, as in "What an Agent Is — Beginner(and Isn't)" | Ignore the label: "What an Agent Is (and Isn't)" |
| Appendix F, and exercise paths in some chapters | Exercise files are described as `workspace/exercises/chNN/...` | `./course.sh ex` creates `workspace/exercises/exN_M_*.py`, one flat folder. Only the solutions folder has chapter subfolders |
| Appendix F | `PYTHONPATH` lists the same folder twice | List it once |
| "How to Use This Book", the table of model labels | The counts are 81, 83, 4 and 5, which add up to 173, not 231 | No model: 114. qwen3.5:9b or Claude: 103. Claude recommended: 9. Claude only: 5 |
| Prerequisites in 23 chapters | Some list chapters the chapter doesn't build on, or "basic understanding of" topics the book hadn't taught yet | See the second printing; for example, Chapter 12 builds on Chapter 2, Chapter 7 (the weather tools it packages) and the Python interlude |
| Architect's Takeaways in Chapters 7, 14, 23, 24 and 25 | Some takeaways belonged to a different chapter | See the second printing |
| Section 3.6 | `ch03_tool_search.py` imports tools from Chapters 4–8, which you haven't built yet | Fixed in `edition-1.1`: it uses Chapter 3's tools and a catalogue of stand-ins. On `edition-1.0`, run it after Chapter 8 |
| Section 15.4 (long-running work) onwards | Uses durable jobs, agent identity and tracing from Chapters 19, 26 and 28 before you reach them | Read sections 15.4–15.7 after Chapter 28; the second printing moves them to 30.8–30.11 |
| Section 30.9 | The reference architecture has a different list of layers from section 1.7 | Both use the 11 layers in section 1.7 |
