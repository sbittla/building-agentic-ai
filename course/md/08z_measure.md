# Interlude: Measuring an Agent

Chapter 8 checked the SQL analyst against answers you knew were right. That's the start of measuring an agent, but one run of each question isn't enough: the same agent, asked the same question twice, can pass once and fail once. This short interlude turns checking into measuring. You'll run every case several times, report a pass rate with a margin of error, and learn when a change is really an improvement and when it only looks like one.

**Prerequisites:** Chapter 4 (agent loop). The testing interlude helps but isn't required.

## Learning objectives

By the end of this interlude you can:

- Keep test cases for an agent in a case file, one JSON object per line.
- Run every case several times and report the pass rate with a 95% interval.
- Spot flaky cases, the ones that pass on some runs and fail on others.
- Decide whether a change made an agent better, worse, or whether you can't tell yet.

## Why this interlude

From here on, the book keeps asking you to compare: two system prompts, two routers (Chapter 20), with and without a skill (Chapter 24), one framework against another. A model's answers vary from run to run, so a single run can make a worse version look better. Chapter 27 builds a full evaluation system. This interlude gives you the three ideas you need before then: **cases**, **trials** and **margins**.

## M.1 Cases, trials and margins

A **case** is a question plus a way to check the answer. Keep cases in a file, one JSON object per line (the **JSONL** format), so they're easy to add to and to review. The kit already has one for the SQL analyst, `eval_sql.jsonl`:

```
{"id": "order-count", "question": "How many orders are there in total?", "answer_sql": "SELECT COUNT(*) FROM orders"}
{"id": "customers", "question": "How many customers do we have?", "answer_sql": "SELECT COUNT(*) FROM customers"}
```

A **trial** is one run of one case. Run each case several times, because the model doesn't give the same answer every time.

A **margin** says how far the true pass rate might be from the one you measured. Nine passes out of ten sounds like 90%, but with only ten runs the agent's real rate could be anywhere from about 60% to 98%. The **95% interval** is the range that, with that much data, very likely contains the real rate.

This file measures two simulated agents, so you can see the effect without spending anything:

@@code i_measure.py::wilson~,load_cases~,contains_expected,run_suite,compare,simulated_agent

Run it with `./course.sh python i_measure.py`:

```
Version A really succeeds 70% of the time, version B 80%.

1 trial(s) per case, 10 cases
  version A      7/10   =  70%   95% interval  40% to  89%
  version B      7/10   =  70%   95% interval  40% to  89%
  B against A: can't tell yet: the intervals overlap, so run more trials or more cases

3 trial(s) per case, 10 cases
  version A     21/30   =  70%   95% interval  52% to  83%
  version B     24/30   =  80%   95% interval  63% to  90%
  B against A: can't tell yet: the intervals overlap, so run more trials or more cases

30 trial(s) per case, 10 cases
  version A    208/300  =  69%   95% interval  64% to  74%
  version B    242/300  =  81%   95% interval  76% to  85%
  B against A: better
```

B really is better, but with one run per case the two versions tie, and with three runs per case you still can't be sure. Only with enough runs do the intervals separate.

## M.2 Reading the results

Table: Reading two measured versions
| You see | It means | Do this |
| --- | --- | --- |
| The intervals don't overlap | The difference is real | Keep the better version |
| The intervals overlap | You don't know yet | Run more trials or, better, add cases |
| A case passes on some runs and fails on others | The case is **flaky** | Read its failing runs; the agent is guessing there |
| 100% on ten runs | The real rate is probably above 70%, nothing more | Add harder cases before you celebrate |

Two habits make measurements trustworthy:

- **More cases beat more trials of the same case.** Thirty different questions tell you more than ten questions run three times, because they cover more of what users will ask. Trials catch the randomness; new cases catch the blind spots.
- **Change one thing at a time.** If you change the system prompt and the tools together, you can't say which one helped.

:::tip The same check, every time
Write the check in code, not by eye: the expected number appears in the answer, the right tool was called, the query ran read-only. A check you apply by eye drifts with your mood. Chapter 27 adds model-graded checks for things code can't judge, and shows how to make sure they agree with people.
:::

`compare` is cautious on purpose: it calls a version better only when the two intervals don't overlap at all. Chapter 27's CI gate uses a sharper statistical test, but the cautious rule never tells you something that isn't there.

## Key takeaways

- A case is a question and a check; keep cases in a JSONL file and add to it whenever the agent fails in a new way.
- Run every case several times: one run is an anecdote.
- Report a pass rate with its 95% interval; small samples have wide intervals.
- A change is an improvement only when the intervals say so; when they overlap, you can't tell yet.
- Flaky cases show where the agent is guessing.

These definitions are the start of one progression. Chapter 27 builds on them without redefining them: it adds pass^k and the agent scorecard (section 27.6), where every metric the rest of the book uses is defined once. Chapter 28 turns those metrics into SLOs, and Chapter 29 into latency, capacity and cost targets.

You can now tell a real improvement from luck. Chapter 9 gives an agent its first actions that change things, behind an approval gate, and from then on every comparison in this book can be measured this way.

## Learn more

Start with these. `RESOURCES.md` in the course kit has all 3 links for this chapter, including the **Go deeper** reading, ready to click.

| Resource | What you'll find |
| --- | --- |
| **Anthropic: Demystifying evals for AI agents**<br>[anthropic.com/engineering/demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Tasks, trials and graders, and why agents need repeated runs |
| **Claude docs: Define success criteria and build evaluations**<br>[platform.claude.com/docs/en/test-and-evaluate/develop-tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) | Writing test cases and checks for a model-based system |

## Exercises

:::ex Concept | M.1 | Is B better?
Version A of an agent passed 17 of 20 runs; version B passed 19 of 20. Use `wilson` to work out both 95% intervals, then decide: is B better, and what would you do next?
**Done when:** You have both intervals and a decision with a reason.
:::

:::ex Simple | M.2 | Watch the margins
Run `i_measure.py`. Then change the two success rates to 0.78 and 0.80 and try 30, 100 and 300 trials per case.
**Done when:** You can say roughly how many runs it takes to separate 78% from 80%, compared with 70% from 80%, and why small differences need so many more.
:::

:::ex Medium | M.3 | Measure the SQL analyst
Measure the SQL analyst on `eval_sql.jsonl`, three trials each, passing when the answer contains the `answer_sql` value. Report rate, interval and flaky cases; change one prompt sentence, re-measure, `compare`.
**Done when:** two reports, a `compare` verdict, and the flaky cases named.
---kit---
Measure the Chapter 8 SQL analyst on the cases in `eval_sql.jsonl`, three trials each: a case passes when the answer contains the value its `answer_sql` returns. Report the pass rate with its interval and the flaky cases. Then add one sentence to the system prompt, measure again and use `compare`.
**Hint:** `run_suite` takes your agent as a function of the question and your check as a function of the answer and the case; run `answer_sql` on a read-only connection to get the expected value.
**Done when:** You have two reports and a verdict from `compare`, and you can say which cases were flaky.
:::
