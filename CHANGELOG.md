# Changelog

What changed in the book and this repository, newest first. Each book printing is matched by a tag; see "Book editions and code versions" in [README.md](README.md). Corrections to a printed edition are listed in [ERRATA.md](ERRATA.md).

## edition-1.2: third printing (October 2026)

### Book
- **Part 10, In the Field, and Chapter 31: The Forward-Deployed Playbook.** What a forward-deployed engineer does (31.1); discovery that ends in a measurable problem brief, with a model drafting it from interview notes and code deciding whether it's ready (31.2); breaking a request into slices and shipping the smallest valuable one (31.3); checking a design against the customer's rules for data residency, model hosting, egress, personal data in logs, retention, sign-in, write access and audit (31.4); pilots against acceptance criteria signed in advance, with a gate that promotes, holds or stops (31.5); demos (31.6); handoff (31.7); the field-to-product loop (31.8); and where each skill is tested in interviews (31.9). Exercises 31.1–31.6 and a Part 10 checkpoint.
- **Capstone 7: A Customer Deployment.** A whole engagement, from a vague request and a constraint sheet to a signed-off pilot and a handoff, with a scoping score added to the rubric.
- **Appendix M: Interviewing for Agent Engineering and Forward-Deployed Roles.** The interview loop, a question bank with brief answers mapped to chapters, and three practice cases.
- **"In the field" notes** in Chapters 7, 9, 18, 26, 27 and 29: what changes when the same technique meets a customer's environment.
- **A forward-deployed path** in "How to Use This Book", Part 10 in the preface's map of the book, four new glossary terms, and the afterword's next steps.

### Repository
- `course/code/ch31/ch31_field.py`: the field kit (brief checker, `draft_brief`, slice ranker, design checker, pilot gate, handoff check, field-to-product report). Offline except `draft_brief`.
- `solutions/exercises/ch31/` (31.2–31.5), `solutions/tests/test_ch31_field.py`, and written answers for 31.1 and 31.6 in `solutions/ANSWERS.md`.
- `solutions/capstones/c7_engagement/`: the request, the constraint sheet, 30 synthetic handover notes (`data.py`) and the engagement record (`engagement.py`); `./course.sh capstone 7`.
- [INTERVIEW_PREP.md](INTERVIEW_PREP.md): the full question bank behind Appendix M.
- Exercises: 246 → 252.

## edition-1.1: second printing (October 2026)

### Book
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

### Repository
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

## edition-1.0: first printing (September 2026)
- 31 chapters, 5 interludes, 231 exercises, 6 capstones.
