# Agent lifecycle

This is the agent engineering lifecycle from *Building Agentic AI Systems*, as a working reference: for each stage, the question it answers, when you may start it, what you must have before you move on, what it produces, where the book teaches it and which code in this kit supports it. It's for an engineer taking an agent from idea to production (and keeping it there) who has the repository open but not the book. The stages come from section 1.10, the production view from sections 30.13 and 30.14, the exit criteria from Card 11 in Appendix I, and the worked example from the case study and the afterword.

```
Decide (once) -> Design -> Build -> Secure -> Evaluate -> Optimize -> Deploy -> Operate -> Improve
                   ^                                                              |        |
                   +------------------------ next version ---------------------------------+
                                                                                  +-> Retire (once)
```

## The stages at a glance

| Stage | The question | Before you move on (Card 11) |
| --- | --- | --- |
| Decide (once) | Does this problem need an agent, and which kind? | You can say why a simpler option won't do |
| Design | Which tools, context, rules and checks will it have, and what may it never do? | Tools, context, rules in code and checks are written down; the decisions are recorded (Appendix K) |
| Build | Does it work, step by step? | Each step works and has a test |
| Secure | What can go wrong on purpose, and what in code stops it? | A threat model, a risk tier and its controls, regression scenarios that pass |
| Evaluate | Is it right often enough, and safely? | A case file, several trials, intervals and a scorecard |
| Optimize | Is it fast and cheap enough for what it earns? | Cost per successful task and p95 latency inside budget, quality unchanged |
| Deploy | Can it go live without surprises? | CI gate passed, launch checklist done, shadow and canary planned, rollback ready |
| Operate | What is it doing, and what does it cost? | Traces, SLOs, alerts, budgets and a named owner |
| Improve | What failed, and did the fix work? | Every failure is a new case; one change at a time, through the improvement loop |
| Retire (once) | How do you switch it off cleanly? | Kill switch, revoked identity, gateway routes removed, data handled by policy, audit log kept |

Two ordering rules (section 1.10):

- **Secure comes before Evaluate.** A test suite can only check the attacks you thought of; the threat model decides which ones go in it.
- **Optimize comes after Evaluate.** Making a wrong agent faster only makes it wrong sooner. Set the quality bar first, then buy back cost and latency without falling below it.

The lifecycle is a loop, not a waterfall. Each new version (a prompt, a tool, a model, a skill) goes back through Design to Deploy, usually by way of the improvement loop below. The entry criterion of every stage is the exit criterion of the one before it.

## Stage by stage

### 1. Decide (once)

- **Question.** Does this need an agent at all, and if so which kind? Choose the least autonomy that does the job.
- **Do.** Walk the options in order: function, workflow, state machine, RAG, single LLM call, agent, multi-agent (Card 1). Ask: can I draw the flowchart first? What does a wrong step cost? Can I tell when it's done and right? Is the flexibility worth the cost and latency? Name the kind of each part and its first risk (Card 10).
- **Produces.** A one-paragraph decision, per kind of request if requests differ. The case study splits one product into a workflow (order status), a state machine with model steps (returns and refunds) and one agent (everything else).
- **Book.** Sections 1.3, 1.6 and 1.9; Cards 1, 2 and 10; ADR-1 and ADR-2 in Appendix K; for the business case, section 29.9 and Card 14.
- **Kit.** `ch29_economics.py` (cost per successful task against the human baseline, payback, break-even and sensitivity); `ch29_benchmark.py` with the published simulator run in `benchmarks/` (E1 compares a workflow, one agent and a team on the same questions).
- **Gate to Design.** You can say, in writing, why a simpler option won't do.

### 2. Design

