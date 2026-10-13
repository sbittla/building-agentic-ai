# Interlude: Measuring an Agent

You change one sentence in the SQL analyst's system prompt, rerun your ten questions, and the score goes from 7 to 8. Did the change help? The same agent asked the same question twice can pass once and fail once, so one run can't say. This interlude shows you how to compare two versions of an agent fairly: run every case several times, report a pass rate with a margin of error and tell a real improvement from luck.

**Prerequisites:** Chapter 4 (agent loop). The testing interlude helps but isn't required.

## Learning objectives

By the end of this interlude you can:

- Keep test cases in a file, one JSON object per line.
- Run every case several times and report the pass rate with a 95% interval.
- Spot flaky cases, which pass on some runs and fail on others.
- Decide whether a change made an agent better, worse, or you can't tell yet.

## Why this interlude

From here on you'll keep comparing: two system prompts, two routers (Chapter 20), with and without a skill (Chapter 24). Chapter 27 builds a full evaluation system; until then you need three ideas: **cases**, **trials** and **margins**.

## M.1 Cases, trials and margins

A **case** is a question plus a way to check the answer. Keep cases in a file with one JSON object per line (the **JSONL** format). The kit has one for the SQL analyst, `eval_sql.jsonl`:

```
{"id": "order-count", "question": "How many orders are there in total?", "answer_sql": "SELECT COUNT(*) FROM orders"}
{"id": "customers", "question": "How many customers do we have?", "answer_sql": "SELECT COUNT(*) FROM customers"}
```

A **trial** is one run of one case. You run each case several times, because the model varies.

A **margin** says how far the true pass rate might be from the one you measured. Nine passes out of ten sounds like 90%, but with only ten runs the real rate could be anywhere from about 60% to 98%. The **95% interval** is the range that very likely contains the real rate, given that much data.

This file measures two simulated agents, so watching the effect costs nothing:

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

B really is better. With one run per case the two versions tie, and with three you still can't be sure. With thirty runs per case, the intervals finally separate.

## M.2 Reading the results

Table: Reading two measured versions
| You see | It means | Do this |
| --- | --- | --- |
| The intervals don't overlap | The difference is real | Keep the better version |
| The intervals overlap | You don't know yet | Run more trials or, better, add cases |
| A case passes on some runs and fails on others | The case is **flaky** | Read its failing runs; the agent is guessing there |
| 100% on ten runs | The real rate is probably above 70%, nothing more | Add harder cases before celebrating |

When you have time for more runs, spend it on new cases rather than repeats: thirty different questions tell you more than ten run three times, because trials catch randomness while new cases catch blind spots. And change one thing at a time, or you can't say which change helped.

:::tip The same check, every time
Write the check in code: the expected number appears in the answer, the right tool was called, the query ran read-only. A check you apply by eye drifts with your mood. Chapter 27 adds model-graded checks for what code can't judge.
:::

`compare` is cautious on purpose: it calls a version better only when the intervals don't overlap at all. Chapter 27's release gate uses a sharper test, but the cautious rule never reports a difference that isn't there.

## Key takeaways

- A case is a question and a check; add one to your JSONL file whenever the agent fails in a new way.
- Run every case several times: one run is an anecdote.
- Report a pass rate with its 95% interval; small samples have wide intervals.
- When the intervals overlap, you can't tell yet.
- Flaky cases show where the agent is guessing.

Chapter 27 builds on these definitions, adding pass^k (does a case pass on every one of k tries?) and the agent scorecard (section 27.6), where every later metric is defined once. Chapter 28 turns those metrics into SLOs (service-level objectives) for the agent in production, and Chapter 29 into latency, capacity and cost targets.

## Learn more

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

## Up next

So far a mistake has cost you a wrong number or a task to delete. In Chapter 9 an agent starts moving files, and a mistake can be a signed contract filed where you'll never find it.
