# Solutions index

Try each exercise before you look. `./course.sh solution <id>` prints a solution; paths are relative to this `solutions` folder. Written answers are in `ANSWERS.md`.

## Chapter 0: Foundations

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 0.1 What happens when you press Enter? | `ANSWERS.md` | A command's journey: wrapper script, image, container, workspace volume, clean-up |
| 0.2 Read the schema | `ANSWERS.md` | Required fields, types and ranges; extra fields are allowed unless the schema forbids them |
| 0.3 Your shared workspace | `ANSWERS.md` | The workspace folder is shared both ways between your computer and the container |
| 0.4 Write three functions | `exercises/ex0_4_basics.py` | Three small functions |
| 0.5 Summarize a forecast | `exercises/ex0_5_forecast.py` | Summarize a forecast given as JSON text |
| 0.6 A careful API call | `exercises/ex0_6_city_temperature.py` | Two API calls in a row, with careful error handling |
| 0.7 Expense report tool | `exercises/ex0_7_expenses.py` | An expense report from a CSV file, robust to bad rows |

## Interlude: The Python You'll Need

| Exercise | Solution | What it shows |
| --- | --- | --- |
| P.1 Comprehensions | `exercises/exP_1_comprehensions.py` | Filtered lists and dictionaries in one line, and totals with dict.get |
| P.2 Call tools by name | `exercises/exP_2_run_tool.py` | Look a function up by name, call it with **args, and turn any failure into text |
| P.3 A class of your own | `exercises/exP_3_tasklist.py` | A class holding dataclass objects, with ids and no shared state |
| P.4 Decorators | `exercises/exP_4_decorators.py` | A decorator that registers a function, and one that wraps it (functools.wraps) |
| P.5 Find the bugs | `exercises/exP_5_bugs.py` | Mutable defaults, off-by-one ranges and swallowed errors |

## Chapter 1: What an Agent Is (and Isn't)

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 1.1 Single call, workflow or agent? | `ANSWERS.md` | Could you draw the flowchart in advance? Then it's a workflow, not an agent |
| 1.2 Tokens and cost | `ANSWERS.md` | Resending history makes total input grow quadratically with turns (47,500 tokens) |
| 1.3 Your first call | `exercises/ex1_3_eli10.py` | Your first call: compare two system prompts |
| 1.4 Make it fail | `ANSWERS.md` | Each failure maps to a missing tool: a clock, a calculator, a file reader |
| 1.5 Build the workflow | `exercises/ex1_5_workflow.py` | A fixed three-step workflow (NOT an agent) |
| 1.6 Remembering a conversation | `exercises/ex1_6_chat.py` | Remembering a conversation (and breaking it on purpose) |
| 1.7 Where does the agent go? | `ANSWERS.md` | Name the tools, the risks and the cost before choosing an agent |

## Interlude: Testing with pytest

| Exercise | Solution | What it shows |
| --- | --- | --- |
| T.1 Run and break | `ANSWERS.md` | A failing test names the broken function and shows the wrong value |
| T.2 Parametrize | `tests/test_exT_2_parametrize.py` | One parametrized test, many cases. Run with pytest -v |
| T.3 Test your Chapter 0 code | `tests/test_ex_t3.py` | Tests for exercise 0.4, edge cases included |
| T.4 Fake the network | `tests/test_exT_4_fake_network.py` | Test max_temperature with no internet, using monkeypatch |

## Chapter 2: Tool Calling

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 2.1 Who wrote this? | `ANSWERS.md` | Tool results are sent as role user; only the model writes assistant messages |
| 2.2 Attack the tool | `ANSWERS.md` | Never eval model input: the safe calculator rejects calls and attributes, but huge powers still need a cap |
| 2.3 Run and trace | `exercises/ex2_3_trace.py` | Print the raw tool_use block from the first model call |
| 2.4 Tune the description | `exercises/ex2_4_description_eval.py` | Measure whether the description makes the model call the tool |
| 2.5 Graceful errors | `exercises/sol_ch02_calculator_agent.py` | Return errors as tool results with is_error, so the model can recover |
| 2.6 A second tool, by hand | `exercises/ex2_6_two_tools.py`, `exercises/sol_ch02_calculator_agent.py` | Why the Chapter 2 `ask` breaks on multi-step questions |

