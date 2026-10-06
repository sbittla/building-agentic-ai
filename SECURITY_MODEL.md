# Security model

This is the security model that *Building Agentic AI Systems* teaches and this kit implements: what an agent has worth protecting, who attacks it and how, where the trust boundaries are, which control stops each attack and exactly where in the code it's enforced, how many controls a given agent needs, and what this educational kit leaves out that a production deployment must add. It's for an engineer reviewing or building an agent with the repository open but not the book. One assumption runs through all of it: **the model will be fooled.** Anything that must hold is enforced by deterministic code outside the model; the prompt is the weakest layer.

## Assets and threats

| Asset | Threat | How it arrives | Scenario |
| --- | --- | --- | --- |
| Private data (notes, repos, customer records) | Exfiltration through a tool call | Indirect injection in a retrieved note or tool result | S1, S2 |
| Private data | Exfiltration with no tool call | A Markdown image in the reply, fetched by the chat client | S4 |
| Money and systems of record | Unwanted action | An external email asks for a transfer; a fooled planner adds it | S3 |
| Money and systems of record | Action without, or beyond, approval | Model skips the gate; an approval is replayed or enlarged | S14 |
| Money | Duplicate side effect | A retry after a timeout that actually succeeded | S13, S15 |
| Other users' data | Cross-user or cross-tenant read | Recall without ownership checks; a guessed session id | S5, S6 |
| Shared memory (every later session) | Memory poisoning | A fooled worker writes a team memory with an instruction | S7 |
| Tools and permissions | Privilege escalation | A tool not on the allow-list; a read token used to refund; a sub-agent widening its token | S8, S9 |
| Internal network | SSRF | A URL or redirect to localhost, a private range or cloud metadata | S10 |
| Allow-listed egress | Allow-list bypass | Look-alike hosts (`python.org.attacker.example`) | S11 |
| Secrets and card numbers | Leak into a tool argument or long-term memory | Model copies a key into a call or a memory | S12 |
| Your agent's instructions | Supply-chain injection | Tool poisoning in a server's description; a rug pull after review; a changed skill | (sections 14.3, 26.9, 30.10) |
| Identity of the acting agent and user | Impersonation | Identity passed as a tool argument ("I'm actually ben@...") | S9; case study finding 3 |

The kinds of injection (section 25.3): direct, indirect, stored (memory), relayed (another agent), in tool descriptions, and hidden (white text, invisible Unicode, text in images).

### The lethal trifecta

An agent with **private data**, **exposure to untrusted content** and **a way to communicate out** can be told by the content to send the data out (sections 25.2 and 25.4). No write tool is needed, so "approve every write" doesn't help. Remove any one leg in code. The kit does it three ways: the egress allow-list and `url_problem` (where data can go), the policy layer's "private read, then every outbound call needs a person" rule (S2), and quarantined reading, so the model that acts never sees untrusted text (section 25.5). The case study has all three legs and breaks each in code.

### The four threat-model questions (section 25.2)

1. What untrusted text can reach the model?
2. What can the agent do that would hurt, and every way data can leave?
3. What does it have that someone would want?
4. Where does a check happen in code, for each harmful action in question 2?

## Trust boundaries

