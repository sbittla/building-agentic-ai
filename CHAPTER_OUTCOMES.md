# Chapter outcomes

What you should be able to do after each chapter, and how you'd know. Each outcome is tied to an exercise or a section. The book prints each chapter's learning objectives at its start and its key takeaways at its end; this file is the self-check that goes with them.

## Chapter 0: Foundations

- Run `./course.sh python hello.py`, then create a file inside `./course.sh shell` and find it on your computer: a file has traveled both ways (exercise 0.3).
- Classify the five inputs in exercise 0.2 against the `schema` in `ch00_json.py`, naming for each the field or rule that decides it.
- Run `./course.sh check --api` and get a ✔ on the API call line; for any ✘, name the fix from section 0.5 without looking it up.
- Given a 401, a 429 and a 503, say for each whether to fix the request, wait and retry, or retry later (section 0.4).
- Make `./course.sh check 0.5` and `./course.sh check 0.6` pass, with `"not json"` and `"Xyzzyqq"` returning readable errors instead of a traceback.
- Search your code for your API key and find it nowhere; it lives only in `.env`, which `.gitignore` already excludes.

## Chapter 1: What an Agent Is (and Isn't)

- Run `ch01_summarize.py` and read off the input tokens, output tokens and `stop_reason`; say what you'd change if it ended with `max_tokens` (exercise 1.3).
- Run `ch01_where_llms_fail.py` and fill the three-row table of exercise 1.4, each row naming the tool that would fix the failure.
- Classify the six scenarios in exercise 1.1 as single call, workflow or agent, each justified by whether you could draw the flowchart in advance.
- Show the chat loop from exercise 1.6 both ways: with the full `messages` list the model knows your name on turn 3; with only the latest message it doesn't.
- Score a system from 0 to 3 on the nine dimensions of agency in section 1.4 and name the dimension you'd turn down first if it misbehaved (exercise 1.8).
- Write the design note of exercise 1.7 with at least four named tools, their risks and a per-email cost for the workflow against a four-call agent.

## Chapter 2: Tool Calling (Function Calling)

- Run `ch02_first_tool.py` and point to the `tool_use` stop reason, the `get_today` call and the matching `tool_use_id` in the `tool_result`.
- Label the four messages in exercise 2.1 by author and `role`, and explain why the tool result is sent with `role: "user"`.
- Pass `calculate` an input that `eval` would run and show it raises `ValueError`; then cap exponents so `10 ** 10 ** 10` returns an error instead of hanging (exercise 2.2).
- Log tool calls for the 10 questions of exercise 2.4 and rewrite the description until the model calls the tool on all seven arithmetic questions and none of the other three.
- Make "What is 5 divided by zero?" and "Compute `2 +* 3`" end in a helpful answer, not a crash, with a passing unit test for each (exercise 2.5).
- Explain, from a run of exercise 2.6, what happens in `ask` when the second response is also a `tool_use`.

## Chapter 3: Tool Selection, Routing and Tool Search

- Add `get_current_time` to both `REGISTRY` and `TOOLS` so "What time is it in Tokyo?" calls it with `Asia/Tokyo` and `./course.sh check 3.3` passes.
- Call `run_tool` with an unknown tool name and with mismatched units, and show both come back as `ERROR` text that says what is allowed, not as an exception (sections 3.1 and 3.5).
- Run your 20-question `ch03_routing_eval.py` three times and report average accuracy, listing every question whose result flips between runs (exercise 3.4).
- Extract contacts from five signatures with `messages.parse(output_format=Contact)` and get a valid `Contact` for each, including the one with no email (exercise 3.5).
- Add near-duplicate tools, then recover routing accuracy by rewriting descriptions or merging tools, shown in a before/after table (exercise 3.6).
- Run the 10 questions of exercise 3.7 with and without `defer_loading` in `ch03_tool_search.py`, and compare accuracy and input tokens in one table.

## Chapter 4: The Agent Loop

