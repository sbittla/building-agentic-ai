# Changelog

What changed in the book and this repository, newest first. The book's First edition is matched by the release `book-v1.0.0`; see "Book editions and code versions" in [README.md](README.md). Corrections to the published text are listed in [ERRATA.md](ERRATA.md). Later fixes to the code go into patch releases such as `book-v1.0.1`.

## book-v1.0.0: First edition (2026)

The first public release: the book's First edition and the repository release that matches it. 32 chapters and 6 interludes, 249 exercises, seven capstones. `book-v1.0.0-rc2` is the current release candidate; [RELEASE_MANIFEST.json](RELEASE_MANIFEST.json) lists what it was verified with and the gates still open.

### Release candidate 4 manuscript (unreleased)
At most the same 510 pages as rc2 and rc3 (LibreOffice 24.2), with six more figures.
- **Figures in every chapter that lacked one:** what one `course.sh` command does (0), history resent on every call (4), how `_safe` resolves then checks a path (6), `_get_json`'s retry path (7), a disguised write stopping at the read-only connection (8), and who owns the stack from a custom loop to a managed service (24).
- **Reading notes** at the start of Chapters 28, 29 and 30 name the core sections and the advanced ones, so the three longest chapters no longer read as one block.
- **Verified against the Claude API reference** (models cached 2026-10-06): Claude Sonnet 5.5 added to the models that reject forced tools and disabled thinking (3.3, 4.8); effort defaults; the minimum cacheable prefix is 512 to 4,096 tokens; mid-conversation `system` messages don't apply to Claude Sonnet 5 (16.8). `CLAIMS_AUDIT.md` gains three rows.
- **Instructions that didn't work as written** on the local model now carry a model note: 9.3, 20.4, 20.5 and 24.4. Exercise 3.7's text matches its solution; T.1 quotes pytest's real message.
- **Capstones:** every one now has a recorded run. Capstone 2's `describe_table` reports columns it dropped and its approval ignores names a query defines; Capstone 4's verdict is decided in code from failing tests, blocking findings and any deleted test.
- **From the full local-model run:** Chapter 11's `research` recovers a plan sent as one string (it once started a subagent per character) and caps it at 4; its synthesis prompt asks for each claim's source; section 11.3 says so. Model notes on 6.2, 8.5, 18.6 and 30.2, and a sentence in Capstone 3, describe what a small model does there.
- **Exercise boxes:** the per-box "Full brief" line moved into each chapter's exercise intro (94 lines).
- Copy-edit: the author's path replaced by a reader's in two examples, checkpoint wording made consistent, a doubled comma, a duplicated reference, a Haiku 4.5 caveat (no `EFFORT`), `--gpu` in the setup steps, and two GPU rows in Appendix H.