| Boundary | What crosses it | Treated as | Enforced by |
| --- | --- | --- | --- |
| Caller → agent API | Requests, session ids | Unauthenticated until the API key checks out | `api_key`, `rate_limit`, `load_session` in `ch30_service.py` |
| Outside content → model context | Pages, files, emails, issues, tool results, memories, other agents' answers | Data, never instructions; untrusted | Quarantined reader (`ch25_quarantine.py`), policy layer (`ch14_policy_agent.py`) |
| Model → tools | Tool name and arguments | Proposals from an untrusted source | `run_tool` gate (`ch09_organizer.py`), `Policy.before_call`, `guarded` (`ch25_guards.py`), `authorize` (`ch26_identity.py`) |
| Agent → outside world | URLs, messages, rendered output | Exfiltration channel | `url_problem`/`fetch_url` (`ch11_web.py`), `sanitize_markdown` |
| Session → memory | Writes that later sessions read | Persistent, attacker-reachable state ("every write is a future prompt") | `gate`, `can_read`, `can_write` (`ch17_memory_policy.py`); `SecureMemoryStore` (`ch17_memory_security.py`) |
| Third-party code → your agent | MCP servers, tool descriptions, skills | Code running with your permissions | `server_env` (`ch13_mcp_agent.py`), policy allow-list, `ch24_skill_registry.py`, `verify` (`ch26_discovery.py`) |
| Model-written code → host | Commands and tests | Untrusted code | The `sandbox` service in `compose.yaml` via `ch10_sandbox.py` |
| Your org → partner org | Delegated tokens, task data | Discovered is not trusted | `TrustStore`, `verify`, `authorize` (`ch26_discovery.py`) |
| Agent → telemetry | Traces and logs | Copied, retained, widely read | `redact` (`ch28_agentops.py`); `ch28_otel.py` records no arguments or text |

## Controls by layer

Each row says where the control lives. All of these are in code, so the regression scenarios can test them with a model that obeys every injection.

### Identity (Chapter 26)

- **Three identities in every action and log line:** user (`act_for`), agent (`sub`), service (`aud`) (section 26.1).
- **An agent never uses a person's credentials** (section 26.2). It holds only short-lived tokens the harness keeps; the model never sees them.
- **Identity is never a tool argument.** The tool trusts only the signed token. `authorize` refuses a resource owned by another user before any approval is asked (section 26.4).
- `mint` refuses agents not in the `AGENTS` registry, disabled agents, and any scope the registry doesn't list for that agent: the registry is the ceiling.

### Authorization (Chapters 9, 14, 22, 26)

- **Policy enforcement point at the tool:** `authorize` in `ch26_identity.py` checks, in order, signature, issuer, audience, expiry, revocation of the token and its whole `chain`, disabled agent, ownership, scope, `max_amount` and single use, and writes an audit record whatever the outcome (section 26.4).
- **Attenuation only narrows:** `attenuate` allows fewer scopes, an earlier expiry and tighter limits, and records the chain so revoking a parent revokes its children (section 26.5).
- **Step-up for risky actions:** `Session.step_up` mints a one-scope, one-amount, two-minute, single-use token after a person approves (section 26.6). The approval becomes a credential the tool verifies.
- **Approval gate in code:** `run_tool` in `ch09_organizer.py` calls `ask_human` for anything in `NEEDS_APPROVAL`; plan-then-act means what's approved is exactly what runs (sections 9.2 and 9.3). Auto-approval belongs in a reviewed config, not the prompt (section 9.6).
- **Allow-list and approvals for MCP tools:** `Policy.visible_tools` hides tools that aren't allowed; `Policy.decide` refuses them if called anyway and asks a person for `needs_approval` tools, showing complete escaped arguments (section 14.5; rules in `policy.json`).
- **Gateway, deny by default:** `Gateway._check` in `ch30_gateway.py` refuses tools not in `POLICY`, authorizes each call with a Chapter 26 token for the gateway's audience, rate-limits per agent and audits every call (section 30.9).
- **Business rules as a state machine:** states, transitions, rules and numbers from records live in code; model outputs are proposals (Chapter 22, `ch22_guarded.py`).
- **Remote MCP server:** per-tool scopes with `require`, token audience checked with `validate_token_resource=True`, host checking against DNS rebinding (section 30.4, `ch30_remote_mcp.py`). Never pass a user's token through to a downstream API.

### Tools and egress (Chapters 11, 14, 25)