## Chapter 3: Choosing Between Tools

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 3.1 Untangle the tools | `ANSWERS.md` | Merge overlapping tools and write descriptions that say when to use each |
| 3.2 Pick the tool_choice | `ANSWERS.md` | auto, any, a named tool or none: pick by how much freedom the model needs |
| 3.3 Add a tool | `exercises/sol_ch03_tools.py` | A new tool needs the function, the registry entry and a schema with an enum |
| 3.4 A 20-question eval | `exercises/ex3_4_routing_eval.py` | A 20-question routing eval, run 3 times |
| 3.5 Structured output, two ways | `exercises/ex3_5_forced_tool.py` | Structured output two ways, with no JSON parsing either way |
| 3.6 Scale to ten tools | `exercises/ex3_6_ten_tools.py` | Ten tools with near-duplicates, then fix by merging |
| 3.7 Tool search at scale | `exercises/ex3_7_tool_search.py`, `tests/test_2026_features.py` | Deferred tools found by search, against loading every tool: accuracy, searches and tokens |

## Chapter 4: The Agent Loop

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 4.1 Draw the loop | `ANSWERS.md` | Two tool round-trips, then an answer: every tool_use is followed by its tool_result |
| 4.2 Run the loop | `ANSWERS.md` | Multi-step questions show two or more tool calls in the trace |
| 4.3 Trigger the cap | `exercises/ex4_3_cap.py` | Trigger the iteration cap, and watch repeated errors |
| 4.4 A better tracer | `exercises/ex4_4_tracer.py` | A tracer that separates model time from tool time |
| 4.5 Cost profile | `exercises/ex4_5_cost_profile.py` | Cost profile of the agent across questions and runs |

## Chapter 5: State and Short-Term Memory

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 5.1 What survives a restart? | `ANSWERS.md` | Only what's written to disk survives; the conversation doesn't |
| 5.2 Idempotency audit | `ANSWERS.md` | Retrying a tool call must not duplicate or damage data |
| 5.3 Run the to-do agent | `ANSWERS.md` | State in tasks.json survives restarts; the chat history doesn't |
| 5.4 Add delete and edit | `exercises/sol_ch05_todo_tools.py` | Delete and rename tools that address tasks by id |
| 5.5 What's due this week? | `exercises/sol_ch05_todo_tools.py` | An overdue filter computed in code, not guessed by the model |
| 5.6 Clarify, don't guess | `ANSWERS.md` | When two items match, the agent asks instead of guessing |
| 5.7 Move to SQLite | `exercises/sol_ch05_todo_sqlite.py` | The same to-do tools on SQLite, plus a JSON migration |

## Interlude: Regular Expressions

| Exercise | Solution | What it shows |
| --- | --- | --- |
| R.1 Extract from logs | `exercises/exR_1_logs.py` | Pull fields out of a log with regular expressions |
| R.2 Mask secrets | `exercises/exR_2_mask.py` | Hide anything that looks like an API key |
| R.3 Parse citations | `exercises/exR_3_citations.py` | Find (file:line) citations in an answer |
| R.4 Error codes | `exercises/exR_4_error_codes.py`, `ANSWERS.md` | Match error codes exactly |

## Chapter 6: Exploring an Environment

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 6.1 Break the sandbox | `ANSWERS.md` | Path checks must resolve the real path; test ../, absolute paths and symlinks |
| 6.2 Ask your notes | `ANSWERS.md` | Answers cite (file:line), and unanswerable questions say so |
| 6.3 Prove the sandbox | `tests/test_ex6_3_sandbox.py` | Prove the notes sandbox holds |
| 6.4 Check the citations | `exercises/ex6_4_citation_checker.py` | Check that every (file:line) citation supports the answer |
| 6.5 Search by filename and date | `exercises/sol_ch06_notes_tools.py` | Find notes by file name and modification date |
| 6.6 Scale test | `exercises/ex6_6_scale_test.py` | Agentic search vs 'read everything' on 2,000 notes |

## Chapter 7: Real APIs

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 7.1 Failure table | `ANSWERS.md` | Every failure mode needs a planned response: retry, explain or stop |
| 7.2 Cache or not? | `ANSWERS.md` | Cache by how fast the data changes and how costly a stale answer is |
| 7.3 Pack for a trip | `ANSWERS.md` | The packing list must follow the forecast numbers in the trace |
| 7.4 Handle the hard cases | `exercises/ex7_4_hard_cases.py` | Unknown city, ambiguous city, and a simulated timeout |
| 7.5 Run tools in parallel | `exercises/ex7_5_parallel.py` | Run independent tool calls at the same time |
| 7.6 Multi-city trip with measurements | `exercises/ex7_6_trip_benchmark.py` | 3-city trip, 5 runs with cache on and 5 with cache off |