### Release candidate 3 manuscript (unreleased)
Same 510 pages as rc2 (LibreOffice 24.2, the same build). Built from the current repository, so it also carries every correction below.
- **Five new figures** where the text describes a mechanism without showing it: tool search (3.1), cache hints (15.1), the five team topologies (21.1), the customer engagement (31.1) and the case study's release 1.3 incident.
- **"On the local model" tips** in Chapters 14, 17, 25 and 27: a full 8K context, keyword recall missing vague questions, a planner reporting tasks it never added, and an eval gate inside a small model's noise.
- **Page budget:** reference detail and repetition trimmed to keep the page count (Chapter 28's benchmark conditions now point to `benchmarks/README.md`, which already lists them; Appendix M and a few "Up next" paragraphs tightened; the exercise-section intro fits on one line). No exercise text changed.
- `CLAIMS_AUDIT.md`: the two rows still marked open are closed; the corrected wording is in the manuscript.

### Since release candidate 2 (unreleased)
Fixes found by running every exercise on the free local model (qwen3.5:9b) and the Claude-only ones on Claude. Code, tests and two exercise texts changed, so rc2's verification no longer applies; the next candidate needs a fresh full run.
- **Exercise 8.4's instructions** now work: `SYSTEM` describes no tables, and `get_schema`'s description tells the model to read the schema first, so the old "rename the table in `SYSTEM`" never produced a failing query. The exercise now replaces `SYSTEM` and softens `get_schema`'s description.
- **Exercise 17.3** tells you to ask about each fact by its words; a vague "what do you know about me?" can find nothing with keyword search, as section 17.3 explains.
- **Solution 3.7** measures what the chapter claims: each question runs a few steps (a date or a status check can come first), and the calculator and unit converter stay loaded. On Claude both setups reach 10/10, tool search at half the input tokens.
- **Solution 14.4** checks every cited issue number against what GitHub returned and rewrites from a short list when one is invented; 14.3 and 14.4 keep GitHub's results small enough for an 8K context.
- **Solution 25.4** fails closed when the quarantined reader errors, and asks again when the planner reports tasks it never added. **Solution 24.6** counts a skill once when it also reads the skill's extra file.
- **The `best-seller` eval case** (`eval_sql.jsonl`, used in Chapters 27 and 29) counted cancelled orders, so its answer was "Laptop" while an agent told to exclude cancelled orders correctly said "Pen set" and was marked wrong. The reference query now excludes cancelled orders.
- **`./course.sh inspector` now runs servers that import course code.** The MCP Inspector starts a server without `PYTHONPATH`, so exercise 12.6's calculator server (which imports `ch03_tools`) failed with `ModuleNotFoundError`; the weather server worked only because it imports nothing from the course. The command now passes the course's path to the server.
- **Solutions documentation:** `ANSWERS.md` describes what you should see for 12.3–12.6 step by step (including a terminal check with `inspector --cli`) and the new 17.3 questions; `SOLUTIONS.md` describes the changed 3.7, 8.4, 14.4 and 25.4 solutions; `EXERCISE_INDEX.md` and the README's results table are regenerated from the current outputs.
- Stricter run checks (`course/run_checks.json`) for 3.7, 14.4, 17.3 and 24.6, which had passed on output that didn't meet the exercise.
- LOCAL_MODEL.md: what to do when a reply is cut off by a full context, when the agent reports actions it never took, and when an eval gate flips between runs.

### Release candidate 2 (`book-v1.0.0-rc2`)
Manuscript and documentation only; no code, test or environment file changed since `book-v1.0.0-rc1`, so rc1's in-image test run (584 passed, 1 skipped, in the course image on GitHub Actions) still applies and is now the recorded verification.
- **A curated index.** About 290 entries with sub-entries and cross-references (`course/index_terms.json`). Each sense is looked up only in the chapters that teach it, so "canary release" and "canary token" are separate entries, and the glossary pages are left out.
- **Who the book is for, stated precisely.** Complete beginners can finish Parts 0 to 4 with the book alone; later parts assume those exercises are done.
- **Lighter benchmark sections.** The full "conditions" tables in Chapters 12, 15, 21, 24, 25, 27, 28 and 29 moved to `benchmarks/README.md`; each chapter keeps a short note of the conditions that matter for reading its numbers.
- **The eight unresolved claims softened** to what a source or the pinned code confirms (CLAIMS_AUDIT.md).
- Fixed stale cross-references in Appendix H (structured outputs, evals, load tests), exercise 10.3's instructions, exercise 12.7's wording, the measurement interlude reference in Chapter 27 and the case study's token figure (now consistent with Chapter 29's E4).
- README: exercise counts by model (130 no model, 105 local or Claude), the Claude Desktop exception, `serve-a2a` is the Chapter 21 agent, `capstone <1-7>`. VERSION_MATRIX: the local model uses Ollama's `/v1/messages` endpoint.
- `dev/check_links.py` prints one GitHub annotation per broken link in CI.