- **The safest tool is the one you don't give.** Rate actions by risk: read-only runs, reversible needs approval or an undo log, hard to reverse always asks, irreversible and severe isn't offered (section 9.1). Limit at the source first: read-only tokens, read-only modes, toolsets, folder limits (sections 14.1 and 14.2).
- **Guards around `run_tool`:** `guarded` in `ch25_guards.py` blocks any call whose arguments contain the per-run `CANARY` or match `SECRETS` (API keys, AWS keys, GitHub tokens, private keys, card-like numbers), and checks egress tools' URLs; blocked calls raise an alert, high severity for the canary (section 25.6).
- **URL rules:** `url_problem` in `ch11_web.py` allows only `https`, matches the allow-list by exact host or subdomain, resolves DNS and refuses any non-global address; `fetch_url` follows redirects by hand and checks every hop (sections 11.7 and 25.4).
- **The trifecta rule:** after any `private_sources` tool runs, `Policy.decide` makes every egress call ask a person, even to an allowed host.
- **Quarantine:** `quarantined_read` is a model call with no tools whose output must match `RECORD` and is stripped of links and markup; the planner sees only checked records; `add_task` refuses senders outside `COMPANY` (section 25.5).
- **Idempotency and checkpoints:** every side effect carries a key that is the same on every attempt; resuming skips finished steps; an unkeyed step that was running at a crash escalates to a person (sections 19.3 and 19.5, `ch19_durable.py`).
- **Sandbox for model-written code:** no network, read-only workspace, no secrets, resource limits (Chapter 10, section 10.4).

### Memory (Chapter 17)

- **Write gate:** `gate` in `ch17_memory_policy.py` refuses secrets and quarantines instruction-like text from non-user sources; `can_write` lets only listed agents write team memory (sections 17.4, 17.7 and 17.8).
- **Read scopes:** `recall` applies `can_read` (owner and scope) to every row before ranking.
- **Memory as a security boundary** (section 17.10, `ch17_memory_security.py`): provenance and trust class on every record; tenant and owner stamped on write; untrusted writes quarantined unless `promote` accepts a plain fact from an allow-listed tool; `authorized` filters by tenant, owner, status and expiry *before* ranking and raises `PermissionError` with a `denied` audit entry for cross-tenant reads; time to live and `purge_expired`; `forget_user`; point-in-time `rollback` that never restores deleted or tampered content; a hash-chained audit log (`verify_audit`) that holds metadata and hashes, never memory text.

### Secrets

- **The service fails closed:** `ch30_service.py` refuses to start without `AGENT_API_KEYS` and warns on keys under 16 characters; there is no default key (section 30.2).
- **Keys compared in constant time** (`hmac.compare_digest`); sessions and logs hold a **key id** (a SHA-256 fingerprint), never the key.
- **Secrets at run time, from the environment;** third-party MCP servers get a minimal environment plus only the names in `pass_env` (section 14.3).
- **The harness holds credentials;** the model never sees them (sections 23.5 and 26.2). The leak scan and the memory gate stop secrets that slip through (S12).
- **Telemetry:** never secrets or tokens; personal data only redacted; prefer references to copies (section 28.3).

### Output

- `sanitize_markdown` removes images from hosts not on the list, shows the real address of every link to one and drops raw HTML (section 25.7). Sanitize at the last step before display.
- Generated SQL, shell or HTML gets the same controls as user input: read-only connections, an authorizer (Exercise 22.6), a sandbox.
- The service returns a generic 502 on model failure; stack traces never reach the caller.

### Supply chain (sections 14.3, 24.7, 30.10)

- Review publisher, needed permissions and code; pin versions; read tool descriptions, not just names; narrow with read-only modes and toolsets.
- **Tool poisoning and rug pulls:** treat descriptions as text the model obeys; re-check the tool list against the allow-list on every change; annotations such as `readOnlyHint` are claims, not permissions.
- **Skills:** `install` in `ch24_skill_registry.py` refuses versions that aren't released or were rolled back, files whose content hash doesn't match the manifest or lockfile, and permissions beyond the skill's trust level; `gate` and `promote` require evaluation first.

### Discovery and cross-org trust (sections 26.9 and 26.10, `ch26_discovery.py`)

