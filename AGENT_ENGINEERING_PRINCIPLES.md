# Agent engineering principles

The engineering rules the book teaches, in one place: each as a one-line rule, why it holds, where the book teaches it and how this kit enforces it in code or tests. It's for engineers building on the kit, and for reviewers who want a checklist to hold an agent design against. The rules are split in two. **Non-negotiable rules** are ones the book states as "always" or "never" and backs with a control in code or a test; break one and the design is wrong, whatever the demo shows. **Strong defaults** are where the book says to start, with stated conditions for choosing differently; depart from one by writing down why (an ADR, Appendix K). The split is this document's grouping of the book's rules, not a list the book prints.

A rule counts as enforced only when something other than the prompt holds it. Section 25.11 says it directly: a control written in the system prompt doesn't count as in place, whatever it says.

## At a glance

| # | Rule | Taught | Enforced by |
| --- | --- | --- | --- |
| N1 | The model proposes; code enforces | 1.7, 9.3, 22.1, 25.11 | `ch22_guarded.py`; tests that assume a fooled model |
| N2 | Identity comes from the login, never a tool argument | Capstone 1, 22.4, 26.4, case study | `config_for`, `authorize`; S9 |
| N3 | Agents get their own short-lived, scoped identity; delegation only narrows | 26.2–26.5, 26.10, 30.4 | `ch26_identity.py`, `ch26_discovery.py` |
| N4 | Every loop has a cap, and every stop has a reason | 4.4, 29.4 | `max_iterations`, `next_action`, `should_stop` |
| N5 | Errors are data returned to the model | 2.6 | `is_error` tool results |
| N6 | Risky actions wait for an approval gate in code | Chapter 9, 26.6 | `run_tool` in `ch09_organizer.py`; S14 |
| N7 | The safest tool is the one you don't give | 9.1, 14.4, 26.3 | Allow-lists, scopes, read-only tokens |
| N8 | Tool output, memory, other agents and model output are untrusted | Chapters 6, 14, 17, 21, 25 | Policy layer, quarantine, write gate, `sanitize_markdown` |
| N9 | Break the lethal trifecta in the architecture | 25.2, 25.4, 25.5 | Egress allow-list, `private_sources`, guards; S1, S2, S10, S11 |
| N10 | Never share memory, sessions, private caches or tokens across tenants | 17.7, 17.10, 30.2, 30.12 | `SecureMemoryStore`, sessions per key; S5, S6 |
| N11 | A step with a side effect must be safe to repeat | 19.3, 19.5 | Idempotency keys, checkpoints; S13, S15 |
| N12 | Discovery is not trust | 14.3, 26.9, 30.10 | `discover` and `verify` kept apart; pins |
| N13 | Fail closed, and keep secrets out of code, prompts and telemetry | 26.8, 28.3, 30.2 | Service refuses to start without keys; redaction |
| N14 | Claim an improvement only when trials and intervals show it | Measurement interlude, 27.7 | `run_suite`, `compare`, `gate` |
| N16 | Five decisions are never the model's: authorization, security policy, tenant isolation, financial limits, destructive actions | 22.1, 25.2, 25.11 | Policy layer, tokens, approval gates; S8, S9, S14 |
| N17 | Every mutating tool has a written contract: idempotency, failure semantics, safe-retry class, timeout | 7.3, 19.5, 30.7 | Idempotency keys; S13, S15 |
| N18 | Memory is not automatically truth: candidates stay candidates until validated | 17.8, 17.10 | `promote`, quarantine, trust classes |
| N15 | Every failure becomes a test case | 25.10, 27.8, 30.14 | Security scenarios with mutations; mined cases |
| D1 | Use the least autonomy that does the job | 1.3, 1.9, 22.8 | Benchmark E1 |
| D2 | One agent before a team | 11.5, 21.9, 21.10 | `ch21_coordination.py` |
| D3 | Rules as data, numbers from records | 22.5 | `POLICY`, `decide` |
| D4 | Every guard needs a fallback | 22.6 | `check_reply` and `TEMPLATES` |
| D5 | Size the controls to the agent's risk | 25.11 | `ch25_risk.py` (`gaps`) |
| D6 | Judge cost per successful task, against the human baseline | 20.9, 29.3, 29.9 | `report`, `ch29_economics.py` |
| D7 | Keep the context small and the prefix stable | 4.6, 16.5–16.7, 29.8 | `ch16_context.py`; E3 |
| D8 | Secure before you evaluate; evaluate before you optimize | 1.10 | Lifecycle order |
| D9 | Version the whole agent; pin the model | 30.13 | Release records; benchmark `config.json` |
| D10 | Release gradually, and roll back by configuration | 30.13, 30.14 | `ch30_improvement_loop.py` |
| D11 | Keep the interfaces your own, whatever you buy | 24.5, 24.9, 30.12 | OpenTelemetry, MCP, your eval cases |