- Run `ch04_agent.py` on the July 4 question and, from the trace alone, name each tool the model called, in order, and the `stop_reason` that ended the run.
- Set `max_iterations=1`, then add the `always_fails` tool (exercise 4.3); show the cap message and describe from the trace how the model reacted to repeated errors.
- Ask "Convert 10 miles to km and 5 kg to lb" and point to the one response with two `tool_use` blocks and the one user message that returns both results (section 4.3).
- Given a `stop_reason` of `max_tokens`, `refusal` or `pause_turn`, say what `next_action` does with it without looking at section 4.4.
- Print per-step tokens and separate model and tool times with `exercises/ex4_4_tracer.py` (exercise 4.4), then state with numbers from exercise 4.5 how input tokens grow with step number.
- Write a system prompt with all five parts from section 4.10, and show a question that was answered from a guess now triggers a `get_current_date` call in the trace.

## Chapter 5: State and Short-Term Memory

- Add three tasks with `ch05_todo_tools.py`, quit, restart and list them: the same IDs and titles come back (exercise 5.3).
- For the Asha scenario in exercise 5.1, say which fact the agent gets from `tasks.json` and which was lost with the message history.
- Call `add_task` twice with the same title and `complete_task` twice with the same ID, and show the replies "Already exists" and "already done" with no duplicate in `tasks.json`.
- Classify the six operations in exercise 5.2 as idempotent or not, with a concrete fix for each one that isn't.
- With "Buy milk" and "Buy oat milk" on the list, produce a transcript where "complete the milk task" gets a question back and "the oat one" completes the right ID (exercise 5.6).
- Make "What's due this week?" call `today` and pass the right `due_before`, checked against test data with past, current and future dates (exercise 5.5).

## Chapter 6: Agentic Search: Exploring an Environment

- Ask five questions of your `workspace/notes`; open every cited `(file:line)` and confirm it holds the fact, and confirm the unanswerable question gets "not covered", not a guess (exercise 6.2).
- Make the three unit tests of exercise 6.3 pass: `run_tool("read_file", ...)` returns `ERROR` for every escaping path, including an absolute one.
- For each of your five paths in exercise 6.1, say whether `_safe` blocks it and why an `if ".." in path` check would not, including a symlink case.
- Read a file longer than 80 lines with `read_file` and point to the part of the result that tells the model how to get the next page (section 6.4).
- Corrupt one citation in an answer on purpose and show your checker from exercise 6.4 flags it.
- Choose agentic search, RAG or both for a given corpus using the rows of the table in section 6.6, and back it with your accuracy, token and time numbers from exercise 6.6.

## Chapter 7: Real APIs

- Run `ch07_weather_tools.py` for three cities and match each item on the packing list to a forecast value in the trace (exercise 7.3).
- Show the three hard cases of exercise 7.4: "Xyzzyqq" gets a spelling message, "Portland" gets a question, and the simulated timeout shows retries in the trace before an `ERROR:` result.
- Given a timeout, a 429, a 503, a 400 and an empty result, say for each whether `_get_json` retries and what the model receives (section 7.3).
- Ask the same city question twice in one run and show `stats` counting a cache hit instead of a second HTTP call (section 7.5).
- Time a two-city question with and without the `ThreadPoolExecutor` change of exercise 7.5 and show the parallel version is faster, with results still in the original order.
- Report wall time, HTTP calls and cache hits for five runs with caching on and five with it off, under a `MAX_HTTP_CALLS` budget (exercise 7.6).

## Chapter 8: Self-Correction: A Text-to-SQL Agent

- Ask for the top five customers by revenue and match the agent's numbers to the check query in exercise 8.3 (Customer 13 at 19,238).
- Run `run_query("WITH x AS (SELECT 1) DELETE FROM orders")` and name the layer from section 8.3 that let it through and the one that stopped it.
- Break a table name in `SYSTEM` (exercise 8.4) and point, in the trace, to the failing query, the exact error text and the corrected query.
- Produce a `query_log.jsonl` that shows at least one self-correction, plus the budget message after three forced failures (exercise 8.5).
- Send `SELECT * FROM orders` through `run_query` and show the result stops at 50 rows with a note telling the model to add LIMIT or aggregate (section 8.5).
- Report the agent's accuracy on your 15 gold questions before and after one change, with every failure labeled by type (exercise 8.7).