## Interlude: SQL in One Sitting

| Exercise | Solution | What it shows |
| --- | --- | --- |
| S.1 Warm-up queries | `exercises/exS_1_warmup.py` | Warm-up queries, each checked a second way |
| S.2 Spot the bug | `exercises/exS_2_fix_query.py`, `ANSWERS.md` | The broken revenue query, and the fix |
| S.3 Business questions | `exercises/exS_3_business.py` | Three business questions in SQL |
| S.4 Safe parameters | `exercises/exS_4_parameters.py`, `ANSWERS.md` | Parameters versus string-built SQL |

## Chapter 8: Self-Correction

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 8.1 Why not just the prompt? | `ANSWERS.md` | A read-only connection is enforced by the database; a prompt is only a request |
| 8.2 Define the terms | `ANSWERS.md` | Write definitions (revenue, active customer) the agent must follow |
| 8.3 Top customers | `ANSWERS.md` | Check the agent's numbers with your own SQL: Customer 13, 19,238 |
| 8.4 Watch it self-correct | `exercises/ex8_4_self_correct.py` | Sabotage the prompt and watch the agent self-correct |
| 8.5 Retry budget and log | `exercises/sol_ch08_sql_tools.py` | A retry budget and a query log for the SQL tool |
| 8.6 Confirm the tables | `exercises/sol_ch08_sql_tools.py` | Confirm the tables with the user before running an expensive query |
| 8.7 An evaluation harness | `exercises/ex8_7_eval_harness.py` | Compare the agent's answers with verified gold SQL |

## Chapter 9: Human in the Loop

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 9.1 Risk sorting | `ANSWERS.md` | Auto-approve reads and reversible steps, approve risky ones, forbid destructive ones |
| 9.2 Prompt injection by file name | `ANSWERS.md` | Even if the model is fooled, the approval gate in code still stops apply_plan |
| 9.3 Dry run | `ANSWERS.md` | Plan first; declining changes nothing |
| 9.4 Approve and undo | `ANSWERS.md` | Every applied plan can be undone from its log |
| 9.5 Partial approval | `exercises/sol_ch09_organizer.py` | Approve some moves and reject others in one plan |
| 9.6 Policy file and stress test | `exercises/sol_ch09_organizer.py`, `tests/test_ex9_6_policy.py` | A policy file that blocks risky moves, tested on 200 files |

## Chapter 10: Feedback Loops

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 10.1 Other signals | `ANSWERS.md` | Every task needs a checkable signal: a reference query, a schema, a measurement |
| 10.2 Gaming the signal | `ANSWERS.md` | Agents can game tests (special cases, skipped tests); defend in code |
| 10.3 Fix the bugs | `ANSWERS.md` | Run tests, read, make small edits, rerun until green; never touch the tests |
| 10.4 Watch the protection | `exercises/ex10_4_protection.py` | A permissive prompt vs the code rule that protects tests |
| 10.5 Four bugs, two files | `exercises/sol_ch10_make_repo2.py` | Add shipping.py with two more bugs (5 failing tests in total) |
| 10.6 Targeted edits | `exercises/sol_ch10_fixer.py` | Targeted replace_in_file edits instead of rewriting whole files |
| 10.7 Benchmark the fixer | `exercises/ex10_7_benchmark.py`, `exercises/sol_ch10_fixer.py` | Benchmark the fixer on 10 seeded bugs, tests in the sandbox |

## Interlude: Asynchronous Python

| Exercise | Solution | What it shows |
| --- | --- | --- |
| A.1 Measure it | `exercises/exA_1_measure.py`, `ANSWERS.md` | Predict, then measure, sequential vs gather |
| A.2 Find the bugs | `exercises/exA_2_fixed.py`, `ANSWERS.md` | Two async bugs, fixed |
| A.3 Limit concurrency | `exercises/exA_3_semaphore.py`, `ANSWERS.md` | Run many at once, but never more than `limit` |
| A.4 Timeouts and partial results | `exercises/exA_4_timeouts.py` | A timeout per call, keep what arrived |