### Book
- **One edition statement.** The copyright page says "First edition: 2026" and names the matching repository tag, `book-v1.0.0`. The internal snapshots that came before (below) are not described anywhere in the book as printings.
- **Paid and free paths stated plainly.** The copyright page, Chapter 0 and Appendix H say which exercises need the paid API, which run on the free local model, and which need an app, a token or a person.
- **"How to Use This Book"** now covers the full start: choosing a path, setting up, choosing a model, checking out `book-v1.0.0`, running a first example, the three kinds of exercise (written answer, executable, model-dependent) and where to get help.
- **A bridge from beginner to production.** Each part's checkpoint ends with a "Ready for the next part?" box, and the step-ups at Parts 5, 7 and 9 are named. Worked examples show how to read a pytest failure (testing interlude), an agent trace (Chapter 4), an evaluation result (Chapter 27) and a production trace (Chapter 28).
- **"Before you move on"** in every chapter (1–31) lists what to understand, what to build, the exercise that proves it, one failure to provoke and one decision to defend.
- **An index** of the glossary terms and the names readers look up most, generated from the final layout (`course/make_index.py`).
- **Two corrections from the claims audit:** what MCP 2026-07-28 makes optional (15.4) and the Sonnet 5 tokenizer figure (Appendix E).
- **Evidence for claims.** Security sections show the attack and the code that enforces the defense, and name the regression scenario that proves it. Every major benchmark (21.10, 27, 28.13, 29.5–29.9) states its conditions and whether each number is measured, estimated or illustrative. A warning in Chapter 29 says its thresholds are examples, not production targets.
- **A dated decision matrix** in Chapter 24: a custom loop, framework-managed agents, provider runtimes and managed services, compared on control, portability, observability, deployment effort, vendor dependency and cost.
- **Appendix M: Production Deployment Reference.** It covers multi-tenant isolation, secret rotation, data retention, dependency and container scanning, backups and recovery, incident ownership and rollback criteria, and states plainly that the course kit is not production-hardened.
- **Appendix G** explains what "verified" means: deterministic tests, live-model runs and production readiness are three different claims.
- A recovery pass restored explanations, failure demonstrations and safety caveats that the earlier shortening had cut. Code listings name their full repository path.

### Repository
- [CLAIMS_AUDIT.md](CLAIMS_AUDIT.md): 80 version-sensitive claims with location, source, version tested and result. [CHANGE_LEDGER.md](CHANGE_LEDGER.md): every manuscript change for this release and its reason.
- `RELEASE_MANIFEST.json` records the release's tag, commit, lock-file hash, MCP specification and test status. `dev/release_manifest.py --check` runs in CI and fails if the manifest, README, VERSION_MATRIX or the book disagree.
- README: a quick start at the top, the release table with development snapshots marked as such, and the three kinds of verification evidence kept apart.
- VERSION_MATRIX: a reproducibility warning for the two unpinned images (GitHub MCP server, Ollama), what depends on each, the tested fallback and how to pin them by digest.
- A book-issue template (`.github/ISSUE_TEMPLATE/book-issue.yml`).
- `LICENSE`: all rights reserved, with permission to use the code for learning from the book.
- CI publishes book releases on `book-v*` tags; release candidates are marked as prereleases.

## Pre-release development history

These are internal snapshots of the manuscript and code made before the First edition. Their tags (`edition-1.0`, `edition-1.1`, `edition-1.2`) are kept for traceability. They are not published editions or printings.

### Readability pass (internal, October 2026; no tag)

A readability pass: the same chapters, sections, exercises, capstones and code, rewritten to read like a book rather than a reference and shortened by about 15%.