## Non-negotiable rules

**N1. The model proposes; code enforces.**
Why: the model is probabilistic and can be fooled, wrong or creative; identity, policy, validation, budgets, approvals, state transitions, audit and rollback must behave the same way every time. Test for each decision: if it were wrong 1 time in 50, would that be acceptable? If not, code owns it.
Taught: section 1.7 (the harness), section 9.3, section 22.1 to section 22.4, section 25.11 (the deterministic control plane), reference card 13.
Enforced: `TRANSITIONS` and `Case.move` in `ch22_guarded.py` refuse any transition not in the table; amounts come from the order record, never the message. `test_22_5_attacks_hold_even_when_the_model_is_fooled` in `solutions/tests/test_part7.py`, and every scenario in `solutions/tests/test_security_scenarios.py` makes the attacker's calls directly with no model involved, so a pass means the control holds whatever the model does.

**N2. Identity comes from the login, never from a tool argument.**
Why: the model fills in arguments and the customer can type anything; `get_order(order_id, email)` turns "I'm actually ben@example.com" into a lookup service for anyone's orders. The case study's early version read out another customer's address this way.
Taught: Capstone 1 ("Identity is never a tool argument"), section 22.4, section 26.4, the case study.
Enforced: `config_for` in `solutions/capstones/c1_support/agent.py` sets the customer from the session; `orders_server.py` reads it from the environment and no tool takes an email. `authorize` in `ch26_identity.py` checks the order belongs to the token's `act_for` user before scope or approval. Tests: `test_c1_identity_comes_from_the_host` (`test_capstones.py`), scenario S9.

**N3. Each agent gets its own short-lived, scoped identity, and delegation only narrows.**
Why: a person's credentials grant everything they can do and blame them in the logs; a short token limits a leak even when nobody notices. A subagent, a server or a partner agent gets a token for its task, never yours, and a server never passes a user's token through to another API.
Taught: section 26.1 to section 26.5, section 26.10, section 30.4, section 30.9.
Enforced: the `AGENTS` registry is the ceiling for `mint`; `attenuate` can only drop scopes, shorten expiry and tighten limits, and records the `chain` so revoking a parent revokes the children. Across organizations, `authorize` in `ch26_discovery.py` grants the intersection of request, holder and `TrustStore` limits. Tests: S9, `test_cross_org_delegation_only_narrows` and `test_rotation_and_revocation` (`test_ch26_discovery.py`). Production adds an identity provider, public-key signing and OAuth token exchange (section 26.8).

**N4. Every loop has a cap, and every stop has a reason.**
Why: a confused model can call the same failing tool forever, and you pay for every call; treating a cut-off or refused reply as an answer is a silent failure.
Taught: section 4.4, section 10.5, section 18.8 (bounded retrieval rounds), section 21.3 (team limits), section 29.4.
Enforced: `run_agent` in `ch04_agent.py` stops after `max_iterations` (default 8) and checks `should_stop` after every step; `next_action` handles `max_tokens`, `refusal` and context overflow explicitly; `get_client` sets a 120-second timeout. `request_budget` and `DailyBudget` in `ch29_costs.py` cap tokens per request and spend per user per day. Tests: `test_4_3_cap_and_failing_tool` (`test_ch04_05.py`), `test_29_4_budgets` (`test_part9.py`).

**N5. Errors are data returned to the model.**
Why: an exception crashes the program and teaches the model nothing; an error message lets it explain or try again. The benchmark shows the payoff: with 10% transient tool failures, success held because the agent read the error and retried (section 29.8, E4).
Taught: section 2.6, used in every chapter after it.
Enforced: the kit's tools return `ERROR: …` text instead of raising (`run_tool` in `ch03_tools.py` catches any exception), and `run_agent` in `ch04_agent.py` sends it back as a tool result with `is_error` set. Tests: `test_2_5_graceful_errors` and `test_2_5_error_reaches_model` (`test_ch01_03.py`).

