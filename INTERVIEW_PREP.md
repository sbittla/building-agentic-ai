# Interview Prep: Agent Engineering and Forward-Deployed Roles

The full question bank behind Appendix M of *Building Agentic AI Systems*. Each answer is a starting point: say it in your own words and back it with something you built. The section or chapter in brackets is where the book teaches it.

Forward-deployed engineer (FDE) loops usually run five to eight rounds: recruiter and hiring manager, practical coding, system design for a real customer, an open-ended decomposition case, AI depth, a client simulation, behavioral, and at some companies a take-home. Interviewers score the same habits in every round: you ask before you build, you measure, you respect the customer's constraints and you own the outcome.

## 1. The role

1. **What does a forward-deployed engineer do?** Ships working software inside one customer's business, in their environment, and stays until it moves the customer's metric; then hands it over so it runs without them. (31.1)
2. **How is it different from a solutions engineer?** A solutions engineer helps win the deal with demos and proofs of concept; an FDE owns the outcome after it, and writes production code in the customer's environment. (31.1)
3. **How is it different from a consultant?** A consultant leaves a plan; an FDE leaves a working system, an owner and a runbook. (31.1, 31.7)
4. **What makes an FDE valuable to the product team?** They see what customers actually need. Fixes built by hand at several customers are evidence for product features. (31.8)

## 2. Discovery and scoping

5. **A customer says "we want AI". What do you do first?** Find the work and the number: who does what today, which outcome matters, and how it's measured now. No solution until there's a brief. (31.2)
6. **What goes into a problem brief?** Users, job, output, one metric with a measured baseline and a target, a named customer owner, constraints and non-goals. (31.2)
7. **Why measure the baseline yourself?** Without today's number nobody can show a gain, and estimates from hopeful people are always optimistic. (31.2)
8. **Why write non-goals?** They stop scope growing in every meeting and make trade-offs explicit. (31.2)
9. **How do you break down an open-ended request?** Users, then decisions, then data, then constraints, then candidate slices; ship the smallest one that moves the metric and fits the constraints. (31.3)
10. **Why not start with the most valuable slice?** The most valuable one is usually the riskiest; the first slice has to earn the trust the others need. (31.3)
11. **The deadline is fixed and the request is vague. What now?** Scope down, write what "done" means, get the owner to choose explicitly between scope and date. (31.2, 31.5)
12. **When should the answer be "don't build an agent"?** When the rules are exact (a function), the steps are known (a workflow), or one prompt does the job. (1.3)
13. **How would you use a model during discovery?** To draft the brief from interview notes with a forced tool call, leaving unknown numbers empty; code still decides whether the brief is ready. (31.2)

## 3. System design for a customer

14. **Design a document assistant for a hospital whose data can't leave its cloud.** Model and index in their account (or a local model), their SSO, permission checks at retrieval time, no personal data in logs, audit trail, citations checked against the text. (18, 25, 26, 31.4)
15. **What rules does a customer environment usually impose?** Data residency, where models may run, an egress allow-list, no personal data in logs, retention limits, their sign-in, no writes to systems of record, audit. (31.4)
16. **How do you catch rule violations before the security review does?** Write the rules down as data and check every design against them in code at each review. (31.4)
17. **Search takes 1.5 s and they need 100 ms.** Measure span by span; cache, route to a smaller model, precompute, cut steps, parallelize, stream; if 100 ms is real, take the model off the request path. (29)
18. **How do you let an agent write to production systems safely?** Its own identity, short-lived scoped tokens, read-only by default, approvals for writes in code, audit and undo. (9, 26)
19. **How do you serve many customers from one platform?** Per-tenant keys, budgets, memory, caches and traces; a gateway that checks every call; evaluation and cost per tenant. (30.9, 30.12)
20. **The customer has no API for the system you need.** Check for exports, a database view or a reporting API first; a browser agent is the last resort, with an allow-list and approvals. (23.1)
21. **How do you handle messy data from a customer?** Write an integration contract per source (fields, frequency, what happens when something is missing), and test on their worst data first. (7.3, 31.4)
22. **Their security team blocks the model you wanted.** Evaluate the allowed one against the brief's target; often it clears the bar for the first slice. Bring numbers to any request for an exception. (31.4)
23. **What's the lethal trifecta?** Private data, untrusted content and a way to send data out, in one agent. Break at least one leg in code. (25)

## 4. AI depth

24. **Prompting, retrieval or fine-tuning?** Prompt first; retrieval for private or changing knowledge; fine-tuning for format, style or a narrow skill, or to cut cost at volume. Decide with evals. (16, 18, 27)
25. **What is context engineering?** Deciding what goes into each model call, from which source, in what order and within what budget, rather than only wording the prompt. (16)
26. **How do you evaluate an agent?** A suite of real tasks with repeated trials, read as confidence intervals and pass^k; outcome, trajectory and cost graded per run. (27)
27. **Why repeated trials?** Models aren't deterministic; one run can't tell 92% from 80%. (27.2, the measurement interlude)
28. **How do you trust a model-graded check?** Calibrate the judge against human labels before relying on it. (27.2)
29. **One agent or a team?** One, until the work splits into independent parts and a measured quality gain pays for the extra tokens. (11, 21)
30. **How do you stop prompt injection?** Not with the prompt: treat read text as data, separate the reader from the actor, allow-list egress, guard actions in code. (25)
31. **How does an agent remember safely?** A memory policy: kind, scope, owner, source, confidence and expiry, with a write gate against poisoning. (17)
32. **What's MCP and why use it?** A protocol for packaging tools and data once so any compatible agent can use them; put a gateway and a policy layer in front. (12–15, 30.9)
33. **When do agents need durable execution?** When work takes longer than a request or must survive crashes: checkpoints, idempotency keys, retries with limits. (19)