## Chapter 9: Human-in-the-Loop Approval

- Sort the eight actions in exercise 9.1 into auto-approve, needs approval or never allowed, each with a reason based on reversibility and impact.
- Ask for a plan on the `messy` folder, decline it, and show a directory listing identical to the one before (exercise 9.3).
- Approve a plan, then undo it, and show matching before and after listings; use `audit_log.jsonl` to explain each move that was reversed (exercise 9.4).
- Point to the line in `run_tool` that stops the injection-named file of exercise 9.2, and explain why a rule in the prompt would not.
- Make the user's reply "1,3,5-8" move exactly those files and log only those moves (exercise 9.5).
- Run the 200-file test of exercise 9.6 so a script shows the policy, gate, collision handling and undo all working, with file hashes matching after undo.

## Chapter 10: Feedback Loops

- Run `ch10_fixer.py` on a fresh `buggy_repo`, get all three tests passing, and explain each changed line in the final diff (exercise 10.3).
- Show `write_file` refusing both a test file and `conftest.py` (exercise 10.4), and explain why `writable()` is an allow-list rather than a block list (section 10.4).
- Make a run stop before it finishes (exercise 10.5) and name which `should_stop` condition fired, with a diff of the partial progress.
- Start `./course.sh sandbox up`, swap `run_tests` for `run_tests_sandboxed` in `REGISTRY`, and get the fixer to pass with tests running in the sandbox.
- Fix the bugs with `replace_in_file` and report the token difference against the whole-file `write_file` (exercise 10.6).
- Name three ways to make the tests pass without fixing the bug and a defense for each, one going beyond blocking test edits (exercise 10.2).

## Chapter 11: Multi-Agent Systems

- Run `ch11_research_team.py` on a question of your own and point, in its output, to the `make_plan` sub-questions, each subagent's cited findings, the final answer and the timing and usage line (exercise 11.3).
- Change `make_plan` so each subtask has `objective`, `out_of_scope` and `effort`, and show in the trace that `quick` subtasks run fewer iterations than `deep` ones (exercise 11.4).
- Add a critic stage, plant an unsupported claim, and show the critic lists it and the lead's revised answer removes or sources it (exercise 11.5).
- Answer five questions with the Chapter 6 agent and with the research team, and produce a table of rubric scores, latency and total tokens that backs a clear recommendation (exercise 11.6).
- For each of the four jobs in exercise 11.7, pick one of the five patterns from section 11.6, run it with the functions in `ch11_patterns.py`, and state its cost in model calls.
- Review the research team against the four rules in section 11.7 and, for each rule, name the line of code that enforces it or the gap where nothing does.

## Chapter 12: MCP Fundamentals and Your First Server

- Start `ch12_weather_server.py` with `./course.sh inspector` and show all three primitives working: both tools, the `weather://favorites` resource and the `packing_advice` prompt, plus an error result for "Xyzzyqq" (exercise 12.3).
- Add `print("hello")` to `geocode`, find the line in the server's stderr rather than the tool result, and name which SDKs would have corrupted the stdio stream instead (exercise 12.4).
- Generate a config with `./course.sh desktop-config` and show a Claude Desktop conversation where you approve calls to your tools and Claude uses the favorites resource (exercise 12.5).
- Build a second server from the Chapter 3 tools with one resource and one prompt, and show it listed in Inspector and working in Claude Desktop beside the weather server (exercise 12.6).
- Serve the weather server with `./course.sh serve` and pass pytest tests for tool listing, a successful call and an error call that give the same results over Streamable HTTP and stdio (exercise 12.7).
- Classify the five items in exercise 12.2 as tool, resource or prompt, and justify each by who decides to use it (section 12.3).