- **Discovery proposes; the trust store decides.** `discover` matches declared `capabilities` and never reads the description text, which stays out of context until `verify` passes.
- `verify` checks: publisher trusted and not revoked, trusted for this *kind*, key belongs to the publisher and is neither revoked nor expired, signature matches, and the descriptor's digest equals the **pin** recorded at review. The signature proves who; the pin proves what.
- Compatibility before authorization: never mint a credential for a capability you won't call.
- **Explicit delegation:** the remote agent gets its own token (`sub` names it, `act_for` still names the user), its scopes the intersection of what it asks, what your agent holds and the org's `max_scopes`; refused if it asks for more than your agent holds; lifetime capped by `max_ttl`. Revoking your token stops the partner's, through the chain.
- Key lifecycle: `rotate_key` with a grace period, `revoke_key` with none, `revoke_org`. Every step lands in `DISCOVERY_AUDIT`.

### Audit, revocation and the kill switch (section 26.7)

`AUDIT` records time, decision, reason, scope, audience, agent, user and token id for every `authorize` call. `revoke` puts a token id on the list every check consults (derived tokens die too); `disable` is the kill switch for an agent and all its tokens. Short lifetimes limit the window of a leak. Key rotation is described in section 26.7; in this file it isn't implemented (see below).

## Risk tiers and required controls (section 25.11)

**Risk = capability × autonomy × access × persistence × blast radius**, each scored 1–3 (`FACTORS` in `ch25_risk.py`), so 1–243. It's a judgment aid, not a probability.

| Tier | Score | Adds (each tier keeps the ones below) | Trace review |
| --- | --- | --- | --- |
| 1 Low | 1–8 | Named owner, eval suite that gates changes, audit log | After incidents |
| 2 Moderate | 9–27 | Threat model, scoped tokens, budgets in code, monitoring and alerts | After incidents |
| 3 High | 28–81 | Approval gates, deterministic control plane, regression scenarios, kill switch | Monthly |
| 4 Critical | 82–243 | Isolation (quarantine or sandbox), step-up tokens, red-team run before launch, security sign-off | Weekly |

A factor at 3 adds its own controls whatever the total (`BY_FACTOR`): capability → sandbox; autonomy → monitoring, kill switch; access → scoped tokens, approval gate; persistence → memory gate; blast radius → red team, kill switch. `required_controls(profile)` lists them and `gaps(profile, controls_in_place)` is the launch review as code. The demo scores the date agent 1 (tier 1), the file organizer with auto-approval 12 (tier 2) and the support agent 108 (tier 4); making every refund wait for a person halves it to 54, tier 3. To lower risk, cut one factor and re-score.

**The deterministic control plane** (Card 13): code owns identity, policy and permissions, validation, budgets, approvals, state transitions, audit and rollback. The model may choose among allowed tools, propose values and actions and suggest the next step; it never names the user, writes its own audit record or approves its own action. A control written only in the prompt doesn't count as in place.

## Deterministic versus model-dependent

A **deterministic** control holds whatever the model does, and you test it with exact assertions. A **model-dependent** defense lowers the odds, and you measure it with evaluations (Chapter 27), not unit tests (section 25.10).

| Deterministic (tested with a fully fooled model) | Model-dependent (measure with evals) |
| --- | --- |
| Allow-lists, hidden tools, approval gates, `authorize`, attenuation, step-up | "Tool output is data" in the system prompt (layer 4 of section 14.4, the weakest) |
| Canary, leak scan, `url_problem`, `sanitize_markdown` | Whether the quarantined reader classifies an email correctly (S3) |
| Memory scopes, write gate, `can_write`, session ownership | Whether the model resists an injection in the first place |
| Sender rule, idempotency keys, checkpoints | A model judge's grades (calibrate against human labels) |

Pattern-based controls are deterministic but not complete: the leak scan misses secrets in formats its regex doesn't know, and the memory gate's `INSTRUCTION` pattern misses instructions phrased differently. That's why each scenario lists what remains.

