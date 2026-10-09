# Afterword: Where to Go from Here

You started this book with one model call that couldn't tell you today's date. You finish it able to build agents that look things up, change things safely, work in teams, run for hours, defend themselves and report on their own health. This short afterword puts the pieces in one place, answers Chapter 1's first question again and points to what comes next.

## The support agent, start to finish

Follow the support agent through the lifecycle of section 1.10, and you've followed the book:

Table: The support agent through the lifecycle
| Stage | What the support agent got | Where |
| --- | --- | --- |
| Decide | Some emails need lookups and judgment, so a fixed workflow isn't enough; refunds stay under rules in code | Sections 1.3 and 1.6 |
| Design | A design note: its tools, what it needs to know at each step, what could go wrong | Exercise 1.7 |
| Build | Tools, a loop, state, a carrier API, approvals, MCP servers, context, memory, a knowledge base, durable refunds, routing, specialists and a state machine | Chapters 2–24 |
| Secure | An injection-resistant design, memory it can't be tricked into keeping, a risk tier and its own identity | Sections 17.10 and 25.11, Chapters 25 and 26 |
| Evaluate | Real support questions, handoff cases, attempts to read another customer's order and injected instructions, run with trials and summarized in a scorecard | The measurement interlude, Chapter 27 |
| Optimize | Retrieval instead of a pasted handbook, a small model where it's enough, a cost per resolved conversation inside budget | Chapters 16, 20 and 29 |
| Deploy | A CI gate, a launch checklist, a secure container and a gradual rollout | Sections 27.7, 30.7 and 30.13 |
| Operate | Traces, SLOs, alerts and a cost per resolved conversation | Chapters 28 and 29 |
| Improve | Every real failure becomes a new test case, and fixes reach production through the improvement loop | Sections 27.8 and 30.14 |
| Retire | One day it's replaced; its tokens are revoked and its memories handled by policy | Section 30.13 |

The case study before the capstones follows it through one release in detail: the decisions, the evidence for each, what testing changed, and an incident and its rollback. Capstone 1 asks you to build that agent yourself. If you've done it, you've done what production teams do.

## Chapter 1's question, again

Section 1.3 asked: *do you actually need an agent?* You can answer it better now. Choose the least autonomy that does the job. Give the model what needs judgment (understanding a messy request, drafting a reply, deciding the next step) and give code everything that must be right every time: the rules, the numbers, the permissions and the stop conditions. That was Chapter 22's lesson, and it's the one most production incidents in this book came back to.

## What stays true

Models will change faster than this book can. These ideas have held as models improved, and they should keep holding:

- An agent is a model, tools and a loop, with a stop condition. Every framework is that loop with features added.
- A tool is a contract: a clear name, a description that says when to use it, a schema, and errors the model can act on.
- The model proposes; code decides. Rules that matter are enforced where the action happens, never only in the prompt.
- The model knows only what's in its context, so choosing that context, step by step, is the craft.
- A change is an improvement only when a measurement says so.
- Give every agent its own identity and only the permissions its task needs; assume text from outside will try to turn it against you.

Appendix I collects the book's frameworks as reference cards for design reviews and on-call.

## Where the field is going

A few developments you'll meet as you keep building. Each reuses what you already know:

- **Computer use** (Chapter 23) and **agent-to-agent protocols** such as A2A (Chapter 21) are now core techniques rather than previews. Claude's API also offers computer use and a hosted browser as ready-made toolsets; the controls from Chapter 23 apply to them unchanged.
- **An advisor for the executor.** A cheaper, faster model does the work and consults a stronger model only for hard decisions. Claude's API offers this as an *advisor tool*; it's the orchestrator-and-workers idea from Chapter 11, inside a single agent.
- **Agents that buy things.** Payment networks and AI companies are building protocols for agents to shop and pay on a user's behalf. Every lesson on approvals (Chapter 9), budgets (Chapter 29) and identity (Chapter 26) applies, because a mistake now costs real money.
- **Agent identity in the protocols themselves.** MCP's roadmap makes agent identity a priority (section 30.11). When it lands, the tokens you built in Chapter 26 become a standard.

## What to do next

- **Build a capstone**, if you haven't: pick the one that matches the work you want to do (the table at the end of the capstones), and take it to the full rubric.
- **Build one for someone else.** If your work puts you in front of customers, Chapter 31's playbook and Capstone 7 turn everything here into an engagement: a measurable brief, the smallest valuable slice, a design that fits their rules and a pilot they agreed to judge. Appendix M collects the interview questions for these roles.
- **Bring one agent to work.** Start with a read-only assistant over data your team already asks about. Write its eval suite before you show it to anyone.
- **Keep up without chasing.** Appendix G lists where to ask for help and how to follow the field. When a new feature appears, ask which layer of the reference model it belongs to and which control it needs; you'll usually find you already know how to use it safely.

Thank you for building along. The best way to learn this craft is the way you've been doing it: build the thing, break it, measure it and make it better.