#### Book
- **Every chapter rewritten for voice and pace.** Each one now opens with a concrete situation (a customer email, a failed handoff, green dashboards hiding a failing agent) and closes by setting up the next chapter. Prose replaces many bullet lists, jargon is replaced by plain words or defined at first use, and repeated explanations are cut.
- **Shorter, with nothing removed:** about 165,000 → 140,000 words. The longest chapters lost the most: Chapter 30 (11,100 → 7,300), Chapters 28 and 29 (9,000 → 6,800 each), Chapter 25 (7,400 → 6,500) and the appendices (13,100 → 10,800). Every section number, exercise, figure and listing is unchanged, so references from earlier snapshots still work.
- **Consistency fixes found in the final read:** the refund rule ($100 without a person) now agrees across Chapters 25 and 26 and the case study; the scorecard's cost metrics are defined as averages; Chapter 1's route table includes Part 10; order ids, model names and chapter references corrected where they had drifted; the afterword returns to Chapter 1's opening example.
- "Common mistakes" lists use one plain style; the "Its job in the book" and "Check yourself" lines are folded into the prose.

#### Repository
- `ch30_improvement_loop.py` labels its demo releases `sql-analyst 1.4–1.6`, matching the questions they fail (they were labelled as the support agent).

### Snapshot edition-1.2 (internal, October 2026)

#### Book
- **Part 10, In the Field, and Chapter 31: From Prototype to Customer Production.** A concise chapter on taking an agent into a customer's production: what changes at a customer (31.1); discovery that ends in a measurable problem brief, with a model drafting it from interview notes and code deciding whether it's ready (31.2); the smallest valuable slice (31.3); checking a design against the customer's rules for data residency, model hosting, egress, personal data in logs, retention, sign-in, write access and audit, on top of section 30.7's launch checklist (31.4); pilots against acceptance criteria signed in advance, with a gate that promotes, holds or stops (31.5); handoff (31.6); and the field-to-product loop (31.7). Exercises 31.1–31.5 and a Part 10 checkpoint.
- **Capstone 7: A Customer Deployment.** A whole engagement, from a vague request and a constraint sheet to a signed-off pilot and a handoff, with a scoping score added to the rubric.
- **"In the field" notes** in Chapters 7, 9, 18, 26, 27 and 29: what changes when the same technique meets a customer's environment.
- **Chapter 0 and the Python interlude are marked as an optional beginner path**, with what experienced developers still need from them (sections 0.1 and 0.5).
- **Shorter interludes.** The regular-expression interlude keeps the patterns for validating agent inputs, reading logs and hiding secrets (`re.fullmatch` replaces `re.match`); the SQL interlude keeps the queries Chapter 8 needs. Their broader material and exercises moved to the course kit.
- **Overlaps consolidated.** Chapter 21 no longer repeats Chapter 11's introduction or its "when not to build a team" test; the rule "the model decides, code enforces" is stated once (section 9.3), named in section 22.1 and listed in full in section 25.11, and Chapters 14, 22 and 25 point to it; the measurement interlude, Chapter 27, 28 and 29 form one progression in which the scorecard (section 27.6) defines each metric once.
- **A forward-deployed path** in "How to Use This Book", Part 10 in the preface's map of the book, four new glossary terms, and the afterword's next steps.
- **A one-page roadmap** in "How to Use This Book": every part marked essential, optional or advanced for the beginner, agent engineer, production engineer, architect and forward-deployed engineer, with the capstone for each.
- **Each overlapping chapter states its job** (Chapters 9, 11, 21, 22, 25, 26, 27, 28, 29, 30 and 31, and the measurement interlude): what it adds, and what it leaves to its neighbour.
- **Section 30.5 shows where each deployment setting comes from**: concurrency cap, instance count, timeout, step and token limits, rate limits and SLO targets, each traced to the Chapter 29 measurement behind it.
- The preface states the book's positioning: build agents from first principles, then make them secure, measurable, cost-aware and production-ready.

