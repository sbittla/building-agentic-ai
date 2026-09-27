# Pilot guide: testing *Building Agentic AI Systems* with real learners

A pilot shows where real beginners get stuck before the book goes on sale. Plan on **two or three learners**, at least one on **Windows** and at least one who has **never programmed**. Each works alone for two to three weeks, then you meet once to go through their notes.

## 1. Before the pilot (you)

- [ ] Run `./course.sh selftest` and `./course.sh check-solutions` on a clean machine. Both must pass.
- [ ] Run `./course.sh live-check --yes` with your own API key. Fix every FAIL, and compare each output in `workspace/live_report.md` with the "what you should see" notes in `solutions/ANSWERS.md`.
- [ ] Give each learner the book (PDF), `building-agentic-ai.zip` and an API key with a **monthly spending limit** of about $20.
- [ ] Don't help them install anything. Watching where they get stuck is the point.

## 2. What each learner does

| Week | Read and do | Stop when |
| --- | --- | --- |
| 1 | How to Use This Book, Chapter 0, the Python interlude | The Chapter 0 checkpoint passes |
| 2 | Chapters 1–4 and the testing interlude, all Simple exercises plus two Medium | The Part 1 checkpoint passes |
| 3 (optional) | Chapter 12 and exercise 12.4, then one capstone's first milestone | The MCP server works in Inspector |

## 3. The log each learner keeps

Keep a simple log with one line every time something happens that's worth noting:

| When | Page or exercise | What happened | Minutes lost | Solved how? |
| --- | --- | --- | --- | --- |
| 2026-10-02 19:40 | Setup step 3 | Docker said "permission denied" | 25 | Restarted the computer |

Log **anything** that made you stop: an error, a word you didn't know, an instruction you read twice, an exercise you didn't understand, an output that didn't match the book.

## 4. Questions for the end of the pilot

1. Where did you almost give up? What got you going again?
2. Which exercise taught you the most? Which one felt pointless?
3. Was any explanation too fast? Too slow?
4. How long did setup take, from download to your first working `./course.sh check`?
5. Did the "Learn more" links help? Which ones did you use?
6. After Chapter 4, could you explain the agent loop to a friend in two minutes? Try it now.
7. How much did you spend on the API?
8. Would you recommend the book to someone like you? Why, or why not?

## 5. What to fix afterward (you)

- Any step where **two or more** learners lost 15 minutes or more gets a fix in the book: clearer wording, a new hint, a troubleshooting row or a screenshot.
- Every "output didn't match the book" note gets checked against `live_report.md` and fixed in the chapter or in `ANSWERS.md`.
- Screenshots: take them on the pilot learners' machines (Windows and macOS) for **Docker Desktop install**, the **Claude Console API keys page** and the **first successful `./course.sh check --api`**. Add them to Chapter 0.