**N6. Risky actions wait for an approval gate in code, and what was approved is exactly what runs.**
Why: a gate in the prompt can be argued past; a gate in `run_tool` runs even when a file name says "ignore previous instructions". Storing the plan under an id stops the model showing one plan and executing another.
Taught: section 9.1 to section 9.4, section 26.6 (step-up tokens), section 22.7.
Enforced: `NEEDS_APPROVAL`, `ask_human` and `run_tool` in `ch09_organizer.py`, with `audit_log.jsonl` and `undo_plan`; single-use, two-minute step-up tokens in `Session` (`ch26_identity.py`); `Policy.before_call` shows the complete, escaped arguments (`ch14_policy_agent.py`). Tests: `test_9_3_9_4_organizer_decline_then_undo`, `test_14_approval_shows_the_whole_call`, `test_c1_agent_return_needs_approval`, scenario S14.

**N7. The safest tool is the one you don't give the agent.**
Why: a read-only token can't post a comment whatever the injected text says. Irreversible, severe actions don't belong to an agent at all.
Taught: section 9.1 (risk table), section 14.4 (defenses ranked, capability removal first), section 26.3 (the registry as ceiling).
Enforced: `visible_tools` in `Policy` hides tools not on the allow-list; the gateway's `POLICY` is deny-by-default (`ch30_gateway.py`); scopes per tool in `ch30_remote_mcp.py`; `ch25_quarantine.py` gives the planner no email-sending tool. Test: scenario S8.

**N8. Treat tool output, retrieved text, memory, other agents' answers and model output as untrusted data.**
Why: the model reads instructions and data as one stream; "the following is data" lowers attack success but never to zero. A memory is a prompt that comes back next month, maybe for a different user.
Taught: Chapter 6 (text in a file is data, not instructions), section 14.4, section 17.8, section 17.10, section 21.7, section 25.3, section 25.5, section 25.7.
Enforced: the policy layer (`ch14_policy_agent.py`); the quarantined reader and schema in `ch25_quarantine.py`; the write gate, provenance and `review_queue` in `ch17_memory_policy.py`; trust classes, `promote` and quarantine-by-default in `ch17_memory_security.py`; `sanitize_markdown` in `ch25_guards.py`. Tests: S3, S4, S7, S12, `test_untrusted_writes_are_quarantined_unless_promoted` (`test_ch17_security.py`). An agent that reads untrusted content shouldn't be able to write procedural memory at all (section 17.8).

**N9. Break the lethal trifecta in the architecture.**
Why: private data plus untrusted content plus a way to communicate out lets injected text exfiltrate data with no write tool involved, so "approve every write" doesn't help. Remove any one leg and the attack fails.
Taught: section 25.2, section 25.4, section 25.5; the case study's threat model.
Enforced: `egress.allow_domains` and `private_sources` in the Chapter 14 policy (every outbound call after a private read needs a person); `url_problem` in `ch11_web.py` on every redirect hop; canary, leak scan and egress checks in `guarded` (`ch25_guards.py`). Tests: S1, S2, S10, S11, `test_11_fetch_checks_every_redirect` (`test_security.py`).

**N10. Never share memory, sessions, private caches or tokens across tenants; authorize before ranking.**
Why: ranking first and filtering after depends on a post-processing step someone will one day skip, cap wrongly or log before filtering.
Taught: section 17.7, section 17.10, section 30.2, section 30.12; ADR-7 in Appendix K.
Enforced: `SecureMemoryStore.authorized` returns only the caller's records and raises `PermissionError` (with a `denied` audit entry) across tenants; sessions in `ch30_service.py` belong to the key id that created them (404 for anyone else). Tests: S5, S6, `test_tenant_isolation_happens_before_ranking`. The kit's earlier `ch17_memory_policy.py` has no tenant at all; section 17.10 says so.

**N11. A step with a side effect must be safe to repeat.**
Why: retries and restarts are normal; a refund or email repeated after a crash isn't. A step whose outcome can't be known is escalated, not guessed.
Taught: section 19.3 to section 19.7, section 30.8 (`request_id` on long-running tools); ADR-6.
Enforced: checkpoints, leases and idempotency keys in `ch19_durable.py`; `resume_unfinished` in `ch30_jobs_server.py`. Tests: S13, S15.