## Chapter 11: Multi-Agent Systems

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 11.1 One agent or many? | `ANSWERS.md` | Use many agents only for broad, parallel, loosely coupled work |
| 11.2 Design the subtasks | `ANSWERS.md` | Each subtask needs an objective, boundaries, an output format and an effort level |
| 11.3 Run the team | `ANSWERS.md` | Plan, parallel findings, cited synthesis, plus time and tokens |
| 11.4 Better delegation | `exercises/sol_ch11_research_team.py` | Structured subtasks with an effort level that sets each subagent's step budget |
| 11.5 A critic agent | `exercises/sol_ch11_research_team.py` | A critic pass that checks the draft against the findings |
| 11.6 Is it worth it? | `exercises/ex11_6_compare.py` | Single agent vs research team, scored with a rubric |
| 11.7 Pick the pattern | `exercises/ex11_7_patterns.py`, `tests/test_multiagent.py` | Router, evaluator-optimizer, voting and handoff, each matched to a job, with its cost in model calls |

## Chapter 12: MCP Fundamentals and Your First Server

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 12.1 Map the architecture | `ANSWERS.md` | Host, client and server: who runs the model and who runs the tools |
| 12.2 Tool, resource or prompt? | `ANSWERS.md` | Tools act, resources are read, prompts are templates the user picks |
| 12.3 Run it in Inspector | `ANSWERS.md`, `tests/test_ex12_7_http.py` | Tools, a resource and a prompt, all visible in the Inspector |
| 12.4 Where does print() go? | `exercises/ex12_4_print_break.py` | Where does print() go in a Python stdio MCP server? |
| 12.5 Claude Desktop | `ANSWERS.md` | Claude Desktop runs your server through Docker and asks before each call |
| 12.6 A server of your own | `exercises/ex12_6_calc_server.py` | The Chapter 3 tools as an MCP server (+ resource + prompt) |
| 12.7 HTTP and tests | `tests/test_ex12_7_http.py`, `tests/fake_http/sitecustomize.py` | The same server over stdio and Streamable HTTP, tested both ways |

## Chapter 13: Build Your Own MCP Client

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 13.1 Collisions | `ANSWERS.md` | Namespace tools as server__tool so names never collide |
| 13.2 A client without a model | `exercises/ex13_2_client.py` | An MCP client with no model at all |
| 13.3 Two servers, one question | `ANSWERS.md` | One question, tools from two servers |
| 13.4 Resources at start-up | `exercises/sol_ch13_mcp_agent.py` | Read servers' resources at start-up and give them to the model |
| 13.5 Add the weather server | `exercises/servers_with_weather.json` | Add a server by configuration only, no host code changes |
| 13.6 Resilience | `exercises/sol_ch13_mcp_agent.py` | Restart a crashed server, reconnect and retry the call once |
| 13.7 Let the server ask the user | `exercises/ex13_7_trip_server.py`, `exercises/ex13_7_host.py`, `tests/test_ex13_7_elicit_sample.py` | A resolver asks the user mid-call (elicitation); the host shows the question and fills the answer |
| 13.8 A coordinator with an analyst | `exercises/ex13_8_coordinator.py`, `exercises/servers_with_analyst.json`, `tests/test_multiagent.py` | A coordinator hub that delegates data questions to an analyst agent served over MCP |

## Chapter 14: Using Servers You Didn't Write

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 14.1 Threat model | `ANSWERS.md` | A policy layer in code hides and blocks dangerous tools even if the model is convinced |
| 14.2 Server review | `ANSWERS.md` | Six questions: publisher, permissions, readable source, pinned version, narrowing, secrets passed |
| 14.3 Read-only GitHub | `ANSWERS.md`, `exercises/ex14_4_digest.py` | A read-only token and --read-only remove write tools entirely |
| 14.4 Weekly engineering digest | `exercises/ex14_4_digest.py` | Weekly engineering digest from Git + GitHub (read-only) |
| 14.5 Mark untrusted content | `exercises/sol_ch14_untrusted.py` | Wrap untrusted tool output before the model sees it |

## Chapter 15: MCP in 2026: From Tool Calling to Agent Infrastructure

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 15.1 Who asked for this? | `ANSWERS.md` | Each 2026-07-28 change matched to who benefits and the problem it removes |
| 15.2 Plan a migration | `ANSWERS.md` | Sampling, roots, logging and SSE replaced; per-user state moved to storage keyed by an id |
| 15.3 MCP by hand | `exercises/ex15_3_wire.py`, `tests/test_part5_mcp2026.py` | Discover, list and call over raw HTTP; a header that disagrees with the body is refused |
| 15.4 What does caching save? | `exercises/ex15_4_cache.py`, `tests/test_part5_mcp2026.py` | 1, 10 and 10 of 10 list requests reach the server |
| 15.5 Search what you may use | `exercises/ex15_5_scoped_search.py`, `tests/test_part5_mcp2026.py` | search_tools filtered by the caller's token scopes |
| 15.6 Fewer polls, safe retries | `exercises/ex15_6_jobs.py`, `tests/test_part5_mcp2026.py` | A long-polling job_status: one call instead of several; the same request_id gives the same job |
| 15.7 An agent behind the gateway | `exercises/ex15_7_gateway_agent.py`, `tests/test_part5_mcp2026.py` | The Chapter 13 agent behind a stdio gateway: tools found by search, writes allowed, the order query refused and audited |

