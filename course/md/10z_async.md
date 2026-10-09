# Interlude: Asynchronous Python

Ask a model three questions one after another and you wait three times. Ask all three at once and you wait only as long as the slowest answer. Agents spend most of their time waiting, so that gap matters. This interlude teaches just enough async Python to read the agent code ahead and avoid its two classic bugs.

**Prerequisites:** The Python interlude (functions and decorators), Chapter 4 (agent loop).

## Learning objectives

By the end of this interlude you can:

- Explain why async code helps agents that mostly wait.
- Use `async def`, `await`, `asyncio.run` and `asyncio.gather`.
- Run blocking code with `asyncio.to_thread`, and set deadlines with `asyncio.wait_for`.
- Read the async code in Chapters 11, 13, 14 and 21, and avoid the two classic bugs.

## Why this interlude

Chapter 11 runs subagents at once, Chapters 13 and 14 talk to MCP servers, and Chapter 21 connects agents over the web. All that code is **asynchronous** (async). It looks odd at first, but five ideas cover it.

## A.1 Waiting without blocking

Normal Python waits for one thing at a time. Async code starts several waits and lets them overlap, all in one program.

@@code i_async.py::fetch,one_after_another,at_the_same_time,slow_blocking_call,with_blocking_code,with_a_timeout

Run it with `./course.sh python i_async.py`. Two one-second waits take two seconds in sequence and one second with `gather`.

@@image d-f6804fb92916.png

Figure: Two requests that overlap with `asyncio.gather`
Alt: Sequence diagram: your program sends a request to a weather API and one to a news API without waiting for the first; both reply after one second, so with gather the two waits overlap and take about one second in total.

## A.2 The five ideas

Table: The five async ideas
| Idea | Syntax | Meaning |
| --- | --- | --- |
| Coroutine | `async def f():` | A function that can pause while it waits |
| Await | `await f()` | "Run this; let other work happen while it waits" |
| Run | `asyncio.run(main())` | Start the async world, once, at the top |
| Gather | `await asyncio.gather(a(), b())` | Run several coroutines at once and collect the results |
| To thread | `await asyncio.to_thread(slow_func)` | Run blocking code without freezing the others |

Two more turn up later: `async with` opens something that must be closed (such as an MCP connection), and `asyncio.wait_for(x, timeout=5)` gives up after a deadline.

:::warn The two classic async bugs
**Forgetting `await`:** `result = fetch()` gives you a coroutine object instead of a result, and Python warns "coroutine was never awaited". **Blocking the loop:** calling `time.sleep()` or a slow normal function inside async code freezes everything, because all coroutines share one *event loop*, the scheduler that switches between them. Use `await asyncio.sleep()` or `asyncio.to_thread()` instead.
:::

:::warn Concurrency isn't durability
`asyncio.gather` overlaps waits inside one process. If the process dies, every coroutine dies with it, and nothing remembers what had finished, so async can't resume a job after a deploy or pause for a person's approval. It makes an agent *faster*. Chapter 19 makes it *survive*, with checkpoints, idempotency keys, leases and a durable execution platform such as Temporal.
:::

## A.3 Reading async agent code

When you see this in Chapter 11 or 13:

```
# open the connections, and close them at the end
async with MCPHub(config) as hub:
    # run the subagents in parallel
    findings = await asyncio.gather(*(run_subagent(t) for t in tasks))
```

Read it as: *connect to the servers, run all the subagents at once, wait for every one, then disconnect.* The `*` spreads a list of coroutines into separate arguments for `gather`.

## Key takeaways

- Async lets one program overlap many waits on the model, APIs and servers.
- `async def` defines, `await` waits, `asyncio.run` starts and `gather` runs things at once.
- Always `await` a coroutine, and move blocking code out with `to_thread`.

That's enough to read Chapter 11, where a lead agent sends research subagents off together with `asyncio.gather`. Running them in parallel turns out to be the easy part. The hard question is whether a team beats one agent at 15 times the tokens.

## Learn more

Start with these. `RESOURCES.md` in the course kit has all 3 links for this chapter, including the **Go deeper** reading, ready to click.

| Resource | What you'll find |
| --- | --- |
| **Real Python: Async IO in Python**<br>[realpython.com/async-io-python](https://realpython.com/async-io-python/) | async, await and the event loop, with examples |

## Exercises

Each exercise starts from a file with the functions in place. `./course.sh check A.1` (A.2 and so on) checks the results and the timing.

:::ex Simple | A.1 | Measure it
Change `i_async.py` to fetch five things taking 1, 2, 1, 3 and 1 seconds. Predict the total time sequentially and with `gather`, then run it.
**Done when:** Your predictions (8 s and 3 s) match the measurements within a tenth of a second.
:::

:::ex Simple | A.2 | Find the bugs
Find and fix the two async bugs in `async def main(): r = fetch("x", 1); time.sleep(2); print(r)`.
**Done when:** You've fixed both and can explain what each bug would do.
:::

:::ex Medium | A.3 | Limit concurrency
Using `asyncio.Semaphore`, write `fetch_all(names, limit=3)`, which fetches 10 things concurrently, never more than three at a time. Print when each fetch starts and finishes.
**Hint:** Put `async with semaphore:` around the fetch.
**Done when:** The output shows at most three fetches in progress at any moment, and the total time matches your prediction.
:::

:::ex Medium | A.4 | Timeouts and partial results
Fetch five items, one of which takes 10 seconds. Give each fetch a 2-second timeout, and return the results that arrived plus a list of those that timed out.
**Done when:** The program finishes in about 2 seconds with four results and one timeout.
:::