## Chapter 13: Build Your Own MCP Client

- Write a client of about 20 lines that lists the to-do server's tools and calls `add_task` and `list_tasks`, and show it prints the new task with no model involved (exercise 13.2).
- Run `python ch13_mcp_agent.py servers.json` on a question that needs both servers, and show `todo__` and `shopdb__` tool calls in the trace for one answer (exercise 13.3).
- Add the Chapter 12 weather server to `servers.json` without touching host code, and show the umbrella question uses `weather__` and `todo__` tools together (exercise 13.5).
- Load every server's resources into the system prompt at start-up within 4,000 characters, and show the SQL agent applies the revenue definition from `shopdb://definitions` without being told (exercise 13.4).
- Register `ch13_agent_server.py` as `analyst` and show a trace with one `analyst__ask_sql_analyst` call and three `todo__add_task` calls, with tokens attributed to each agent (exercise 13.8).
- Build the `trips` server with elicitation and show that booking asks for nights and budget, declining books nothing and no value is ever invented (exercise 13.7).

## Chapter 14: Using Servers You Didn't Write

- Run your host with `servers_ecosystem.json`, ask the Filesystem server for a path outside `./notes`, and show the `Access denied` refusal it returns (section 14.2).
- Connect GitHub's server with `--read-only` and a read-scope token, summarize open issues accurately, and show "close issue 3" fails because the tool doesn't exist (exercise 14.3).
- Run `ch14_policy_agent.py` with `policy.json` and show three things: a hidden tool missing from the model's tool list, an approval prompt with the full escaped arguments, and every decision recorded in `tool_calls.jsonl` (section 14.5).
- Produce the weekly engineering digest from the Git, GitHub and Time servers, check it against the repository, and show from the audit log that only read tools ran (exercise 14.4).
- Add an `after_call` hook that wraps `fetch`, `github` and `fs` output in `<untrusted_content>` tags, plant an injection in a note, and show the agent reports it instead of following it (exercise 14.5).
- Review one MCP Registry server against the six questions in section 14.3 and give a yes or no for installing it at work, with the question that decided it (exercise 14.2).

## Chapter 15: MCP in 2026: From Tool Calling to Agent Infrastructure

- Run `./course.sh python ch15_modern.py` and explain every line of its output, including why two list calls produced only one request to the server (section 15.3).
- With the server started by `./course.sh serve ch15_modern.py`, use `post` to send `server/discover`, `tools/list` and a `tools/call` for `get_price`, and point to the protocol version, the cache hints and `structuredContent` in the answers (exercise 15.3).
- Send a request whose `Mcp-Name` header names a different tool from its body, show it's refused, and explain which gateway bypass that refusal prevents (section 15.2).
- Send a request without the `_meta` envelope, show the error, and explain why a complete request lets any copy of the server answer it (section 15.2).
- Using `CountingServer`, report how many list requests reach the server over ten turns with the five-minute hint, with the cache bypassed and with the hint set to zero (exercise 15.4).
- Write the migration plan in exercise 15.2 so each deprecated feature maps to its replacement from section 15.4 and the in-memory search results get a new home, with a ship-first item named.

## Chapter 16: Context Engineering

- Run `ch16_assemble.py` at budgets of 120, 300 and 800 tokens and explain every line of each report; then add a `catalog` source and show a product question routes to `product` and includes it (exercise 16.4).
- Extend `assemble` and pass unit tests showing a duplicate order status resolved to the newer item, a failed `refresh` reported as dropped, and `max_age` enforced (exercise 16.6).
- Run `ch16_context.py` with `budget_tokens=3000`, print the context size before each call, and show a trim or compaction happening while the third answer still uses facts from the first (exercise 16.3).
- Measure one five-question session with caching `off`, `prefix` and `auto` from the `cache_creation_input_tokens` and `cache_read_input_tokens` fields, and explain from the table why `auto` wins (exercise 16.5, section 16.7).
- Give the Chapter 11 research workers an `isolated_brief` of at most 600 tokens, and report input tokens, a 1–5 quality score and citation counts for the original and isolated teams (exercise 16.8).
- Rewrite the weak system prompt in exercise 16.2 with the five parts from section 16.10, and show each rule is specific enough to write a test for.