## Chapter 16: Context Engineering

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 16.1 Where did the tokens go? | `ANSWERS.md` | Trim tool results first, cache the stable prefix second, compact last |
| 16.2 Design a system prompt | `ANSWERS.md` | Role, tool use, rules, output format and boundaries, each testable |
| 16.3 Watch compaction happen | `ANSWERS.md` | Watch trimming or compaction keep a conversation under budget |
| 16.4 Assemble a context | `ANSWERS.md` | The report explains every inclusion and drop; routing decides which sources are fetched |
| 16.5 Measure caching savings | `exercises/ex16_5_cache_savings.py` | Measure what prompt caching saves, from real usage fields |
| 16.6 Fresh or stale? | `exercises/sol_ch16_assemble.py`, `tests/test_ex16_6_fresh.py` | Newest item per origin, failed refreshes reported, max_age enforced, with unit tests |
| 16.7 Let a program do the counting | `exercises/ex16_7_programmatic_compare.py` | Many calls feeding one summary favor a program; step-by-step reasoning favors the plain loop |
| 16.8 Brief the research team | `exercises/ex16_8_briefed_team.py`, `tests/test_part6.py` | Workers get isolated briefs and answer in one call: fewer tokens, same citations |

## Chapter 17: Agent Memory Engineering

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 17.1 Sort the memories | `ANSWERS.md` | Each memory classified by kind, scope, lifetime and store, or not stored at all |
| 17.2 Write a memory policy | `ANSWERS.md` | A one-page memory policy whose rules can be enforced in code |
| 17.3 Remember across restarts | `ANSWERS.md` | Memory survives restarts in memory.db; forget really deletes |
| 17.4 Watch the policy work | `ANSWERS.md` | Every output line explained: stored, replaced, refused, quarantined, expired or recalled |
| 17.5 Consolidate episodes | `exercises/ex17_5_consolidate.py`, `tests/test_part6.py` | Episodes about one topic become one semantic memory that records its sources |
| 17.6 Poison the memory | `exercises/ex17_6_poison.py`, `tests/test_part6.py` | Five poisoning attempts, all quarantined by layered defenses |
| 17.7 A team memory | `exercises/ex17_7_team_memory.py`, `tests/test_part6.py` | Only the lead writes team memory; workers read it and keep private notes |
| 17.8 A memory-backed assistant | `exercises/ex17_8_assistant.py` | A to-do assistant with policy-governed memory and a budget |

## Chapter 18: Agentic Knowledge Systems

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 18.1 Choose the chunk size | `ANSWERS.md` | Chunk size follows the document type; overlap protects boundaries |
| 18.2 Keyword, vector or hybrid? | `ANSWERS.md` | Keyword for exact codes, vectors for meaning, hybrid for both |
| 18.3 Build and search | `ANSWERS.md` | Keyword and vector search disagree; see where and why |
| 18.4 Change the embedder | `ANSWERS.md` | Recall@3 and MRR for each embedder and search mode |
| 18.5 Paraphrased evaluation | `exercises/ex18_5_paraphrased.py` | Questions that share almost no words with their answers. Keyword search struggles here; a semantic embedder (EMBEDDER=local or voyage) should not |
| 18.6 A cited knowledge agent | `exercises/ex18_6_knowledge_agent.py` | A cited knowledge agent, evaluated on accuracy, citation validity and honest refusals |
| 18.7 A new source | `exercises/ex18_7_weather_source.py`, `tests/test_part6.py` | A weather source the planner uses only for forecasts |
| 18.8 Know when to stop | `exercises/ex18_8_know_when_to_stop.py` | Answerable and unanswerable questions scored for one and two search rounds |
| 18.9 Answers you can check | `exercises/ex18_9_verified.py`, `tests/test_part6.py` | Quotations and wrong-source citations caught, then one revision round |