#### Repository
- `course/code/ch31/ch31_field.py`: the field kit (brief checker, `draft_brief`, slice ranker, design checker, pilot gate, handoff check, field-to-product report). Offline except `draft_brief`.
- `solutions/exercises/ch31/` (31.2–31.5), `solutions/tests/test_ch31_field.py`, and a written answer for 31.1 in `solutions/ANSWERS.md`.
- `solutions/capstones/c7_engagement/`: the request, the constraint sheet, 30 synthetic handover notes (`data.py`) and the engagement record (`engagement.py`); `./course.sh capstone 7`.
- [FIELD_GUIDE.md](FIELD_GUIDE.md): the engagement workflow week by week, discovery, design-review, pilot and handoff checklists, the hard conversations and the demo, moved out of Chapter 31.
- [INTERVIEW_PREP.md](INTERVIEW_PREP.md): a bonus interview guide (the loop, 59 questions with brief answers, five practice cases), kept in the kit instead of the book.
- [EXTRA_PRACTICE.md](EXTRA_PRACTICE.md) and `course/extras.md`: more regex and SQL, and three extra exercises with the usual commands: X.1 (was R.4), X.2 (was S.3) and X.3 (was 31.6 in the draft). S.4 is now S.3. `dev/make_exercises.py` writes them to `course/extras.json`, which `course.py` loads; the book's counts don't include them.
- README: a "Use the code that matches your book" box at the top, and a capstone column in the editions table; `dev/check_references.py` checks both counts.
- `./course.sh run-chapter` records Capstone 7 as needing no model (`OFFLINE_CAPSTONES`); first recorded runs for Chapter 31, Capstone 7 and X.1–X.3 in `solutions/outputs/`.
- `dev/verify.py` groups the Chapter 31 tests as Part 10; verification re-run for this edition (commit, lock hash and environment in [verification/README.md](verification/README.md)).
- Model ids and prices checked against Anthropic's pricing page on 8 October 2026 ([VERSION_MATRIX.md](VERSION_MATRIX.md)).
- Exercises: 246 → 249 in the book, plus 3 extra in the kit.

### Snapshot edition-1.1 (internal, October 2026)