## Regression scenarios and mutation testing

`solutions/tests/test_security_scenarios.py` holds 15 scenarios (attack, control, enforcement, residual risk in `solutions/tests/security_scenarios.json`), each with two tests: **failure mode** (the attack succeeds without the control, proving the test can see it) and **mitigated** (the real code stops it). Run `./course.sh check-solutions -k security_scenarios` (seconds, no API key).

| Category | Scenarios |
| --- | --- |
| Indirect prompt injection | S1 secret sent out, S2 data to an allowed site, S3 external wire request, S4 image-link exfiltration |
| Cross-user and cross-tenant | S5 memory recall, S6 session read, S7 shared-memory poisoning |
| Unauthorized tools and escalation | S8 tool not allowed, S9 read token used to refund or widened |
| SSRF and malicious URLs | S10 internal address or redirect, S11 look-alike host |
| Secrets, permissions, retries | S12 secret in a tool or memory, S13 double charge on retry |
| Approval bypass | S14 no approval or a replayed approval |
| Recovery | S15 crash repeats finished steps |

`dev/security_mutations.py` switches each of **12 controls** off in the real code, one at a time, and checks that the matching mitigated tests fail (results in `verification/security_mutations.json` and `verification/SECURITY.md`): leak scan and egress guard (S1, S12), memory read scopes (S5), session ownership (S6), URL rules (S10, S11), authorization at the tool (S9, S14), policy layer (S2, S8), idempotency keys (S13), approval gate (S14), sender rule (S3), memory write gate (S7, S12), safe rendering (S4), and checkpoints with idempotency switched off together (S13, S15; either one alone protects S15). All 12 are caught. When you add a tool, server or memory, add its scenario with both halves and its residual risk.

## What this kit does not do

The security code is labeled **Production pattern** in `course/code_maturity.json`: the controls and records are the real shape, the implementation is simplified. Verified in the code:

| Area | What the kit does | What a production deployment adds |
| --- | --- | --- |
| Token signing | HS256 with one shared key (`ALGORITHM` in `ch26_identity.py`); `KEY` falls back to a built-in `dev-only-signing-key-change-me-...` if `TOKEN_SIGNING_KEY` is unset | An identity provider signing with a private key; services verify with the public key and can't forge; no default key (section 26.3) |
| Token issuance | Homegrown `mint` and `attenuate` | OAuth 2.x, token exchange (RFC 8693), audience-bound tokens, a policy engine (section 26.8) |
| Revocation, kill switch, single use | `REVOKED`, `DISABLED`, `USED` and `AUDIT` are in-process Python sets and lists, lost on restart and not shared | A shared revocation store every service checks; audit to append-only storage the agent can't write |
| Key rotation | `rotate_signing_key` in `ch26_identity.py` keeps signing keys by key id, with a grace period (0 for an emergency); `rotate_key` in `ch26_discovery.py` does the same for publisher keys. Keys live in process memory | The identity provider rotates asymmetric keys on a schedule and publishes the public keys (JWKS); services never hold a signing key |
| Descriptor signatures | HMAC with shared demo secrets hard-coded in `KEYS` (`ch26_discovery.py`) | Public-key attestations published at the partner's domain; package provenance |
| Cross-org tokens | The partner verifies tokens signed with your key | The partner's authorization server exchanges your token for its own; workload identity with proof-of-possession (DPoP) (sections 26.10 and 30.11) |
| API authentication | Static bearer keys from `AGENT_API_KEYS`, no per-key scopes or expiry; key id is an unsalted SHA-256 prefix | User sign-in or managed keys with scopes, expiry and rotation; enterprise authorization (section 30.11) |
| Remote MCP auth | `StaticTokenVerifier` maps tokens from `.env` to scopes and reports a synthetic one-hour expiry | Verify signed JWTs from your identity provider or call its introspection endpoint (section 30.4) |
| Rate limits and session locks | In-process buckets and locks in `ch30_service.py`; per-agent counters in `ch30_gateway.py` | A shared store (such as Redis) across processes |
| Gateway audit | One JSON line per call, arguments redacted with `redact` from `ch28_agentops.py` (section 28.3), written to a local file | Audit storage agents can't write, kept for the retention period; the gateway calls servers with its own credentials (section 30.9) |
| Memory store | `SecureMemoryStore` is in memory; content hashes are plain SHA-256 (guessable for short texts); tenant isolation is application code | Per-tenant encryption keys and crypto-shredding, keyed hashes, row-level security or a database per tenant, a legal-owned retention policy, deletion propagated to indexes, embeddings and caches, a quarantine review UI (section 17.10) |
| Approvals | `ask_human` and `console_approver` read `y` from the terminal | An approval service that authenticates the approver, records who approved what, and shows the full action |
| Leak scan | A short regex list (`SECRETS`) | Your secret formats, a secrets manager so real secrets never reach the agent, egress through a proxy |
| SSRF | DNS checked before the request | Pin the resolved address or use an egress proxy, against DNS rebinding (S10's residual) |
| Risk model | `gaps` trusts the list of controls you pass in | Profiles read from the agent inventory; a control counts only with evidence (a passing scenario, a scope in the registry) |
| Discovery trust store | Python objects built in `demo_world` | Trust as reviewed data in gateway policy, checked on every call, backed by a contract with the partner |

Production-hardened code (real key management, durable storage, load and failure testing, monitoring, a security review) is not in the kit. Section 30.7's launch checklist and the tier from section 25.11 say what it takes.

## Before launch: the security lines of the checklist (section 30.7)

- [ ] Every endpoint except health needs a key or sign-in; the service refuses to start without its keys.
- [ ] The agent has its own identity and short-lived, scoped tokens; tools check ownership and limits.
- [ ] Every write tool needs approval or a reviewed policy; risky actions use step-up tokens.
- [ ] Egress only to allowed sites; canaries and a leak scan guard the tools; rendered output is sanitized.
- [ ] Generated code runs in an isolated sandbox with no secrets.
- [ ] Injection red-team tests pass with a model that obeys the attacker (Exercise 25.6).
- [ ] Remote MCP servers verify token audience and scopes; HTTPS everywhere.
- [ ] Sessions are private to their owner; keys are stored and logged only as fingerprints.
- [ ] A kill switch disables the agent, a single tool or an agent identity at once.

Check the agent against the OWASP Top 10 for Agentic Applications as well; section 25.9 maps each risk (ASI01–ASI10) to the defense in the book.

## Where this comes from

- Chapter 9 (sections 9.1–9.6): `course/code/ch09/ch09_organizer.py`.
- Chapter 14 (sections 14.1–14.5): `ch14_policy_agent.py`, `policy.json`, `ch13_mcp_agent.py`.
- Sections 17.4, 17.7, 17.8 and 17.10: `ch17_memory_policy.py`, `ch17_memory_security.py`.
- Chapter 25 (sections 25.1–25.11, including 25.2 threat model, 25.10 regression scenarios, 25.11 risk model and control plane): `ch25_guards.py`, `ch25_quarantine.py`, `ch25_risk.py`, `ch11_web.py`.
- Chapter 26 (sections 26.1–26.10): `ch26_identity.py`, `ch26_discovery.py`.
- Sections 30.2, 30.4, 30.7, 30.9, 30.10 and 30.11: `ch30_service.py`, `ch30_remote_mcp.py`, `ch30_gateway.py`.
- Section 24.7 and `ch24_skill_registry.py`; Chapter 19 and `ch19_durable.py`; Chapter 10 and `ch10_sandbox.py`; section 28.3 and `ch28_agentops.py`.
- Cards 12 and 13 in Appendix I; the case study's threat model.
- `solutions/tests/security_scenarios.json`, `solutions/tests/test_security_scenarios.py`, `dev/security_mutations.py`, `verification/SECURITY.md`.
