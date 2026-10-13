# Change ledger: First edition (book release 1.0.0)

The manuscript changes made while preparing the First edition, with the reason for each. Changes are grouped as **technical**, **editorial** or **layout**. The working base was the shortened manuscript (internal readability pass, October 2026). The longer edition-1.2 snapshot (commit `cf205bd`) was kept for comparison, and every substantial deletion was judged by four rules:
- **Restore** what explains a difficult concept, demonstrates a failure, gives a critical safety caveat or makes an exercise reproducible.
- **Leave out** what only repeats.
- **Move to the repository** reference material that changes often.
- **Rewrite** what was useful but outdated.

For volatile facts (models, prices, protocols, SDKs), see [CLAIMS_AUDIT.md](CLAIMS_AUDIT.md). For the release record, see [RELEASE_MANIFEST.json](RELEASE_MANIFEST.json).

## Release identity (technical)

| Where | Change | Reason |
| --- | --- | --- |
| Copyright page (`course/build.js`) | Now reads "First edition: 2026", names the matching tag `book-v1.0.0`, points to ERRATA.md and VERSION_MATRIX.md, and states plainly that some examples use a paid API while others run free on a local model. The code license now matches the repository (all rights reserved, with permission to use the code for learning) | The book had not been published, so earlier internal snapshots must not be described as printings. The paid-API sentence was misleading for readers on the free path |
| Preface, How to Use This Book, Appendix G | The edition paragraph, the checkout commands (`git checkout book-v1.0.0`, `git describe --tags`) and the release table now refer to this release | Readers need the exact code that matches the book |
| README, VERSION_MATRIX, CHANGELOG, MIGRATION, ERRATA, CI | Release table, development-snapshot note, release-candidate status, `book-v*` release workflow | The same release identity everywhere |

## Learning support added (editorial)

| Where | Change | Reason |
| --- | --- | --- |
| How to Use This Book | New material: the three kinds of exercise (written answer, executable, model-dependent), where the level steps up (Parts 5, 7 and 9), and "Getting help" | The review's R03 structure; beginners need to know which activities need paid usage, an app or a person |
| End of every part | A "Ready for the next part?" box | Makes the move from beginner to production explicit |
| Testing interlude, Chapters 4, 27 and 28 | Worked examples of reading a pytest failure, an agent trace, an evaluation result and a production trace | Readers need to interpret logs, traces, test failures and evaluation results, not only produce them |
| Chapters 1–31 (major chapters) | "Before you move on": what to understand, what to build, the exercise that proves it, one failure to provoke, one decision to defend | Measurable chapter outcomes (R05, R13) |
| Chapter 24 (24.9) | Dated decision matrix comparing a custom loop, frameworks, provider runtimes and managed services | Readers choosing a production stack |
| Appendix M | Production Deployment Reference, covering multi-tenant isolation, secret rotation, retention, scanning, backups, incident ownership and rollback criteria | The kit is not production-hardened; readers need to know what production adds |
| Appendix G | "What 'verified' means": deterministic tests, live-model runs and production readiness | So that a deterministic pass is never read as production evidence |
| Index | New index, generated from the final layout (`course/make_index.py`); curated in release candidate 2 (below) | A reference book needs one (R15) |

## Evidence for claims (technical)

| Where | Change | Reason |
| --- | --- | --- |
| Chapters 25 and 26 | Each defense shows the attack path and the enforcing code, names the regression scenario (S1–S14) that proves it, and says what that proof covers: a scripted model that fully obeys the attacker | A prompt instruction must never be presented as a security boundary (R09) |
| 21.10, 27, 28.13, 29.5–29.9 | Conditions for each benchmark: model or simulator, sizes, concurrency, arrival pattern, cache, trials, uncertainty, and whether each figure is measured, estimated or illustrative. Chapter 29 adds a warning that its thresholds are examples, not targets | Results must be reproducible and must not be read as universal rules (R09, P2) |
| 15.4 | The MCP protocol now says servers must implement `server/discover` and send cache hints, while calling `server/discover` and honoring the hints are optional for clients | Corrected against the 2026-07-28 specification changelog (CLAIMS_AUDIT.md) |
| Appendix E | The tokenizer figure is now "up to about 35% more tokens … depending on the content" | Corrected against Anthropic's announcement (CLAIMS_AUDIT.md) |
| Appendix E | States its assumptions: all paid exercises priced on Claude, no prompt caching, no automatic client retries, and a doubling factor for your own reruns | Cost figures must explain what they assume (R08) |
| Appendix H, Appendix B | Which exercises need paid Claude (3.7, 16.7, 24.6, 24.7), which need Claude Desktop (12.5), a GitHub token (14.3, 14.4), a cloud host (30.7) or a person (3.1, and every approval gate) | Paid versus local clarity (R02, R11) |