## 5. Performance and cost

34. **What makes up an agent's latency?** Model, tools, retrieval, orchestration, queueing and serialization; measure each from traces. (29.1)
35. **Why does cost grow faster than the number of steps?** Each call resends the whole conversation so far. (29.2)
36. **Which cost metric matters most?** Cost per successful task: failures and escalations were paid for too. (29.9)
37. **How do you build a business case?** Compare with the human baseline, not zero; state every assumption; compute payback; test which assumption matters most. (29.9)
38. **How do you find a system's capacity?** Sweep concurrency to find the knee, load-test open-loop at the forecast arrival rate, plan with Little's law. (29.5–29.7)

## 6. Pilots, production and operations

39. **What is a pilot?** An experiment with a question and acceptance criteria agreed before it starts. (31.5)
40. **What goes into acceptance criteria?** A success rate read as an interval, p95 latency, cost per task, zero critical failures, a minimum number of runs and the brief's metric improving by an agreed amount. (31.5)
41. **Promote, hold or stop?** Promote when every criterion is met; hold when evidence is thin or a fixable miss; stop on a critical failure or a rate that misses even optimistically. (31.5)
42. **How do you roll out?** Shadow, then a canary on a small share of traffic with SLOs deciding, then the rest; version the whole agent. (30.13)
43. **What do you monitor in production?** Traces of every model and tool call, failure classes, SLOs on what users feel, error-budget burn, cost per success. (28)
44. **How does the agent improve after launch?** Mine production failures into labeled eval cases, then move each change through offline, shadow and canary gates. (30.14)
45. **What do you hand over when you leave?** Runbook, owner, eval suite with the signed criteria, dashboard, tested kill switch, escalation contacts, training and known limits. (31.7)

## 7. Practical coding

46. **Write a rate limiter with per-user and global limits.** Token buckets per user and global, checked together; return the wait; test bursts and concurrency. (7.6, 30.2)
47. **Make a flaky tool call production-grade.** Timeout, backoff for retryable errors only, idempotency key, clear error for the model, a test per failure. (7.3, 19.4)
48. **Parse a messy export.** Validate fields, keep rejected rows with a reason, report counts. (7.3, the regex interlude)
49. **Write a function that checks a plan before running it.** Known tools, valid dependencies, no cycles, a size limit. (20.3)
50. **Test an agent without calling a model.** Replace the client with a scripted stand-in and assert on the tools, order and arguments. (The testing interlude)

## 8. Customer conversations

51. **Tell the CTO the deployment will slip three weeks.** Early and plain: cause, what's done, the new date and confidence, what they can have now, an option to cut scope. (31.5)
52. **"It's wrong 20% of the time."** Ask for examples, classify them, fix the biggest class, add every example to the suite, report on the agreed metric. (28.8, 31.5)
53. **The customer wants a feature that breaks their own security rule.** Say so plainly, show the rule, and offer the closest design that keeps it; let their security owner decide on any exception in writing. (31.4)
54. **A stakeholder wants a demo next week on "everything".** Demo one slice on their real data, show the boundaries and end with the brief's metric. (31.6)
55. **The pilot succeeded but nobody uses it.** Go back to the users: watch them work, find what stops them (trust, workflow fit, training) and treat adoption as the metric for the next iteration. (31.2, 31.7)

## 9. Behavioral

56. **Something you owned end to end.** Situation, task, action, result with numbers; show you scoped, measured, shipped and handed over.
57. **A time you were wrong.** How you found out (ideally a measurement), what you changed, what you do now.
58. **A conflict with a customer or a colleague.** What each side needed, how you made the trade-off explicit, and the outcome.
59. **A time you said no.** The request, why it would have hurt the customer, and what you offered instead.

## 10. Cases to practice

Talk through users, decisions, data, constraints and the first slice; then the design; then how you'd know it worked. About 30 minutes each.

1. A logistics company wants to "use AI in customer service": late deliveries, address changes and damage claims; an order API with no sandbox; data must stay in the EU.
2. A bank's compliance team spends two days a month gathering audit evidence from tickets, chats and spreadsheets; nothing may be written to the ticketing system; every answer needs a source.
3. A manufacturer wants an agent that answers technicians' questions from 4,000 PDF manuals, many scanned, on tablets with poor connectivity.
4. An insurer wants to "reduce claim handling time" (Chapter 31's Lakeside engagement): run it yourself before reading the chapter's answers.
5. A hospital network wants help with shift handovers (Capstone 7): write the brief and the acceptance criteria before you design anything.