## Chapter 17: Agent Memory Engineering

- Run `ch17_memory.py`, tell it two facts, restart it, then ask it to forget one, and show it recalls both facts after the restart and only one after the forget (exercise 17.3).
- Run `ch17_memory_policy.py` and say why each memory was stored, superseded, refused, quarantined, expired or recalled; then change `HALF_LIFE` and `TTL["episodic"]` and predict the differences before you rerun it (exercise 17.4).
- Write five tool results that try to plant a memory and a test that shows none of them active, and name one attack the write gate alone wouldn't catch (exercise 17.6, section 17.8).
- Give the research team a shared `team` scope and pass a test where a worker's write to it is refused, the lead's is accepted and every worker recalls the lead's finding (exercise 17.7, section 17.7).
- Run `ch17_memory_security.py` and explain from its output why Ana's "invoices" recall skips three memories, why Bo's deletion survives rollback, and why the audit text holds no memory content (section 17.10).
- Write `revert_batch` and pass the test in exercise 17.9: both good memories recalled, none of the bad batch, `state_at` never restoring it and `verify_audit` still passing.

## Chapter 18: Agentic RAG and Knowledge Systems

- Run `ch18_rag.py`, search three questions of your own in each mode, and show one query where keyword and vector results disagree, with the reason (exercise 18.3).
- Rebuild the index with `EMBEDDER=hashing` and `EMBEDDER=local` and produce a table of recall@3 and MRR for both embedders across all three modes (exercise 18.4).
- Add eight paraphrased questions to `EVAL` and show, with numbers, where vector or hybrid search beats keyword search, noting how much one question moves the result (exercise 18.5, section 18.6).
- Run `ch18_agentic.py` on the Kafka-and-orders question and show that `plan_needs` routes one need to `knowledge` and one to `shop_db`, and the answer cites a file and line and the SQL that produced the number (section 18.9).
- Run `answer` on four answerable and four unanswerable questions with `max_rounds` set to 1 and to 2, and tabulate correct answers, correct abstentions and wrong answers for each setting (exercise 18.8).
- Extend `verify` to catch misquotes and citations to the wrong source, with a test for each, and report how many of 10 answers pass before and after one revision (exercise 18.9).

## Chapter 19: Long-Running Agents

- Run `ch19_durable.py --crash 2`, show the step statuses in `jobs.db` with `sqlite3`, resume, and show `services.json` holds one account and one email (exercise 19.3).
- Repeat with `--crash 3` and a deleted `jobs.db`, and explain which duplicated side effect appears and which record would have prevented it (exercise 19.3, section 19.5).
- Show from `_run_step` that a `Permanent` error fails at once while a transient one backs off 1, 2 and 4 seconds and escalates after three attempts (section 19.4).
- Run two workers on five jobs with a short `LEASE`, crash one mid-job, and show all five finish, the other worker completed the crashed job and `services.json` has exactly one charge per job (exercise 19.4).
- Add a dollar budget per job and show a job with a tiny budget stops as `needs_human` with a reason naming the budget while a normal job finishes (exercise 19.5).
- Run `ch19_harness.py` sessions in a loop with one crash between sessions, and show every item passing or escalated, `progress.md` telling the story, and your SQL cross-check catching a number you changed by hand (exercise 19.6).

## Chapter 20: Planning and Model Routing