## Chapter 19: Long-Running Agents

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 19.1 Which mechanism? | `ANSWERS.md` | Each failure matched to checkpoints, retries, keys, leases, escalation, compensation or checks in code |
| 19.2 Idempotent or not? | `ANSWERS.md` | Setting a value is idempotent; adding, sending and moving money need a key or a design change |
| 19.3 Crash and resume | `ANSWERS.md` | A resumed job skips finished steps and reuses their results; deleting the checkpoint repeats everything |
| 19.4 Two workers | `exercises/ex19_4_workers.py`, `tests/test_part7.py` | Two workers share a queue of jobs. One dies holding a job; when its lease runs out, the other worker claims the job and finishes it |
| 19.5 A cost budget per job | `exercises/ex19_5_budget.py`, `tests/test_part7.py` | A cost budget per job. The agent action records what each model call cost; a job that would go over its budget waits for a person |
| 19.6 A report that finishes itself | `exercises/ex19_6_report_loop.py`, `tests/test_part7.py` | Run harness sessions until the report is finished, one item needs a person, or the session limit is reached. A crash between sessions loses nothing, and a final check recomputes the cancellation share with our own SQL |

## Chapter 20: Planning and Model Routing

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 20.1 Plan or not? | `ANSWERS.md` | Plan when the task is long, predictable in shape or costly to get wrong; approve plans for risky bulk work |
| 20.2 Route the steps | `ANSWERS.md` | Small models for lookups and formatting, the large model with more effort for the judgement step |
| 20.3 Break the plan | `exercises/ex20_3_bad_plans.py`, `tests/test_part7.py` | Plans that check_plan must reject, and one it accepts. No model is called: checking a plan is ordinary code |
| 20.4 Run independent steps in parallel | `exercises/ex20_4_parallel_plan.py`, `tests/test_part7.py` | Run every step whose dependencies are finished at the same time. TopologicalSorter hands out "ready" steps; threads run them; done() unlocks more |
| 20.5 Evaluate the routers | `exercises/ex20_5_router_eval.py`, `tests/test_part7.py` | Score two routers against labels you wrote yourself |
| 20.6 A plan that survives a crash | `exercises/ex20_6_durable_plan.py`, `tests/test_part7.py` | A checked plan becomes a Chapter 19 durable job. Each plan step is a "plan_step" action whose brief gets earlier results through "$n" references, and each step's model is chosen by the rules router |

## Chapter 21: Multi-Agent Orchestration

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 21.1 Pick the topology | `ANSWERS.md` | Supervisor for most systems; pipelines for fixed sequences; A2A networks across companies; a board for many loosely coupled agents |
| 21.2 Write the contracts | `ANSWERS.md` | A result schema with required sources and dates, numeric prices and a maximum size; a brief with objective, scope and answer form |
| 21.3 Watch the board | `ANSWERS.md` | Every board row explained; refused delegations reach the lead as errors it must handle |
| 21.4 A specialist that fails | `exercises/ex21_4_failures.py`, `tests/test_part7.py` | A specialist that fails in three ways, each contained as an ERROR result for the lead, plus one more chance after a contract violation |
| 21.5 A team of A2A agents | `exercises/ex21_5_a2a_team.py`, `tests/test_a2a.py` | Two agents published with A2A (analyst and to-do keeper), found by their cards and used by one coordinator |
| 21.6 A mixed team | `exercises/ex21_6_mixed_team.py`, `tests/test_a2a.py` | A team with a remote member. The A2A analyst runs in this process on its own port; the lead delegates to it and to the local analyst, compares the answers, and sends a disagreement to the checker |

## Chapter 22: Hybrid Architectures: Probabilistic Intelligence, Deterministic Control

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 22.1 Model or code? | `ANSWERS.md` | Judgement on text goes to the model with an evaluation; limits, currency and approvals go to code |
| 22.2 Find the holes | `ANSWERS.md` | Amounts and ids from the model, identity in arguments, prompt-only limits: each fixed by a control in code |
| 22.3 Follow the five paths | `ANSWERS.md` | Five requests, five paths; the amount always comes from the order record |
| 22.4 Change the policy, not the code | `exercises/ex22_4_policy_json.py`, `tests/test_part7.py` | The refund policy as a versioned JSON file, with a new rule added as data. The decision stays pure code; every case records the policy version |
| 22.5 Attack the workflow | `exercises/ex22_5_attacks.py`, `tests/test_part7.py` | Six attacks on the refund workflow, and the invariants that must hold whatever the model does. Run it with a real model, or (in the tests) with a scripted model that does exactly what each attacker asks |
| 22.6 A guarded SQL analyst | `exercises/ex22_6_guarded_sql.py`, `tests/test_part7.py` | The Chapter 8 analyst as a hybrid. The model writes SQL; SQLite's authorizer, not the prompt, decides what that SQL may do. Business definitions come from a file your team maintains |

