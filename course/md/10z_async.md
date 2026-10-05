# Interlude: Asynchronous Python

Agents spend most of their time waiting on the model, an API or a server. This short interlude shows you how to make those waits overlap, so a program can do several things at once. You'll run a small timing demo, learn to read async agent code and fix the two most common async bugs.

## Learning objectives

By the end of this interlude you can:

- Explain why async code helps agents that spend most of their time waiting.
- Use `async def`, `await`, `asyncio.run` and `asyncio.gather`.
- Run blocking code with `asyncio.to_thread`, and set deadlines with `asyncio.wait_for`.
- Read the async code in Chapters 11, 13 and 19, and avoid the two classic async bugs.

## Why this interlude

Chapter 11 runs several subagents at the same time, and Chapters 13, 14 and 19 talk to MCP servers and web clients. All of this uses **asynchronous** (async) Python. It looks unusual at first, but you need only five ideas.

## A.1 Waiting without blocking

Most of an agent's time goes to **waiting**: for the model, for an API, for a server. Normal Python code waits for one thing at a time. Async code can start several waits and let them overlap, all in one program.

@@code i_async.py

Run it with `./course.sh python i_async.py`. Two one-second waits take two seconds one after the other, but one second with `gather`.

@@image d-f6804fb92916.png

Figure: Two requests that overlap with `asyncio.gather`
Alt: Sequence diagram: your program sends a request to a weather API and one to a news API without waiting for the first; both reply after one second, so with gather the two waits overlap and take about one second in total.

## A.2 The five ideas

Table: The five async ideas
| Idea | Syntax | Meaning |
| --- | --- | --- |
| Coroutine | `async def f():` | A function that can pause while it waits |
| Await | `await f()` | "Run this, and let other work happen while it waits" |
| Run | `asyncio.run(main())` | Start the async world, once, at the top of the program |
| Gather | `await asyncio.gather(a(), b())` | Run several coroutines at the same time and collect all results |
| To thread | `await asyncio.to_thread(slow_func)` | Run ordinary blocking code without freezing the others |

You'll meet two more: `async with` opens something that must be closed later (such as an MCP connection), and `asyncio.wait_for(x, timeout=5)` gives up after a deadline.

:::warn The two classic async bugs
**Forgetting `await`:** `result = fetch()` gives you a coroutine object, not a result, and Python warns "coroutine was never awaited". **Blocking the loop:** calling `time.sleep()` or a slow normal function inside async code freezes everything, because all coroutines share one *event loop*, the scheduler that switches between them. Use `await asyncio.sleep()` or `asyncio.to_thread()` instead.
:::

## A.3 Reading async agent code

When you see this in Chapter 11 or 13:

```
# open the connections, and close them at the end
async with MCPHub(config) as hub:
    # run the subagents in parallel
    findings = await asyncio.gather(*(run_subagent(t) for t in tasks))
```

Read it as: *connect to the servers; run all subagents at once and wait for all of them; then disconnect.* The `*` spreads a list of coroutines into separate arguments for `gather`.

## Summary

- Async lets one program overlap many waits: for the model, APIs and servers.
- `async def` defines, `await` waits, `asyncio.run` starts and `gather` runs things at the same time.
- `to_thread` keeps blocking code from freezing everything; `async with` opens what must be closed.
- Always `await` a coroutine, and never call blocking functions inside async code.

With these ideas you can read the code in Chapter 11, where a lead agent uses `asyncio.gather` to run several research subagents in parallel and then combines what they find.

## Learn more

Free, trustworthy places to read more about this chapter's topics. Start with the **Start here** rows; **Go deeper** rows are for when you want more detail. Links were checked in September 2026; if one has moved, search for its title.

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Real Python: Async IO in Python**<br>[realpython.com/async-io-python](https://realpython.com/async-io-python/) | async, await and the event loop, with examples | Start here |
| **Python docs: asyncio**<br>[docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html) | The official reference, including gather and timeouts | Go deeper |
| **Claude docs: Python SDK**<br>[platform.claude.com/docs/en/cli-sdks-libraries/sdks/python](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) | Installing the SDK, and AsyncAnthropic for parallel calls | Go deeper |

## Exercises

Each exercise starts from a file with the functions in place. `./course.sh check A.1` (A.2 and so on) checks both the results and the timing.

:::ex Simple | A.1 | Measure it
Change `i_async.py` to fetch five things taking 1, 2, 1, 3 and 1 seconds. Predict the total time sequentially and with `gather`, then run it.
**Done when:** Your predictions (8 s and 3 s) match the measurements within a tenth of a second.
:::

:::ex Simple | A.2 | Find the bugs
This code has two async bugs. Find and fix them: `async def main(): r = fetch("x", 1); time.sleep(2); print(r)`.
**Done when:** You've fixed both and can explain what each bug would do.
:::

:::ex Medium | A.3 | Limit concurrency
Using `asyncio.Semaphore`, write `fetch_all(names, limit=3)`, which fetches 10 things concurrently but never more than three at a time. Print when each fetch starts and finishes.
**Hint:** Put `async with semaphore:` around the fetch.
**Done when:** The output shows at most three fetches in progress at any moment, and the total time matches your prediction.
:::

:::ex Medium | A.4 | Timeouts and partial results
Fetch five items, one of which takes 10 seconds. Give each fetch a 2-second timeout, and return the results that arrived plus a list of the items that timed out.
**Done when:** The program finishes in about 2 seconds with four results and one timeout.
:::