- Write five bad plans and one good one by hand, and pass a test showing `check_plan` rejects each bad plan with the right reason and accepts the good one, with no model call (exercise 20.3).
- Make a step in a plan fail, and show from the trace that `execute` replans only the remaining work, keeps finished results and stops at its replan limit (section 20.5).
- Change the executor to run ready steps together with `get_ready()` and `done()`, and report the wall time of a two-branch plan run serially and in parallel (exercise 20.4).
- Label 12 SQL tasks easy or hard, run `by_rules` and `by_model` on them, and report each router's accuracy and how many hard tasks it sent to the small model (exercise 20.5).
- Run the comparison in `ch20_router.py` and report cost per successful task for always-large, always-small, rules and the cascade, or successes and time on the local model (section 20.9).
- Turn a checked plan into a Chapter 19 durable job routed by `by_rules`, crash it halfway, and show the resumed job repeats no finished step or model call and reports the model for each step (exercise 20.6).

## Chapter 21: Multi-Agent Orchestration

- Run `ch21_orchestrator.py` with `Board(max_tasks=2)` and then `Board(max_depth=0)` (exercise 21.3), and explain every row of the board and what the lead did when a delegation was refused.
- Write a result schema for a handoff (exercise 21.2) and show that `jsonschema` rejects a result with a missing source, a price that isn't a number or more than 15 prices.
- Make a specialist fail three ways (exercise 21.4) and prove with a test that each failure reaches the lead as an `ERROR:` result, with no exception raised.
- Publish an agent with `ch21_a2a_server.py`, read its card at `/.well-known/agent-card.json` and get a task answered through `ch21_a2a_client.py`; then use the decision card in section 21.8 to say why your own in-process agents don't need A2A.
- Sweep tool latency with `ch21_coordination.py` (exercise 21.7) and name the smallest latency at which the team beats a one-at-a-time single agent on p95, and whether it ever beats one with parallel tool calls.
- Use `failure_propagation` to find how many workers a lead with two steps can have at 97% per step before the chance that every part is right drops below 80%, with and without one retry per worker.

## Chapter 22: Hybrid Architectures: Probabilistic Intelligence, Deterministic Control

- Apply section 22.1's 1-in-50 test to every decision in an expense assistant (exercise 22.1), giving each an owner and, wherever the model owns it, the check or evaluation that keeps it honest.
- Run `ch22_guarded.py` (exercise 22.3) and, for each of the five requests, name its states and the line of code behind each transition, including why the $5,000 request refunded nothing like $5,000.
- Move `POLICY` into a versioned `refund_policy.json` (exercise 22.4) and pass boundary tests at day 30 and day 31 and at $100 and $100.01, with the policy version in every case's log.
- Attack `handle` with six messages and a scripted model that obeys the attacker (exercise 22.5), and show by test that no case refunds over policy, refunds the wrong order or sends an amount code didn't decide.
- Guard the Chapter 8 analyst with SQLite's `set_authorizer` (exercise 22.6) and show writes, `ATTACH`, other tables and `PRAGMA` refused by the authorizer while `eval_sql.jsonl` still passes.

## Chapter 23: Computer-Use Agents

- Drive the back office by hand with `Browser` (exercise 23.3): the address changes, the credit is refused for lack of approval, another site is refused by the allowlist, and you can show the action log and screenshots.
- Run the injected note against a scripted model that obeys it (exercise 23.4) and name which layer from section 23.6 stops each part; you pass when no credit is issued and the email is unchanged.
- Verify a queue of address changes in code, not through the agent (exercise 23.5), so a request the agent claims but didn't do is reported as failed.
- Run `ch23_reliability.py` and explain from its log why the timed-out credit click was verified and never clicked again, and when the same step would end in `needs_human` instead.
- Run four requests through `run_steps` with three injected faults (exercise 23.7) and get done, done, needs a person, session lost; after the resume, the audit shows three address writes and no credit.

## Chapter 24: Skills, Frameworks and Agent Runtimes

