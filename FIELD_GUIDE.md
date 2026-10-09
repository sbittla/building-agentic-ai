# Field Guide: Running a Forward-Deployed Engagement

The working companion to Chapter 31 of *Building Agentic AI Systems*. The chapter teaches the core: a measurable brief, the smallest valuable slice, a design checked against the customer's rules, a pilot gate and a handoff. This guide holds the detail you need on an engagement: how the role compares with the ones around it, the week-by-week workflow, checklists to take into each meeting, the conversations that decide whether a pilot survives, and the demo. The code is `course/code/ch31/ch31_field.py`; Capstone 7 is a whole engagement to practise on. For interview preparation, see [INTERVIEW_PREP.md](INTERVIEW_PREP.md).

The section numbers in brackets are where the book teaches the idea.

## 1. The role

A forward-deployed engineer (FDE) ships working software inside one customer's business and stays until it moves the customer's metric, then hands it over so it runs without them (31.1).

| Role | Owns | Measured by | Writes production code? |
| --- | --- | --- | --- |
| Product engineer | One product, for every customer | Features shipped, reliability | Yes |
| Solutions engineer | The sale: demos, proofs of concept, answering technical questions | Deals won | Rarely |
| Consultant | Advice and a plan | The client's satisfaction with the plan | Sometimes |
| Support engineer | Problems after launch | Time to resolve | Fixes, not features |
| **Forward-deployed engineer** | **One customer's outcome**, end to end | **The customer's metric moving**, then adoption | **Yes, in their environment** |

The role began at Palantir and spread with generative AI: by 2026 OpenAI, Anthropic (as Applied AI Engineers), Scale AI, Databricks and many AI startups hire engineers whose job is to make agents work at a specific customer.

### Skills, and where the book builds them

| Skill | Where you build it |
| --- | --- |
| Breaking down an open-ended problem | Sections 31.2 and 31.3, Chapter 20 (planning) |
| Designing for a regulated customer | Section 31.4, Chapters 18, 25, 26 and 30 |
| Practical code under messy conditions | Chapters 7, 8 and 19 |
| AI depth: prompting, retrieval, agents, evaluation | Chapters 1, 16, 18 and 27 |
| Performance and cost | Chapter 29 |
| Customer communication | Section 31.5 and sections 3 and 4 of this guide |
| Ownership end to end | The capstones, especially Capstone 7 |

## 2. The engagement, week by week

A typical six-to-ten-week engagement. Stretch or compress it, but keep the order: every stage has an exit you can check.

| Weeks | Stage | What you do | Exit (check in code where you can) |
| --- | --- | --- | --- |
| 0 | Kick-off | Meet the sponsor and the customer owner; get access requests started (they take longest); agree how you'll communicate | Named owner; access tickets filed |
| 1–2 | Discovery | Interview the people who do the work; watch it; collect the last ten real cases; run a time study for the baseline | `check_brief` passes (31.2) |
| 2 | Slicing | List candidate slices with value, effort, risk and needed capabilities; agree the first one | `rank_slices` table agreed with the owner (31.3) |
| 2–3 | Design review | Meet their security team and data protection officer; write their rules as an `Environment`; review the design | `check_design` returns no violations (31.4) |
| 3 | Acceptance criteria | Agree success rate, p95, cost per task, critical failures, minimum runs and the gain on the brief's metric | Criteria signed and committed next to the eval suite (31.5) |
| 3–4 | Proof of concept | Run on their real data, no real users | Eval suite passes on their worst data |
| 4–8 | Pilot | A small group of real users; weekly gate readouts | `pilot_gate` says promote (31.5) |
| 8–10 | Rollout and handoff | Gradual rollout (30.13); train users and operators; walk the runbook with their on-call team | `handoff_gaps` is empty (31.6) |
| After | Field-to-product | Report what you built by hand | `productize` report to the product team (31.7) |

## 3. Checklists

### Discovery

- [ ] Talked to the people who do the work, not only the person who asked.
- [ ] Watched the work at least once; noted where the time really goes.
- [ ] Collected the last ten real cases, not the "typical" one.
- [ ] Measured the baseline yourself (a time study, a log query), with the method written down.
- [ ] One metric with a unit, a baseline, a target and a named customer owner.
- [ ] Constraints from their security team and data protection officer, in writing.
- [ ] Non-goals written down and agreed.
- [ ] Open questions listed, each with an owner and a date.