#### Book
- **New material:** sections 1.9 (kinds of agents), 1.10 (the agent engineering lifecycle), 4.10 (writing the system prompt), 30.12 governance and 30.13 (the agent lifecycle in production); the interlude *Measuring an Agent* (after Chapter 8, exercises M.1–M.3); an Afterword; reference cards 10–14.
- **New engineering sections, each with code, tests and an exercise:** 17.10 memory as a security boundary; 21.10 coordination economics (does the team pay for itself?); 23.9 reliability engineering for computer use; 24.10 skills as software (registry, versions, trust, evaluation, rollback); 25.11 the agent risk model and the deterministic control plane; 26.9 discovery (finding a capability is not trusting it) and 26.10 trust across organizations; 28.13 continuous profiling; 29.9 agent economics and payback; 30.14 the agent improvement loop (the reference architecture is now 30.15). Section 26.7 adds signing-key rotation.
- **Signature frameworks:** the agent engineering lifecycle (design, build, secure, evaluate, optimize, deploy, operate, improve) runs through 1.10, every part opener, 30.13, the Afterword and Card 11; the eleven-quality release scorecard (27.6); the agent risk model and the deterministic control plane (22.1, 25.11, Cards 12 and 13).
- **Appendix K, architecture decision records:** seven recurring decisions with defaults, when to switch, consequences and evidence, plus a template. **Appendix L:** a map from every chapter to its exercises, code and capstones.
- **Chapter outcomes:** five or six checkable outcomes per chapter, each tied to an exercise or a section, in [CHAPTER_OUTCOMES.md](CHAPTER_OUTCOMES.md); each chapter's Key takeaways points to them.
- **Learning paths by role** in "How to Use This Book": beginner, agent engineer, production agent engineer and advanced architect, plus a short route for readers in a hurry.
- **Final technical pass (print readiness):** a version banner for MCP at the start of Chapters 12 and 15 and in the Part 5 opener; deprecations worded as "deprecated, not removed, as of 2026-07-28" and checked against the specification announcement, with Dynamic Client Registration added; the agent security boundary diagram and table (section 25.2) referenced from Chapters 1, 14 and 26; a tool contract for mutations with retry semantics for payments, tickets, reservations, provisioning and database writes (section 7.3); concurrency versus durability (the async interlude and section 19.1); answer correctness versus action correctness (section 27.3); "What agents must never decide" (section 25.11, Card 13); memory as validated versus candidate (section 17.10); multi-agent claims framed as measured trade-offs (Chapter 11); API-dependent notes point to VERSION_MATRIX.md and ERRATA.md.
- **Print length (589 to 460 pages, no concept removed):** tighter spacing around paragraphs, headings, tables, boxes and listings; listings show the code that teaches, with helpers as outlines (signature and docstring, `name~` in `@@code`) and the full file in the kit; Summary and Architect's Takeaway merged into **Key takeaways**, Prerequisites and Real-world connection folded into each chapter's opening; Learn more prints up to three Start here links, with every link in `course/learn_more.md` and [RESOURCES.md](RESOURCES.md) (Appendix G no longer reprints them); long exercises print a short brief, and `./course.sh ex <id>` shows the full one (`---kit---` in the manuscript); how to run an exercise and see its solution is said once under each Exercises heading instead of in every box; "How to Use This Book" is shorter, with the setup details, Docker caveats and first-command fixes moved to Appendix A and the local-model settings and full troubleshooting to `LOCAL_MODEL.md`; Chapter 15 points to Chapter 12's MCP version note instead of repeating it.
- **ISBNs** on the copyright page: paperback 979-8177506326, hardcover 979-8177514734.
- **Code maturity labels:** every listing says whether it's a learning demo, a prototype or a production pattern; nothing in the kit claims to be production-hardened.
- **One cost model:** every cost figure comes from `dev/cost_model.py` (COST_MODEL.md); the old "$5–15" and "$35–75" figures are replaced by stated assumptions: about $55–100 for a learner on Claude Sonnet 5, $28–49 for one clean pass.
- **Claims qualified:** the build-or-buy table in 30.12 no longer gives thresholds the book can't support; exercise 27.8 is labelled as a quality gate that fails on purpose.
- **Moved:** Chapter 15's long-running tools, gateways, registries and company authorization are now sections 30.8–30.11, after the chapters they depend on. Exercises 15.5–15.7 became 30.9–30.11; `ch15_gateway.py` and `ch15_jobs_server.py` became `ch30_gateway.py` and `ch30_jobs_server.py`. Section 24.10 moved to the Afterword.
- **Section 3.6** (tool search) no longer imports code from later chapters.
- **Continuity:** "The support agent so far" in 21 chapters; a prompt-injection caution in Chapter 6; back-links where topics return; "routing" and "memory" disambiguated.
- **Signposts:** prerequisites, Architect's Takeaways and reading paths corrected; exercise counts are computed from `course/exercises.json`.
- **Captions:** every table, figure and listing in the chapters and interludes is numbered, with alt text for every figure.
- **Opening pages:** one shorter Contents (four pages instead of nine; each chapter's sections run together in a paragraph under it) and no separate lists of figures and tables; Acknowledgments and About the Author moved to the back; "How to Use This Book" reordered so who it's for, what you'll build and the reading paths come first, then setup and your first agent.
- **Security regression scenarios (section 25.10):** fifteen attacks, each with the control that stops it, a deterministic test, its result and the residual risk; which defenses are deterministic and which depend on the model.
- **Benchmark (section 29.8, exercise 29.7):** workflow vs agent vs multi-agent, sequential vs parallel tools, small vs large model and context, concurrency and failures, with p50/p95/p99, throughput, success, tokens and cost per success. The published run is reproducible from its seed.
- **Case Study: The Support Agent in Production**, before the capstones: requirements, threat model, design per request type, evaluation data, test findings, load test, deployment, an incident and its rollback.
- **Getting started:** a free five-minute quick start (`./course.sh quickstart`, no key and no download), what your computer needs, what to do when the first commands fail, a path from first agent to production, and why your results may differ on the local model. Chapters 0, 1 and 4 show the output you should see and the common errors.
- **Durability:** the copyright page and preface name the matching tag; this changelog, [ERRATA.md](ERRATA.md), [VERSION_MATRIX.md](VERSION_MATRIX.md) and [MIGRATION.md](MIGRATION.md) are referenced from Appendix G.

#### Repository
- Reference documents: [ARCHITECTURE.md](ARCHITECTURE.md), [AGENT_ENGINEERING_PRINCIPLES.md](AGENT_ENGINEERING_PRINCIPLES.md), [DECISION_GUIDE.md](DECISION_GUIDE.md), [AGENT_LIFECYCLE.md](AGENT_LIFECYCLE.md), [SECURITY_MODEL.md](SECURITY_MODEL.md), [PERFORMANCE_MODEL.md](PERFORMANCE_MODEL.md), [EVALUATION_MODEL.md](EVALUATION_MODEL.md), [COST_MODEL.md](COST_MODEL.md), [CURRICULUM_MAP.md](CURRICULUM_MAP.md); COMPATIBILITY.md is now [VERSION_MATRIX.md](VERSION_MATRIX.md), opening with a release matrix.
- Generated and checked in CI: `dev/cost_model.py --check`, `dev/curriculum_map.py --check`; `dev/check_references.py` now also checks the version matrix's and README's exercise counts and every listing's maturity label (`course/code_maturity.json`).
- `ch30_gateway.py` redacts arguments in its audit trail; `ch26_identity.py` rotates signing keys (`rotate_signing_key`); `ch27_scorecard.py --release` prints the eleven-quality scorecard; the benchmark labels simulated cost as simulated.
- `dev/check_links.py` and a weekly `links` workflow check every external link in the book and docs.
- Security mutations: 12 controls, each caught by a test when removed (checkpoints and idempotency added for S15).
- Exercises: 231 → 246 (M.1–M.3, 1.9, 17.9, 21.7, 23.7, 24.10, 25.7, 26.7, 28.8, 29.7, 29.8, 30.8 and 30.12 added; 15.5–15.7 renumbered 30.9–30.11).
- `./course.sh quickstart` and `course/code/quickstart.py`.
- `course/code/ch29/ch29_benchmark.py` with a simulator backend (no key, exact replay) and `claude` and `local` backends; the published simulator run is in `benchmarks/sim-edition-1.1/`.
- Verification evidence: `dev/verify.py` records passed, failed, error and skipped tests separately, each with the commit, the hash of `requirements.lock` and the environment, in `verification/`. Tests that need the course image are skipped with a reason outside it instead of failing.
- Security: `solutions/tests/security_scenarios.json` and `test_security_scenarios.py`; `dev/security_mutations.py` removes each security control in turn and checks that a test fails (`verification/SECURITY.md`).
- CI: the reference check and the generated docs run on every branch; the full suite runs in the course image and uploads its results; an `edition-*` tag publishes a release with them.
- [VERSION_MATRIX.md](VERSION_MATRIX.md): a dated matrix of every pinned version, model, price and protocol version, checked against `requirements.lock`, the `Dockerfile` and the code by `dev/check_references.py`.
- `sol_chNN_*.py` solution files moved into their own chapter folders (they had been filed under `ch00`, `ch01` and `ch03`).
- `dev/check_references.py`: checks every exercise id, file, command and cross-reference in the book and docs; runs in CI.
- README counts and EXERCISE_INDEX.md are generated from `course/exercises.json`, and CI fails if they're stale.

### Snapshot edition-1.0 (internal, September 2026)
- 31 chapters, 5 interludes, 231 exercises, 6 capstones.