**N12. Discovery is not trust.**
Why: finding a capability answers "what says it can do this?", not "should my agent use it, for this user, with what rights?" A signature proves who published a descriptor; only a pin proves it's what someone reviewed, so a rug pull is caught.
Taught: section 14.3, section 26.9, section 26.10, section 30.10.
Enforced: `discover` matches declared capabilities and never reads descriptor text; `verify` checks publisher, kind, key and pin before anything reaches the model (`ch26_discovery.py`); the gateway's allow-list has the final word. Tests: `test_finding_is_not_trusting`, `test_signature_and_pin_catch_different_things`.

**N13. Fail closed, and keep secrets out of code, prompts and telemetry.**
Why: a service with a built-in default key is protected by a password printed in a book. Keys go to the harness, never to the model; logs and traces carry ids and counts, not message text or keys.
Taught: section 26.8, section 28.3, section 30.2, section 30.6.
Enforced: `ch30_service.py` refuses to start without `AGENT_API_KEYS` and logs only a key id; `MCPHub` passes servers a minimal environment; `redact` in `ch28_agentops.py`. Tests: `test_13_servers_get_a_minimal_environment`, `test_10_tests_run_without_secrets`, `test_28_summarize_classify_report_alerts`.

**N14. Claim an improvement only when trials and intervals show it.**
Why: nine passes out of ten could be a real rate anywhere from about 60% to 98%. One run is an anecdote; overlapping intervals mean you don't know yet.
Taught: the measurement interlude (section M.1 and section M.2), section 27.7.
Enforced: `run_suite` and `wilson` in `ch27_eval.py`; `compare` in `i_measure.py` calls a version better only when intervals don't overlap; `gate` in `ch27_trajectory.py` blocks only a drop larger than noise, alongside absolute limits (safety at zero). Test: `test_27_gate_and_drift` (`test_part9.py`).

**N15. Every failure becomes a test case.**
Why: a defense shown once disappears in a refactor; a production failure that isn't in the suite comes back.
Taught: section 25.10 (both a failure-mode and a mitigation test, plus "what remains"), section 27.8, section 30.14.
Enforced: `solutions/tests/test_security_scenarios.py` with `security_scenarios.json`; `dev/security_mutations.py` turns each control off and confirms its test fails (results in `verification/SECURITY.md`). `mine_failures` and `to_cases` in `ch30_improvement_loop.py` add deduplicated, labelled cases whatever the release decision. Tests: `test_every_scenario_has_both_tests`, `test_a_fixed_failure_cannot_come_back`.

**N16. Five decisions are never the model's.**
Why: authorization, security policy, tenant isolation, financial limits and permission for destructive actions are where one persuaded model does the most harm. The model may ask and explain; code decides.
Taught: section 22.1, the security boundary in section 25.2, the "What agents must never decide" box in section 25.11, Card 13.
Enforced: the policy layer (`ch14_policy_agent.py`), `authorize` in `ch26_identity.py`, the approval gate in `ch09_organizer.py`; scenarios S8, S9 and S14.

**N17. Every mutating tool has a written contract.**
Why: a timeout means *unknown*, not *failed*; a blind retry charges the card twice.
Taught: the "Tool contract for mutations" box and its table in section 7.3, section 19.5, the launch checklist in section 30.7.
Enforced: idempotency keys and escalation of unkeyed steps in `ch19_durable.py`; scenarios S13 and S15.

**N18. Memory is not automatically truth.**
Why: a memory is a claim with an author. Tool output, web content, agent inference and claims about other people are candidates until the write gate, provenance and validation accept them.
Taught: section 17.8, the validated-versus-candidate table in section 17.10.
Enforced: trust classes, quarantine and `promote` in `ch17_memory_security.py`; scenarios S7 and S12.

## Strong defaults

**D1. Use the least autonomy that does the job.** Why: an agent is slower, costs more, is harder to test and compounds mistakes. If you can draw the flowchart first, build a workflow. Taught: section 1.3, section 1.9, section 22.8; ADR-1. Evidence: in the simulator's E1 (section 29.8), a workflow matched the agent's 97% success at 37% of the cost per success. Switch when the steps depend on what the tools return.

**D2. One agent before a team.** Why: a team adds calls, duplicated context, messages, synchronization and failure propagation; with 97% per step, five steps all right is about 86%. Taught: section 11.5, section 21.9, section 21.10; ADR-2. Enforced: `coordination_report` and `decide` in `ch21_coordination.py` pick the team only for a measurable gain worth its cost or a requirement one agent can't meet (`test_decide_requires_a_measurable_gain_worth_its_cost`). Always compare against the best single agent, for example one with parallel tool calls.