### Design review (customer environment)

The technical launch checklist is section 30.7; these are the items only a customer's environment adds. `check_design` enforces them.

| Rule | What usually breaks it | Where the book handles it |
| --- | --- | --- |
| Data residency | Managed services in a default region | Section 18.3, section 30.6 |
| Model hosting | A provider endpoint outside the allowed region; no local option | Section 24.6, Appendix H |
| Egress | A tool, library or telemetry exporter calling home | Section 25.4, section 30.9 |
| Personal data in logs | Tracing that records prompts and tool results | Section 28.3 |
| Retention | Caches, traces and memories kept "just in case" | Section 17.6, section 28.3 |
| Sign-in | API keys or local accounts instead of their identity provider | Chapter 26, section 30.11 |
| Write access | A connector that can change the system of record | Chapter 9, Chapter 22 |
| Audit | Reads and writes nobody can reconstruct | Section 9.4, section 26.7 |

- [ ] An integration contract for every data source: what you read, how often, what happens when a field is missing or the format changes (section 7.3).
- [ ] Tested on their ugliest data first, not the sample they sent.
- [ ] No API? Exports, a database view or a reporting API checked before a browser agent (section 23.1).
- [ ] If their rules force a weaker model, both models evaluated against the brief's target, with the numbers shown.

### Pilot

- [ ] Criteria signed before the first run, committed next to the evaluation suite.
- [ ] Stages agreed: proof of concept (feasibility, no real users), pilot (value, a small group), general release (scale), each with its own criteria.
- [ ] A weekly readout of the gate's decision, with the interval, not a point estimate.
- [ ] Every complaint example added to the evaluation suite (section 30.14).
- [ ] A critical failure stops the pilot; the customer owner hears the same day.

### Handoff

The technical items (runbook, kill switch, SLOs, dashboards, pinned versions) are in section 30.7's launch checklist. The handoff adds the ones that make the customer the owner:

- [ ] A named team on their side owns it in production.
- [ ] Their on-call team has walked through the runbook with you.
- [ ] They can run the evaluation suite themselves, with the signed criteria.
- [ ] They have tested the kill switch.
- [ ] Escalation: who calls whom, on both sides, and how fast.
- [ ] Users trained to check the output (for example, a summary's citations) and to know when not to trust it.
- [ ] Known limitations written down.

## 4. The conversations

**When it slips.** Tell the customer owner early, in plain words: what happened, what you've already done, the new date and how confident you are in it, what they can have now, and an option to cut scope instead of moving the date. Then don't surprise them again. A slip told early costs a little trust; a slip discovered costs all of it.

**When they say it's wrong.** "It's wrong 20% of the time" is the most common pilot complaint and the most useful one. Ask for the examples, classify them with the failure taxonomy (section 28.8), fix the largest class first, and add every example to the evaluation suite so it can't come back (section 30.14). Report progress on the agreed metric, not on anecdotes, in both directions.

**When they want something their own rules forbid.** Say so plainly, show the rule, and offer the closest design that keeps it. Any exception is their security owner's decision, in writing.

**When the pilot succeeded but nobody uses it.** Go back to the users: watch them work, find what stops them (trust, workflow fit, training), and make adoption the metric for the next iteration.

## 5. The demo

Demos win engagements and lose them. A few rules keep them honest:

- **Use their data.** A demo on your sample data proves you can build a demo. One on twenty of their real files, chosen by them, proves the system can do their work.
- **Show the boundaries.** Show what it refuses, where a person approves (Chapter 9) and what it does with a file it can't read. Customers trust a system that knows its limits more than one that never fails on stage.
- **Rehearse failure.** Have a recorded run ready for when the network fails, and say so if you use it.
- **End with the number.** Close on the brief's metric and the acceptance criteria, not on the most impressive answer.

## 6. Practice

Exercise X.3 in [EXTRA_PRACTICE.md](EXTRA_PRACTICE.md) ("The hard conversations") practises section 4. Capstone 7 runs a whole engagement, from a vague request to a signed-off pilot.