## Restored from the longer snapshot (editorial, by chapter)

| Chapter | Restored | Reason |
| --- | --- | --- |
| 1 | That a thinking block's text is hidden by default; that a `max_tokens` of a few hundred can run out before the answer; local-model differences in exercise output; why Optimize comes after Evaluate; that a committed key stays in Git history | Concept, failure, reproducibility, safety |
| 2–3 | That the model never runs anything itself; that strict tools fix the input's shape but not its meaning; that one eval pass is only a rough reading | The split between model and code; methodology |
| 4 | A five-step walkthrough of one pass through the loop, and which decisions are the model's | The first agent must be understood at every step |
| 5 | The "who changes it" row (history against tools); stored memory returns attacker-planted text | Concept, safety |
| 7–8 | The contract for tools that change things (19.5, 30.7); how many runs a gold-answer comparison needs | Safety, methodology |
| 9–11 | What the approver saw; no way back without undo; how `run_tests` and `should_stop` decide; one subagent's exception ending the whole run | Safety, failure |
| 12–15 | Protocol semantics separated from SDK behavior throughout; the attack on tool output step by step; what the production pattern leaves out | MCP accuracy, safety |
| 16–18 | The five-part system prompt table (exercise 16.2 needs it); who decides compaction; how to choose between context, memory and knowledge | Reproducibility, how to choose |
| 19–24 | Which errors are transient (19.4); when to replan; A2A context ids; paired comparisons with the same random numbers; what each listing is (demo, prototype or production pattern) | Methodology, protocol behavior, maturity labels |
| 25–28 | Quarantine limits; that `gaps` trusts its input; that revocation and audit stores live in memory in the kit; how `misread_result` is detected | Safety, deployment limits |
| 29–31 | Little's law at 8 in flight; cache expiry while queued; how the simulator works; protocol requirements for remote MCP; the mix-up attack and issuer validation; retiring an agent; the known-limitations handoff item | Methodology, attack and defense, deployment limits |

## Release candidate 2 (editorial)

| Where | Change | Reason |
| --- | --- | --- |
| Index (`course/index_terms.json`, `course/make_index.py`) | Rebuilt from a curated list of about 290 terms with sub-entries and cross-references. Each sense is searched only in the chapters that teach it, the glossary pages are excluded, and at most six page ranges are kept per entry | The generated index mixed senses ("canary release", "canary token") and listed every glossary mention |
| Preface, How to Use This Book, Chapter 0 | The beginner promise is now precise: complete beginners can finish Parts 0 to 4 with the book alone; later parts assume those exercises | "For complete beginners" overstated what Parts 5–10 ask of a reader |
| Chapters 12, 15, 21, 24, 25, 27, 28, 29 | The full "Conditions behind…" tables moved to `benchmarks/README.md`; each chapter keeps a two- or three-sentence note. Table 29.8 (`bench-conditions`) is cut to seven rows | Reference tables broke the reading flow; the conditions stay reproducible in the repository |
| Chapters 12, 15, 21, 24, 25, 28 | The eight unresolved claims narrowed to what a source or the pinned code confirms | CLAIMS_AUDIT.md: no unresolved rows remain |
| Appendix H | Structured outputs, evals and load tests point to the chapters that now hold them (3, 4, 11, 18, 20, 25, 27; Chapter 27; exercises 29.2 and 29.6) | Stale references from an earlier chapter order |
| Exercises 10.3, 12.7, 27.3 | The setup command is in the text (10.3, 27.3); 12.7 describes the `sitecustomize.py` approach the solution uses | Instructions referred to a "Run line" the printed book doesn't show |
| Case study | Load-test token figure consistent with Chapter 29's E4 (about 1,200 tokens per task) | It said 6,000, which contradicted the benchmark it cites |

## Layout

| Where | Change | Reason |
| --- | --- | --- |
| Listings | Captions give the full repository path (`course/code/chNN/...`) | R06: unambiguous code-to-book mapping |
| Tables | No column narrower than its longest word | Words such as "Portability" were breaking mid-word |
| Contents | "Before you move on" and "Up next" are kept out of the Contents | Keeps the Contents to numbered sections |

## Not changed, by decision

- Section, exercise and listing numbers: unchanged, so every cross-reference and checker still works.
- ISBNs: kept (paperback 979-8177506326, hardcover 979-8177514734), as confirmed by the author.
- Pinned dependency versions: kept, although newer releases exist. The book states what was tested (VERSION_MATRIX.md, CLAIMS_AUDIT.md).