- Map each part of your Chapter 13 agent to its Claude Agent SDK equivalent (exercise 24.1, table in section 24.1), and mark anything you'd still write yourself.
- Run `ch24_agent_sdk.py` with "Delete all cancelled orders." (exercise 24.3) and show a `deny` in `decisions` with the database unchanged; explain why listing `run_query` in `allowed_tools` would skip that check.
- Write a skill that `validate()` in `ch24_skills.py` accepts with no problems, and show from the trace that three test questions each load the right skill, or none (exercise 24.6).
- Measure whether `sql-report` earns its tokens (exercise 24.8): a table of pass rates with and without the skill, each answer checked in code.
- Run `ch24_skill_registry.py` and explain why 1.1.0 was refused by the gate, why the edited `shop-schema` failed to install and why a lockfile pinned to 1.2.0 is refused after the rollback.
- Write `promote_reviewed` (exercise 24.10) so 1.3.0, which adds `send_email`, is held for needing a major version, and 2.0.0 is promoted only once a named reviewer approves it.

## Chapter 25: Agentic Security

- Find the lethal trifecta in each agent of exercise 25.1 and remove one leg with a change in code or configuration, never a sentence in a prompt.
- Run `ch25_guards.py` (exercise 25.3), move the injection into a Markdown image, and name the guard that stopped each attempt and what `sanitize_markdown` removed.
- Add calendar invites as a second quarantined source (exercise 25.4) and show by test that the planner never receives an invite's description and the external invite creates no task.
- Evade your own leak scan five ways (exercise 25.5), then harden `scan` until all five are blocked while your list of ordinary arguments still passes.
- Run `./course.sh check-solutions -k security_scenarios` (section 25.10), then write a scenario of your own with both halves: the attack succeeds without the control, fails with it, and you've stated what remains.
- Score an agent with `ch25_risk.py`, name the one factor whose cut drops it a tier, and build a launch gate (exercise 25.7) that refuses it again when you add long-term memory.

## Chapter 26: Agent Identity and Authorization

- Mint a support-agent token and break it five ways (exercise 26.3), finding a different reason for each failure in `AUDIT` or the exception; then show `AGENTS` stops `refunds:create` for the analyst.
- Run `ch26_identity.py` and explain why Ben's refund is refused before anyone is asked, and why the step-up token for Ana's refund can't be reused or raised.
- Give the Chapter 21 team attenuated tokens (exercise 26.4) and prove by test that each specialist holds only its scopes, expires no later than the lead and stops working when the lead's token is revoked.
- Run `ch26_discovery.py` and, for each of the five capabilities, name the check from section 26.9 (trust per kind, signature, pin or protocol version) that rejected, skipped or selected it.
- Explain from the demo output in section 26.10 why ShipFast's agent got `pickups:create` but not `orders:read`, and why revoking your agent's token also stops the partner's.
- Build `select_reviewed` and `approve` (exercise 26.7) so the agent uses 2.1.0 before review, 2.2.0 after approval and 2.1.0 again once 2.2.0's text changes, and a stale-hash approval pins nothing.

## Chapter 27: Agent Evaluation: Dimensions, Trajectories and Scorecards

- Run `python ch27_eval.py eval_sql.jsonl 3` with six cases of your own added (exercise 27.3) and report the pass rate with its 95% interval, pass^k and a cause for every flaky case.
- Calibrate `ch27_judge` against `judge_calibration.jsonl` (exercise 27.5): report Cohen's kappa before and after one rubric change, and trust the judge in CI only at about 0.6 or above.
- Grade six cases on the path with `grade` (exercise 27.6) and produce at least one run whose outcome passed and process failed, naming the trajectory rule that caught it.
- Read the `ch27_scorecard.py` demo and explain why task success is 100% but success rate 83%, and which dimension caught the false "the cancelled orders are gone" claim.
- Turn the scorecard into a CI gate (exercise 27.8) that exits non-zero on its thresholds, then flip it to FAIL by removing `get_schema`; use `gate` to explain why 90% against 85% on 20 runs each doesn't block.
- Simulate a week of production (exercise 27.7) and get `drift` to flag the day the pass rate drops and no day before it.

## Chapter 28: AgentOps: Observability, Telemetry and SLOs for Agents

