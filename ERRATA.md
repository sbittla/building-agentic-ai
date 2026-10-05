# Errata

Mistakes found in a printed edition of *Building Agentic AI Systems*, newest printing first. Each entry says where the mistake is, what's wrong, and what to do instead, so a reader of that printing can correct their copy without guessing.

How corrections work:
- A printing's tag (`edition-1.0`, `edition-1.1`, ...) never changes. If the code at a tag has a bug, the fix goes on `main` and the entry here says which commit or tag has it, so the code still matches the book you're holding.
- A correction that changes what an exercise asks for, or how the code behaves, goes into the next printing and the [CHANGELOG](CHANGELOG.md), not only into this list.
- Version changes in the world (new models, SDK releases, a new MCP specification) are not errata; [COMPATIBILITY.md](COMPATIBILITY.md) tracks them.

To report a mistake, open an issue on the repository with the printing, the page or section, and what you expected. Include `./course.sh check` output for anything about the code.

## Corrected printing, October 2026 (`edition-1.1`)

No errata reported yet.

## First printing, September 2026 (`edition-1.0`)

All of these are fixed in the corrected printing and in `edition-1.1`.

| Where | What's wrong | Correction |
| --- | --- | --- |
| Several chapter titles and sentences | A difficulty label leaked into the text, as in "What an Agent Is — Beginner(and Isn't)" | Ignore the label: "What an Agent Is (and Isn't)" |
| Appendix F, and exercise paths in some chapters | Exercise files are described as `workspace/exercises/chNN/...` | `./course.sh ex` creates `workspace/exercises/exN_M_*.py`, one flat folder. Only the solutions folder has chapter subfolders |
| Appendix F | `PYTHONPATH` lists the same folder twice | List it once |
| "How to Use This Book", the table of model labels | The counts are 81, 83, 4 and 5, which add up to 173, not 231 | No model: 114. qwen3.5:9b or Claude: 103. Claude recommended: 9. Claude only: 5 |
| Prerequisites in 23 chapters | Some list chapters the chapter doesn't build on, or "basic understanding of" topics the book hadn't taught yet | See the corrected printing; for example, Chapter 12 builds on Chapter 2, Chapter 7 (the weather tools it packages) and the Python interlude |
| Architect's Takeaways in Chapters 7, 14, 23, 24 and 25 | Some takeaways belonged to a different chapter | See the corrected printing |
| Section 3.6 | `ch03_tool_search.py` imports tools from Chapters 4–8, which you haven't built yet | Fixed in `edition-1.1`: it uses Chapter 3's tools and a catalogue of stand-ins. On `edition-1.0`, run it after Chapter 8 |
| Section 15.4 (long-running work) onwards | Uses durable jobs, agent identity and tracing from Chapters 19, 26 and 28 before you reach them | Read sections 15.4–15.7 after Chapter 28; the corrected printing moves them to 30.8–30.11 |
| Section 30.9 | The reference architecture has a different list of layers from section 1.7 | Both use the 11 layers in section 1.7 |