- **Question.** Which tools, context, rules and checks will it have, and what may it never do?
- **Do.** Write the design note (Exercise 1.7): tools, what it needs to know at each step, rules that live in code, the checks, what could go wrong. Split the work: the model proposes, deterministic code enforces identity, policy, validation, budgets, approvals, state transitions, audit and rollback (Card 13, section 22.1's "wrong 1 time in 50" test). Walk the reference architecture's layers top to bottom (section 30.15).
- **Produces.** The design note; decision records for the recurring choices (Appendix K: workflow or agent, one agent or a team, direct tools or MCP, fixed or agentic retrieval, hosted or local model, synchronous or durable, one tenant or many); the first evaluation cases. The case study wrote its suite before the agent was shown to anyone.
- **Book.** Exercise 1.7, Chapter 22, Appendix K, section 30.15.
- **Kit.** `ch22_guarded.py` (a deterministic shell with model steps); `eval_sql.jsonl` as the shape of a case file.
- **Gate to Build.** Tools, context, rules in code and checks are written down, and the decisions are recorded.

### 3. Build

- **Question.** Does it work, step by step?
- **Do.** Build the loop, tools, servers, context, memory, durable jobs, plans and controls the design calls for. Test each piece with a stand-in model so the test is deterministic and free.
- **Produces.** Working code with a test per step.
- **Book.** Chapters 2–24; the testing interlude.
- **Kit.** `course/code/ch02` to `course/code/ch24`; reference solutions and tests in `solutions/`; `./course.sh check-solutions` runs every solution and capstone offline with a scripted model (no API key); `./course.sh run-chapter <n>` runs reference solutions on a real model.
- **Gate to Secure.** Each step works and has a test.

### 4. Secure

- **Question.** What can go wrong on purpose, and what in code stops it?
- **Do.** Answer the four threat-model questions (section 25.2) and look for the lethal trifecta. Score the agent's risk (capability × autonomy × access × persistence × blast radius) and put in the tier's required controls (section 25.11). Give it its own identity and scoped, short-lived tokens (Chapter 26). Write a regression scenario per defense, with both halves: the attack succeeds without the control and fails with it (section 25.10).
- **Produces.** A one-page threat model; a risk profile and tier; the list of required controls with no gaps; passing regression scenarios; agent identity and scopes in the registry.
- **Book.** Chapter 9 (approval gates), Chapter 14, section 17.10, Chapters 25 and 26. See `SECURITY_MODEL.md` for the full control set.
- **Kit.** `./course.sh python ch25_risk.py` (`risk_score`, `tier`, `required_controls`, `gaps`); `./course.sh check-solutions -k security_scenarios` (S1–S15); `dev/security_mutations.py` (switches each control off and checks its test fails; results in `verification/SECURITY.md`); the red-team suite of Exercise 25.6.
- **Gate to Evaluate.** `gaps(profile, controls_in_place)` is empty and every scenario passes. A control written only in the system prompt doesn't count.

### 5. Evaluate

- **Question.** Is it right often enough, and safely?
- **Do.** Run the case file with several trials per case, report pass rates with Wilson intervals, check the trajectory as well as the answer, calibrate any model judge against human labels, and summarize in a scorecard.
- **Produces.** The case file (outcome, process and cost checks; attack and handoff cases); per-run scorecard (success, pass^k, tool and argument accuracy, safety violations, steps, p50/p95, cost per task and per successful task); the release-level scorecard of eleven qualities with floors.
- **Book.** Chapter 3's first eval, the measurement interlude (sections M.1 and M.2), Chapter 27 (sections 27.2–27.7).
- **Kit.** `i_measure.py` (`run_suite`, `compare`); `./course.sh python ch27_eval.py eval_sql.jsonl 3` (real model, three trials); `ch27_trajectory.py` (`gate`, the one-sided two-proportion test of section 27.7); `ch27_judge.py`; `./course.sh python ch27_scorecard.py --release` (canned runs, no key; prints the per-run card and the release qualities against `QUALITY_TARGETS`). Exercise 27.8 is a scorecard that deliberately fails when a model misses its floors.
- **Gate to Optimize.** Every quality at or above its floor; safety and security have no slack.

### 6. Optimize

- **Question.** Is it fast and cheap enough for what it earns?
- **Do.** Find where the time and money go (model, tools, retrieval, orchestration, queueing, serialization), then pull the levers: retrieval instead of pasted context, prompt caching, a smaller model where the suite shows no loss, budgets in code. Load-test open-loop at an arrival rate and find the knee; size capacity with Little's law. Rerun the scorecard after every change.
- **Produces.** Cost per successful task and p95 latency against budget; a capacity plan and concurrency limit; per-request and daily budgets in code.
- **Book.** Chapter 16 (context, section 16.7 on caching), Chapter 20 (model routing), Chapter 29 (sections 29.1–29.9), Card 8.
- **Kit.** `ch29_costs.py` (`estimate`, `request_budget`, `DailyBudget`, `concurrency_needed`); `ch29_loadtest.py`; `ch29_perf.py`; `ch29_benchmark.py`; `ch20_router.py`; `ch29_economics.py`.
- **Gate to Deploy.** Cost per successful task and p95 inside budget, with the scorecard unchanged. Exercise 29.7 is the rule: a success floor decides, not cost alone.

### 7. Deploy

- **Question.** Can it go live without surprises?
- **Do.** Gate every change in CI. Go through the launch checklist line by line. Version the whole bundle (model id pinned to a dated id, system prompt, tool definitions and server versions, skills, policies, the eval suite that approved it) and put the version on every trace. Plan the shadow and canary, and rehearse a rollback by configuration.
- **Produces.** A passing CI gate; the completed checklist (security and trust, quality, reliability, cost and performance, operations); a container; a smoke test that passes against the real URL; a versioned release bundle; a written rollout and rollback plan.
- **Book.** Sections 27.7, 30.2, 30.6, 30.7 and 30.13.
- **Kit.** `./course.sh serve-api` (`ch30_service.py`); `ch30_service.Dockerfile`; `ch30_smoke_test.py`; `ch30_gateway.py` for a front door with deny-by-default policy.
- **Gate to Operate.** CI gate passed, checklist done, shadow and canary planned, rollback ready.

### 8. Operate

- **Question.** What is it doing, and what does it cost?
- **Do.** Trace every model call, tool call and handoff with the release version on each span; keep secrets and personal data out of telemetry. Classify failures with the taxonomy. Measure SLOs from named sources and alert on error-budget burn rate, not on single errors. Enforce budgets in code. Give the agent a named owner in the inventory.
- **Produces.** Traces and structured logs; failure-class counts; an SLO table with error budgets; burn-rate alerts; a dashboard; an owner.
- **Book.** Chapter 28 (sections 28.1–28.13), Chapter 29 (section 29.4 budgets, 29.7 capacity), section 30.12 (inventory), Cards 5 and 7.
- **Kit.** `ch28_otel.py`; `ch28_agentops.py` (`redact`, `summarize`); `./course.sh python ch28_ops.py` (timeline, latency breakdown, `classify_detailed`, `AGENT_SLOS`, `measure_slos`, the HTML dashboard); `ch28_profile.py`.
- **Gate to Improve.** Production runs are traced and graded, and someone owns the result.

### 9. Improve (then the next version)

- **Question.** What failed, and did the fix work?
- **Do.** Sample real runs for grading (every flagged run plus a random share), watch for drift, turn every failure worth fixing into a labeled case, and send each fix through the improvement loop below. One change at a time.
- **Produces.** A growing suite; candidate releases with decision records; promoted or rolled-back versions.
- **Book.** Section 27.8 (continuous evaluation), section 30.14 (the improvement loop), section 30.13 (model changes).
- **Kit.** `ch27_trajectory.py` (`sample_for_review`, `drift`); `./course.sh python ch30_improvement_loop.py`; its tests in `test_ch30_improvement_loop.py`.
- **Gate back to Design.** A candidate exists for one named failure class, with a new bundle version.

### 10. Retire (once)

See the checklist at the end of this document.

## The improvement loop (section 30.14)

The routine that turns production failures into a release that's proven better before every user gets it. Every gate is decided by code against a threshold written down in advance; people write the labels and set the thresholds in review.

```
traces + grades -> mine failures -> new eval cases -> baseline (current release, grown suite)
  -> one change -> offline eval -> shadow -> canary -> promote | roll back -> traces + grades
                       | fail        | fail     | fail
                    reject        reject     roll back        (rejected: try another change)
```

| Stage | Consumes | Produces | Decided by (`ch30_improvement_loop.py`) |
| --- | --- | --- | --- |
| Mine failures | Graded production runs | Failed runs with taxonomy classes | `mine_failures`, using `classify_detailed`; a failed grade with no class is `unclassified` (the taxonomy needs a class) |
| Build cases | Failed runs with a reviewer's label | Deduplicated cases; id starts with the class, `source` is the trace id | `to_cases`; a person writes the expected answer, `normalize` merges near-duplicates |
| Baseline | Grown suite, current release | Pass rates with intervals | Nobody: it's the yardstick |
| One change | A failure class and its mitigation | A candidate with a new bundle version | The engineer |
| Offline eval | Both versions, three trials per case | Pass rates, the gate's z, broken old cases, mined-case pass rate | `offline_eval`: `gate` must not block, `max_broken` 0, `fixed_min` 90% of mined-case runs pass |
| Shadow | Mirrored real requests | Paired grades; users see only the current version | `shadow`: `gate` must not block, `shadow_max_worse` 2% |
| Canary | `canary_share` 10% of real traffic | Each arm's SLOs and burn rate | `canary` with `measure_arm`: any missed SLO (success, p95, cost) or burn over `canary_max_burn` 1.0 rolls back; under `canary_min_runs` 30 holds |
| Promote or roll back | Every stage's result | `release_decisions.json`: decision, reasons, thresholds, each stage's numbers, no raw traces | `improvement_turn`, stopping at the first failing gate |

Rules that make it work:

- **No guessed labels.** A failure without a reviewer's expected answer waits; a wrong label teaches the gate to block the fix.
- **One problem, one case.** In the demo, 44 failed runs are three problems.
- **Mined cases stay in the suite whatever the decision.** On the next turn any release that brings the failure back breaks an old case and is rejected offline.
- **For agents that act, shadow the decision** (what it would have done), not the action.
- **Too little data holds; it doesn't pass.**

The demo promotes release 1.5 and rolls back 1.6, which is right but misses the 8-second p95 objective in the canary. Exercise 30.12 moves the latency check into shadow.

**What production adds** (section 30.14): mirror traffic at the gateway; group paraphrased failures with embeddings and a review queue; raise the canary in steps (1%, 10%, 50%) over hours with two-window burn-rate alerts; hash users or tenants, not requests, to the canary; roll back by switching traffic in configuration; compare cost per successful task.

**When the model changes** (section 30.13): run the suite and scorecard on the new model, recalibrate the judge against human labels, compare cost per successful task, then shadow and canary it like any release. Subscribe to deprecation notices.

## Retirement checklist (section 30.13)

An agent that's half-retired still holds credentials.

- [ ] Tell its users and send them somewhere else.
- [ ] Switch it off with the kill switch (`disable` in `ch26_identity.py`, section 26.7).
- [ ] Remove its routes from the gateways (section 30.9) and its entry from the inventory (section 30.12).
- [ ] Revoke its identity and every token derived from it (`revoke`; derived tokens die through their `chain`).
- [ ] Apply the retention policy to its memories and sessions: delete what it shouldn't keep, export what it must (Chapter 17; `forget_user` in `ch17_memory_security.py`).
- [ ] Keep the audit log as long as the policy says.
- [ ] Cancel its scheduled jobs and leases (Chapter 19) and delete its secrets.

## The support agent through the lifecycle

The case study and the afterword follow one agent through every stage. Its lessons, by stage:

| Stage | What happened | Lesson |
| --- | --- | --- |
| Decide | Workflow for order status, state machine for refunds, agent for open questions, small-model router | Least autonomy per kind of request (simulator E1: the workflow matched the agent at 37% of the cost per success) |
| Secure | All three legs of the lethal trifecta present; broken in code: identity from the login, refunds through rules and step-up tokens, sanitized replies, no arbitrary URL fetch | Scenarios S3–S6, S9 and S14 must pass before any release |
| Evaluate | 120 cases at launch, three trials, gate on the interval; unsafe actions and missed handoffs have no slack | Write the suite before the agent exists |
| Build/Evaluate | Testing found invented policy, a cost 8× budget, identity as a tool argument, retries in the tail | Each finding changed the design and added a case |
| Optimize | Retrieval and caching instead of the pasted handbook | Measure before optimizing |
| Deploy/Operate | Release 1.3's "warmer" prompt passed the gate, then burned the missed-handoff SLO in the canary; automatic rollback by configuration | The gate catches what the suite knows; the canary catches what it doesn't |
| Improve | Eight handoff cases added; missed handoff became a hard limit; the handoff rule moved from the prompt into code | Rules that must hold belong in code |

## Honest limits

The lifecycle code in this kit is labeled **Production pattern** (`ch25_risk.py`, every Chapter 27 and Chapter 28 file, `ch29_costs.py`, `ch29_economics.py`, `ch30_improvement_loop.py`) or **Prototype** (`ch29_benchmark.py`, `ch29_loadtest.py`, `ch30_smoke_test.py`) in `course/code_maturity.json`. None is production-hardened. The improvement loop runs fake agents that answer the same way every time; the risk model counts a control as in place when you list it, where a production version wants evidence (a passing scenario, a scope in the registry); `ch27_eval.py` needs a real model, while `ch27_scorecard.py --release`, `ch28_ops.py`, `ch29_economics.py`, `ch25_risk.py` and `ch30_improvement_loop.py` run offline with no key.

## Where this comes from

- Section 1.10 (the stages and their order); sections 1.3, 1.6, 1.9; Cards 1, 10, 11, 13 and 14 in Appendix I; Appendix K.
- Chapter 22 and section 30.15 (design); Chapters 2–24 (build).
- Sections 25.2, 25.10, 25.11 and Chapter 26 (secure): `course/code/ch25/ch25_risk.py`, `solutions/tests/test_security_scenarios.py`.
- The measurement interlude and Chapter 27 (evaluate): `i_measure.py`, `course/code/ch27/ch27_eval.py`, `ch27_trajectory.py`, `ch27_scorecard.py`.
- Chapter 29 (optimize): `ch29_costs.py`, `ch29_benchmark.py`, `ch29_economics.py`.
- Sections 27.7, 30.6, 30.7 and 30.13 (deploy): `ch30_service.py`, `ch30_smoke_test.py`.
- Chapter 28 (operate): `ch28_ops.py`, `ch28_agentops.py`, `ch28_otel.py`.
- Sections 27.8 and 30.14 (improve): `course/code/ch30/ch30_improvement_loop.py`.
- Section 30.13 (retire); the case study (`course/md/89_case_study.md`) and the afterword (`course/md/90z_afterword.md`).