## Chapter 23: Computer-Use Agents

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 23.1 Screen or API? | `ANSWERS.md` | APIs and exports first; a browser or desktop agent only where nothing else exists |
| 23.2 Threat-model the browser agent | `ANSWERS.md` | Harms from page content and from mistakes, each with a control that holds even if the model is fooled |
| 23.3 Drive it by hand | `exercises/ex23_3_by_hand.py`, `tests/test_part7.py` | Drive the browser harness by hand, with no model. The same calls the agent makes, so you can see what each one returns |
| 23.4 The injected note | `exercises/ex23_4_injection.py`, `tests/test_part7.py` | The agent updates Ben's address while his customer notes try to get a $500 credit and an email change. The harness, not the model, stops it |
| 23.5 Verify, don't trust | `exercises/ex23_5_verified_queue.py`, `tests/test_part7.py` | A queue of address changes, each verified in code by reading the page directly, not by trusting the agent's final answer |
| 23.6 A queue that survives a crash | `exercises/ex23_6_durable_queue.py`, `tests/test_part7.py` | The browser queue as a Chapter 19 durable job. Each request is a step; address changes are run by the agent and verified in code; credits wait for a person. A crash loses nothing: finished requests stay finished |

## Chapter 24: Skills, Frameworks and Agent Runtimes

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 24.1 Map the features | `ANSWERS.md` | Every hand-built part has a framework equivalent |
| 24.2 Pick a framework | `ANSWERS.md` | Choose by need: minimal loop, full runtime, portability or teaching |
| 24.3 See the approval gate work | `ANSWERS.md` | A DELETE is denied by can_use_tool and the database is unchanged |
| 24.4 Agent SDK with your MCP servers | `exercises/ex24_4_sdk_mcp.py` | The Agent SDK with an in-process server AND a stdio server |
| 24.5 Same agent, three frameworks | `exercises/ex24_5_three_ways.py` | The Chapter 8 SQL analyst built four ways, one eval suite |
| 24.6 Write a skill | `exercises/ex24_6_skills.py`, `exercises/skills/customer-lookup/SKILL.md` | A second skill with a reference file, validated, and a trace showing only the needed skill loads |
| 24.7 A managed analyst | `exercises/ex24_7_managed.py` | A managed session to completion, and one stopped by a tiny budget |
| 24.8 Does the skill help? | `exercises/ex24_8_skill_eval.py`, `tests/test_part7.py` | Does the sql-report skill help? Run each request with and without the skill and check the answer's shape in code |
| 24.9 Choose a runtime | `ANSWERS.md` | The runtime follows from where state must live, how long work runs, and who operates the infrastructure |

## Chapter 25: Agentic Security

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 25.1 Find the trifecta | `ANSWERS.md` | Each agent's three legs identified; one removed in code or configuration |
| 25.2 Map your agent to OWASP | `ANSWERS.md` | Each OWASP agentic risk, how it could happen here, the defense in place and the gap to close first |
| 25.3 Trip the canary | `ANSWERS.md` | The canary and egress guards block the fetch; sanitizing removes the image channel |
| 25.4 Quarantine a second source | `exercises/ex25_4_calendar.py`, `tests/test_part8.py` | Calendar invites as a second untrusted source. Only metadata reaches the planner; descriptions go through the quarantined reader |
| 25.5 Evade the guard, then fix it | `exercises/ex25_5_evasion.py`, `tests/test_part8.py` | Five ways to sneak the canary past the leak scan, and a scan that normalizes before it searches |
| 25.6 Red team your agent | `exercises/ex25_6_redteam.py` | Red-team the agent with 6 planted attacks x 3 defenses |

## Chapter 26: Agent Identity and Authorization

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 26.1 Whose permission? | `ANSWERS.md` | Three identities per action, minimal scopes, step-up for money and sensitive data |
| 26.2 Design the token | `ANSWERS.md` | A token for one trip: one employee, one audience, capped amount and dates, a short life |
| 26.3 Break the token | `exercises/ex26_3_break_token.py`, `tests/test_part8.py` | Five ways to misuse a token, and one way to over-ask |
| 26.4 Tokens for a team | `exercises/ex26_4_team_tokens.py`, `tests/test_part8.py` | The Chapter 21 team with tokens. The lead's token is attenuated for each specialist: fewer scopes, a shorter life, a record of where it came from. Tools check the token; agents never see it |
| 26.5 An audit circuit breaker | `exercises/ex26_5_breaker.py`, `tests/test_part8.py` | An audit circuit breaker. A burst of denials, or any attempt on another user's resource, disables the agent at once |
| 26.6 A token-checked API | `exercises/ex26_6_orders_api.py`, `tests/test_part8.py` | The order tools as an HTTP API that checks bearer tokens. The harness holds the token, renews it when it expires, and the model never sees it |