**D3. Keep business rules as data, and take numbers from records.** Why: a policy change becomes a reviewed, versioned data change; a pure decision function gets exact unit tests at every boundary. Taught: section 22.5, section 9.6 (auto-approval policies in configuration). Enforced: `POLICY` and `decide` in `ch22_guarded.py`; `policy.json` for Chapter 14. Test: `test_22_4_policy_as_data`.

**D4. Every guard needs a fallback, and you log how often it fires.** Why: without one, a failed check becomes a different failure. Taught: section 22.6. Enforced: `check_reply` falls back to a template (`test_22_reply_guard_falls_back`).

**D5. Size the controls to the agent's risk.** Why: a date agent needs an owner, evals and a log; a refunding support agent needs approvals, a red team and a kill switch. Risk = capability × autonomy × access × persistence × blast radius; cut one factor to cut the score. Taught: section 25.11, reference card 12. Enforced: `risk_score`, `tier`, `required_controls` and `gaps` in `ch25_risk.py` (`test_ch25_risk.py`). It's a judgment aid, not a probability.

**D6. Judge cost per successful task, against the human baseline.** Why: failed and escalated tasks were paid for too; a cheaper model that fails slightly more can make the business case worse. Against zero, an agent looks like either a pure cost or a pure saving. Taught: section 20.9, section 29.3, section 29.9, reference card 14. Enforced: `report` in `ch20_router.py`; `cost_per_successful_task` and `business_case` in `ch29_economics.py` (`test_baseline_is_people_not_zero`).

**D7. Keep the context small and the prefix stable.** Why: every call resends the whole history; in E3 an extra 8,000 tokens of system prompt made each successful task 16 times as expensive with no accuracy gain. Taught: section 4.6, section 16.5 to section 16.7, section 29.8. Enforced: `trim_old_tool_results`, `compact` and `with_cache` in `ch16_context.py`; bounded history in `ch30_service.py`.

**D8. Secure before you evaluate; evaluate before you optimize.** Why: a suite only checks the attacks the threat model put in it, and making a wrong agent faster makes it wrong sooner. Taught: section 1.10, section 30.13; the case study ("measured before optimizing").

**D9. Version the whole agent, and pin the model to a dated id.** Why: model id, prompt, tool definitions, server versions, skills, policies and the approving eval suite all change behavior; an incident should point to one release. Taught: section 30.13. Enforced in part: candidates in `ch30_improvement_loop.py` carry a version and model, and `release_decisions.json` records the evidence; each benchmark run's `config.json` records the commit, model ids and a hash of prompts and tools. The kit has no bundle registry; a production version adds one and puts the version on every span.

**D10. Release gradually, and roll back by configuration.** Why: offline cases are the questions you thought of; shadow and canary use real ones. Too little data holds; it doesn't pass. Taught: section 30.13, section 30.14; the case study's release 1.3 incident. Enforced: `offline_eval`, `shadow`, `canary` and `GATES` in `ch30_improvement_loop.py` (`test_slow_candidate_rolls_back_at_canary`, `test_canary_holds_when_too_few_runs`).

**D11. Keep the interfaces your own, whatever you buy.** Why: a framework changes how much code you write, not what good looks like; owning OpenTelemetry spans, MCP tool interfaces, the policy layer and your eval cases lets you swap a component. Taught: section 24.5, section 24.9, section 30.12.

## Where this comes from

- Section 1.3, section 1.7, section 1.10; section 2.6; section 4.4; Chapter 9; section 14.3 to section 14.5
- Section 17.7, section 17.8, section 17.10; section 19.5; section 20.9; section 21.9, section 21.10
- Section 22.1 to section 22.7; Chapter 25 (especially section 25.10 and section 25.11); Chapter 26 (especially section 26.4 and section 26.9)
- The measurement interlude; section 27.7, section 27.8; section 29.8, section 29.9; section 30.2, section 30.13, section 30.14
- Capstone 1 and the case study; Appendix I cards 12–14; Appendix K
- Code: `course/code/ch22/ch22_guarded.py`, `course/code/ch26/ch26_identity.py`, `course/code/ch25/ch25_risk.py`, `course/code/ch30/ch30_improvement_loop.py`; tests in `solutions/tests/test_security_scenarios.py`, `solutions/tests/test_part7.py`, `solutions/tests/test_part9.py`
