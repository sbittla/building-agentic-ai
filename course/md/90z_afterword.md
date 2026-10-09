# Afterword: Where to Go from Here

You started this book with a model that couldn't tell you today's date. You finish it able to build agents that look things up, change things safely, work in teams, run for hours, defend themselves and report on their own health. These last pages put the pieces together and point you at what to build next.

## The support agent, start to finish

Chapter 1 promised a support agent that would one day answer Priya properly: find her order, check the delivery date and refund the express fee only if the rules allow it. Follow that agent through the lifecycle of section 1.10 and you've retraced the book:

Table: The support agent through the lifecycle
| Stage | What the support agent got | Where |
| --- | --- | --- |
| Decide | Emails need lookups and judgment, so a fixed workflow isn't enough; refunds stay under rules in code | Sections 1.3 and 1.6 |
| Design | A design note: tools, what it needs to know, what could go wrong | Exercise 1.7 |
| Build | Tools, a loop, state, approvals, MCP servers, memory, a knowledge base, durable refunds, routing and a state machine | Chapters 2–24 |
| Secure | Injection resistance, guarded memory, a risk tier and its own identity | Chapters 17, 25 and 26 |
| Evaluate | Real questions, handoffs, cross-customer reads and injected instructions, run with trials and summarized in a scorecard | The measurement interlude, Chapter 27 |
| Optimize | Retrieval instead of a pasted handbook, a small model where it's enough, cost per resolved conversation inside budget | Chapters 16, 20 and 29 |
| Deploy | A CI gate, a launch checklist and a gradual rollout | Sections 27.7, 30.7 and 30.13 |
| Operate | Traces, SLOs, alerts and a capacity plan | Chapters 28 and 29 |
| Improve | Every real failure becomes a test case, and fixes ship through the improvement loop | Sections 27.8 and 30.14 |
| Retire | Tokens revoked, memories handled by policy | Section 30.13 |

The case study follows it through its first months in production, incident and rollback included, and Capstone 1 has you build it yourself. Do both and you've done what production teams do.

## Chapter 1's question, again

Section 1.3 asked: *do you actually need an agent?* You can answer it better now. Choose the least autonomy that does the job, and split the work the way Chapter 22 did: the model proposes, code decides. Judgment goes to the model (reading a messy request, drafting a reply, choosing the next step); rules, numbers, permissions and stop conditions stay in code. Most of the failures this book guards against, from the message trying to talk its way to a $5,000 refund to the case study's missed handoffs, come from forgetting that split.

## What stays true

Models will change faster than this book can. These ideas should keep holding:

- An agent is a model, tools and a loop with a stop condition. Every framework is that loop plus features.
- A tool is a contract: a clear name, a description of when to use it, a schema and errors the model can act on.
- The model proposes, code decides. Rules that matter are enforced where the action happens, never only in the prompt.
- The model knows only what's in its context, so choosing that context, step by step, is the craft.
- A change is an improvement only when a measurement says so.
- Every agent gets its own identity and only the permissions its task needs. Assume outside text will try to turn it against you.

Appendix I keeps these as reference cards for design reviews and on-call.

## Where the field is going

You'll meet these as you keep building, and each reuses what you already know:

- **Computer use** (Chapter 23) and **agent-to-agent protocols** such as A2A (Chapter 21) have moved from previews to core techniques. Model providers now ship them as ready-made toolsets; Chapter 23's controls still apply.
- **An advisor for the executor.** A cheaper, faster model does the work and consults a stronger one only for hard decisions. It's Chapter 20's routing and Chapter 11's orchestrator and workers, inside a single agent.
- **Agents that buy things.** Payment networks and AI companies are building protocols for agents to pay on a user's behalf. Approvals (Chapter 9), budgets (Chapter 29) and identity (Chapter 26) all apply, because now a mistake costs real money.
- **Agent identity in the protocols themselves.** MCP's roadmap makes agent identity a priority (section 30.11). When it ships, the tokens you built in Chapter 26 become a standard.

## What to do next

- **Build a capstone**, if you haven't. Pick the one that matches the work you want to do (the table at the end of the capstones) and take it to the full rubric.
- **Build one for someone else.** Chapter 31 and Capstone 7 turn everything here into a customer engagement, from a measurable brief to a pilot they agreed to judge. `INTERVIEW_PREP.md` in the kit collects interview questions for these roles.
- **Keep up without chasing.** Appendix G lists where to get help and follow the field. When a new feature appears, ask which layer of the reference model it belongs to and which control it needs. Usually you already know how to use it safely.

Then bring one agent to work. Pick a task people near you do by hand every week, and start read-only, over data your team already asks about. The dullest useful task is the best place to start. Write its eval suite before you show it to anyone, and put an approval gate in front of anything that changes data. Then measure it, break it and make it better, the way you have all through this book.

Thank you for building along. Now go build the next one.