- Run `ch28_otel.py` and `ch28_agentops.py spans.jsonl`, break one tool on purpose (exercise 28.3), and show the second report classifies the failing runs and raises an alert that names the tool.
- Read a run's `timeline` and `latency_breakdown` and say whether model, tools or "other" dominates, and what you'd change first for each case in section 28.6.
- Script ten incidents with `build_spans` and classify them with `classify_detailed` (exercise 28.7); name the incidents that would look healthy without their eval result.
- Build the dashboard from spans (exercise 28.6): on the sample, task success shows as missed with a negative budget, and on your own traces the eval-based SLOs say "no data".
- Add a burn-rate alert to a simulated day (exercise 28.5) that fires within two hours of an afternoon incident, not before, and clears after it ends.
- Run `ch28_profile.py` and name the resource behind the slow tail of `run_sql` and `render_chart`, with lift and correlation; then add `fx_rates` (exercise 28.8) and show why profile samples need the span id.

## Chapter 29: Agent Performance Engineering: Latency, Throughput and Cost

- Compute `latency_model` and `cost_per_task` for one run and name the biggest term; check yourself on section 29.1's example, where human review is 39% of a $0.155 task.
- Show coordinated omission with `ch29_loadtest.py` (exercise 29.1): a table of p50 and p95 for both clocks at 4, 8 and 12 requests per second, and which clock hides the queue.
- Wrap the Chapter 8 analyst in a $0.02 request budget and a $0.10 daily `DailyBudget` (exercise 29.4), and show by test that each trips at the computed moment while another user is unaffected.
- Sweep concurrency with `ch29_perf.py` (exercise 29.6), name the knee and the limiting resource, and explain why at 16 in flight throughput rises while goodput falls.
- Read `ch29_benchmark.py`'s results in section 29.8's four-step order and pick a design; in exercise 29.7, say at which small-model error rate it stops meeting a 95% success bar.
- Run `ch29_economics.py`, state the break-even automation and failure rates and the assumption with the biggest payback swing; then find the failure rate at which Haiku's net saving equals Sonnet's (exercise 29.8).

## Chapter 30: Deploying Agents: From One Service to an Agent Platform

- Call the agent API so it returns 401, 429 with `Retry-After`, 404 for another caller's session and 409 for a concurrent request, and explain each code (exercises 30.1 and 30.3).
- Build the image with `ch30_service.Dockerfile` and pass `ch30_smoke_test.py` against the local container and the public HTTPS URL, saying where each secret lives (exercise 30.7).
- Point the Chapter 13 hub at the remote to-do server (exercise 30.5) and show a wrong token fails clearly and `MCP_READONLY_TOKEN` can list tasks but not add one.
- Call `start_report` twice with the same `request_id` and get one job id, and finish a job in one `job_status` call with `wait_s` (exercise 30.10).
- Run `ch30_gateway.py` and explain each refusal; then change `search_tools` so a caller finds only the tools its token allows, and nothing without a token (exercise 30.9).
- Run `ch30_improvement_loop.py` and explain why 1.5 is promoted and 1.6 rolled back at the canary; then write a stricter shadow stage (exercise 30.12) that rejects 1.6 for p95 latency before any user sees it.

## Chapter 31: From Prototype to Customer Production

- Name what's missing from three vague requests before a brief could pass `check_brief`, with the question you'd ask next for each (exercise 31.1).
- Write a `ProblemBrief` for a narrow workflow of your choice that passes `check_brief`, and show the original request fails it on at least four counts (exercise 31.2).
- Run `ch31_field.py`, explain why the claim summary is the first slice and why automatic approval isn't, and fix each of the eight violations in the draft design (sections 31.3 and 31.4).
- Add a rule for the personal data a design sends to a model, and show it catches an unredacted design and passes one whose model runs in the customer's network (exercise 31.3).
- Read a pilot's results with `pilot_gate`, explain hold, promote and stop to a customer owner, and say how many more runs a held pilot needs (exercise 31.4).
- Draft a brief from interview notes with `draft_brief`, find what `check_brief` still flags and close the gaps with follow-up answers (exercise 31.5).