## Chapter 27: Agent Evaluation: Trajectories and Continuous Evaluation

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 27.1 Design an eval | `ANSWERS.md` | Cases with deterministic checks, grown from real failures |
| 27.2 Read the numbers | `ANSWERS.md` | Flat throughput plus 429s means a rate limit; p95 far above p50 means queueing |
| 27.3 Run the SQL suite | `exercises/eval_sql_more.jsonl` | Six more SQL cases, each with a check that can fail |
| 27.4 Eval in CI | `exercises/ex27_4_ci_gate.py` | Fail the build when eval quality drops |
| 27.5 Calibrate a judge | `exercises/ex27_5_calibrate.py` | Check the judge against people before trusting it |
| 27.6 Grade the path | `exercises/ex27_6_trajectory.py`, `exercises/ex27_6_trajectory.jsonl`, `tests/test_part9.py` | Grade six cases on outcome, process and cost, three times |
| 27.7 Evaluate in production | `exercises/ex27_7_online.py`, `tests/test_part9.py` | A simulated week of production. Sample flagged runs and 10% of the rest each day, grade the sample, and check the daily rates for drift |

## Chapter 28: AgentOps: Observability for Agents

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 28.1 A trace viewer | `exercises/ex28_1_trace_report.py` | A report over the last 50 runs in traces.jsonl |
| 28.2 What would you trace? | `ANSWERS.md` | A span per state transition, redacted text, and an SLO on the reply-guard fallback rate |
| 28.3 Read the report | `ANSWERS.md` | Every report number explained; a failing tool shows up as a failure class and a named alert |
| 28.4 A new failure class | `exercises/ex28_4_ignored_error.py`, `tests/test_part9.py` | A failure class for runs that finished after a tool error that was never followed by a successful call of the same tool |
| 28.5 An SLO dashboard with burn alerts | `exercises/ex28_5_burn.py`, `tests/test_part9.py` | Hourly SLO reports and an error-budget burn alert: more than 10% failures (for a 90% objective) in two consecutive hours |

## Chapter 29: Agentic Performance and Cost Engineering

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 29.1 See queueing | `exercises/ex29_1_queueing.py` | See queueing, and see how the wrong clock hides it |
| 29.2 Load test a real agent | `exercises/ex29_2_real_loadtest.py` | Load-test the Chapter 13 MCP agent with real questions |
| 29.3 Where does the money go? | `ANSWERS.md` | History and the repeated prefix dominate; caching saves about 30%, routing plus caching about 46% |
| 29.4 Budgets that hold | `exercises/ex29_4_budgets.py`, `tests/test_part9.py` | A per-request and a per-user daily budget around the Chapter 8 analyst, both enforced in code |
| 29.5 Halve the cost | `exercises/ex29_5_cost_cut.py`, `tests/test_part9.py` | Cost per successful task before and after two levers: routing easy cases to the small model, and caching the stable prefix |

## Chapter 30: Deploying Agents as Services

| Exercise | Solution | What it shows |
| --- | --- | --- |
| 30.1 Pick the status code | `ANSWERS.md` | 401, 429, 422, 404, 502 and 409, and why each one |
| 30.2 Call your agent API | `ANSWERS.md` | Sessions carry context between requests; streaming shows progress |
| 30.3 Hit the limits | `ANSWERS.md` | Per-key rate limits give 429 with Retry-After; bad keys give 401 |
| 30.4 Stream the words | `exercises/sol_ch30_service.py` | Stream every model call and forward text as it arrives |
| 30.5 Remote MCP with your agent | `exercises/ex30_5_remote_hub.py`, `exercises/servers_remote.json` | The Chapter 13 hub, now able to reach REMOTE MCP servers |
| 30.6 Production drill | `exercises/ex30_6_drill.py` | Load-test the agent API over HTTP |
| 30.7 Ship it | `exercises/ex30_7_deploy.sh` | Build, run and smoke-test the production image, then deploy with secrets and limits |
