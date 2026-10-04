# Where to learn more

Every link from the book's **Learn more** sections and Appendix G, so you can click them. Checked September 2026.

## When you're stuck: where to ask

- **[Anthropic Discord](https://discord.com/invite/anthropic)**: Ask questions about Claude and the API; developers and Anthropic staff
- **[Anthropic Help Center](https://support.claude.com)**: Account, billing and API key questions
- **[Claude status page](https://status.claude.com)**: Check whether an outage is causing your errors
- **[Stack Overflow: python tag](https://stackoverflow.com/questions/tagged/python)**: Search first: most error messages have been asked before
- **[r/learnpython](https://www.reddit.com/r/learnpython/)**: A friendly community for beginner Python questions
- **[Python Discourse: Python Help](https://discuss.python.org/c/help/7)**: The official Python forum's help category
- **[MCP discussions on GitHub](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions)**: Questions and proposals about MCP
- **[Docker Community Forums](https://forums.docker.com)**: Installation and container problems

## Free courses

- **[Anthropic Academy](https://anthropic.skilljar.com)**: Free courses: Claude API, MCP, Claude Code, agent skills
- **[Anthropic courses on GitHub](https://github.com/anthropics/courses)**: Free notebooks: prompt engineering and tool use
- **[DeepLearning.AI short courses](https://www.deeplearning.ai/courses?types=short_course)**: One- to two-hour free courses on agents, RAG, evals and MCP
- **[Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course)**: Free, vendor-neutral, with a certificate
- **[Hugging Face MCP Course](https://huggingface.co/learn/mcp-course)**: Free MCP course with hands-on units
- **[Claude docs: Prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)**: Writing prompts that work; useful in every chapter

## Keeping up to date

- **[Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)**: New models, API features and deprecations, as they ship
- **[Claude docs: Models overview](https://platform.claude.com/docs/en/models/overview)**: Current model names and prices; check before changing MODEL in .env
- **[Anthropic Engineering blog](https://www.anthropic.com/engineering)**: In-depth posts on agents, tools, evals and context
- **[MCP blog](https://blog.modelcontextprotocol.io)**: Protocol changes and new specification versions
- **[Simon Willison's weblog](https://simonwillison.net)**: A well-known independent developer's daily notes on LLMs and agent security
- **[MCP roadmap](https://modelcontextprotocol.io/development/roadmap)**: The protocol's priorities and upcoming changes

## How to Use This Book

- [Anthropic Academy (free courses)](https://anthropic.skilljar.com) (Start here): Free video courses on the Claude API, MCP and Claude Code, with certificates
- [Claude Developer Platform docs](https://platform.claude.com/docs/en/home) (Start here): The official reference for everything the book calls through the API
- [Anthropic courses on GitHub](https://github.com/anthropics/courses) (Start here): Free notebooks: API fundamentals, prompt engineering, tool use
- [Claude Cookbooks](https://github.com/anthropics/claude-cookbooks) (Go deeper): Short, runnable recipes for common tasks (tools, RAG, caching, agents)
- [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course) (Go deeper): A free, vendor-neutral course on agents, good as a second viewpoint

## Chapter 0: Foundations

- [MDN: Command line crash course](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Command_line) (Start here): The terminal from zero: folders, paths, running commands
- [Docker: Get started](https://docs.docker.com/get-started/) (Start here): What images and containers are, with a guided first run
- [Docker Desktop install guide](https://docs.docker.com/desktop/) (Start here): Step-by-step install for Windows, macOS and Linux
- [Claude docs: Get your API key](https://platform.claude.com/docs/en/get-api-key) (Start here): The official step-by-step guide to creating a key
- [Claude Console: API keys](https://platform.claude.com/settings/keys) (Start here): Where you create API keys, add billing and set spending limits
- [JSON introduction](https://www.json.org/json-en.html) (Start here): The whole JSON format on one page
- [JSON Schema: Getting started](https://json-schema.org/learn/getting-started-step-by-step) (Go deeper): How schemas describe data, the format every tool uses
- [MDN: An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview) (Go deeper): Requests, responses, status codes and headers
- [The Twelve-Factor App: Config](https://12factor.net/config) (Go deeper): Why secrets live in environment variables, not in code

## Interlude: The Python You'll Need

- [The official Python tutorial](https://docs.python.org/3/tutorial/) (Start here): Free and complete; chapters 3 to 5 and 9 cover this interlude
- [Python for Everybody](https://www.py4e.com) (Start here): A free beginner course with videos, for people who have never programmed
- [CS50's Introduction to Programming with Python](https://cs50.harvard.edu/python/) (Start here): Harvard's free Python course with lectures and problem sets
- [Automate the Boring Stuff with Python](https://automatetheboringstuff.com) (Start here): Free online book of practical Python for everyday tasks
- [Python Tutor](https://pythontutor.com/visualize.html) (Start here): Paste a few lines and watch them run step by step: variables, lists, function calls
- [Exercism: Python track](https://exercism.org/tracks/python) (Start here): Free small exercises with automated feedback, to practice the fundamentals
- [Real Python: Primer on decorators](https://realpython.com/primer-on-python-decorators/) (Go deeper): Decorators explained step by step (section 5)
- [Python docs: dataclasses](https://docs.python.org/3/library/dataclasses.html) (Go deeper): Reference for @dataclass and field()
- [mypy: Type hints cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) (Go deeper): The type-hint syntax MCP uses to build tool schemas (Chapter 12)

## Chapter 1: What an Agent Is (and Isn't)

- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Start here): The workflows-versus-agents distinction this chapter uses
- [Claude docs: Get started](https://platform.claude.com/docs/en/get-started) (Start here): Your first API call, in Python and other languages
- [Claude docs: Messages API reference](https://platform.claude.com/docs/en/api/messages) (Go deeper): Every parameter of messages.create
- [Claude docs: Models overview](https://platform.claude.com/docs/en/models/overview) (Go deeper): Which models exist, their prices and context sizes
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) (Go deeper): The library the book uses: README, examples and changelog

## Interlude: Testing with pytest

- [pytest: Get started](https://docs.pytest.org/en/stable/getting-started.html) (Start here): Install, write and run your first tests
- [Real Python: Effective testing with pytest](https://realpython.com/pytest-python-testing/) (Start here): A friendly tour of fixtures, marks and parametrize
- [pytest: How to parametrize tests](https://docs.pytest.org/en/stable/how-to/parametrize.html) (Go deeper): One test, many inputs (exercise T.2)
- [pytest: How to monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) (Go deeper): Replacing functions and settings in tests (exercise T.4)

## Chapter 2: Tool Calling (Function Calling)

- [Claude docs: Tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) (Start here): How tool calling works, with examples
- [Claude docs: How to implement tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use) (Start here): Writing tool definitions, tool_choice and handling results
- [Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (Go deeper): How to name, describe and test tools so models use them well
- [Python docs: ast module](https://docs.python.org/3/library/ast.html) (Go deeper): The syntax trees the safe calculator walks
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) (Go deeper): The standard list of LLM security risks, including tool misuse

## Chapter 3: Tool Selection, Routing and Tool Search

- [Claude docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) (Start here): messages.parse, JSON schemas and strict tools
- [Pydantic documentation](https://pydantic.dev/docs/validation/latest/get-started/) (Start here): The data classes used for structured outputs
- [Claude docs: How to implement tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use) (Go deeper): tool_choice settings and writing descriptions
- [Python docs: zoneinfo](https://docs.python.org/3/library/zoneinfo.html) (Go deeper): Time zones for exercise 3.3
- [Claude docs: Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) (Go deeper): Deferring tools and letting the model search for them (section 3.6)

## Chapter 4: The Agent Loop

- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Start here): When to use a loop, and how to keep it simple
- [Claude docs: Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons) (Start here): What each `stop_reason` means (including refusals) and what to do next
- [Claude docs: Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) (Go deeper): Adaptive thinking, display options, effort and turning thinking off (section 4.8)
- [Claude docs: Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming) (Go deeper): Showing output as it arrives
- [ReAct paper (Yao et al., 2022)](https://arxiv.org/abs/2210.03629) (Go deeper): The research idea behind 'think, act, observe' loops
- [Claude docs: Migrating to Claude Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/migration-guide) (Go deeper): What changed in the current default model: thinking, sampling settings, tokenizer

## Chapter 5: State and Short-Term Memory

- [Claude docs: Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) (Start here): How much a model can hold, and what happens at the limit
- [Python docs: json module](https://docs.python.org/3/library/json.html) (Start here): Saving and loading conversation state
- [Claude docs: Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) (Go deeper): Anthropic's built-in approach to long-term memory
- [Claude docs: Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) (Go deeper): Measuring how big a conversation has become

## Interlude: Regular Expressions

- [RegexOne](https://regexone.com) (Start here): Interactive beginner lessons, one idea at a time
- [regex101](https://regex101.com) (Start here): Test a pattern and see each part explained (choose the Python flavor)
- [Python docs: Regular expression HOWTO](https://docs.python.org/3/howto/regex.html) (Go deeper): The official gentle introduction
- [Python docs: re module](https://docs.python.org/3/library/re.html) (Go deeper): Every function and flag

## Chapter 6: Agentic Search: Exploring an Environment

- [Python docs: pathlib](https://docs.python.org/3/library/pathlib.html) (Start here): Working with files and folders safely
- [Claude docs: Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool) (Go deeper): Anthropic's built-in tool for viewing and editing files
- [Claude Code overview](https://code.claude.com/docs/en/overview) (Go deeper): A production agent that explores codebases with the same ideas
- [OWASP: Path traversal](https://owasp.org/www-community/attacks/Path_Traversal) (Go deeper): Why tools must stay inside their folder

## Chapter 7: Real APIs

- [Open-Meteo API documentation](https://open-meteo.com/en/docs) (Start here): The free weather API used in this chapter; no key needed
- [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status) (Start here): What 200, 404, 429 and 503 mean
- [HTTPX documentation](https://www.python-httpx.org) (Start here): The Python HTTP client used for API calls
- [AWS: Exponential backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) (Go deeper): Why retries wait longer each time, with randomness
- [MDN: Retry-After header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After) (Go deeper): How a server tells you when to try again
- [Claude docs: Rate limits](https://platform.claude.com/docs/en/api/rate-limits) (Go deeper): The limits on your own API usage, and how to read them
- [Public APIs list](https://github.com/public-apis/public-apis) (Go deeper): Hundreds of free APIs to build your own tools against

## Interlude: SQL in One Sitting

- [SQLBolt](https://sqlbolt.com) (Start here): Free interactive SQL lessons in the browser
- [W3Schools SQL tutorial](https://www.w3schools.com/sql/) (Start here): Short pages with a try-it editor for each statement
- [SQLite: SQL as understood by SQLite](https://www.sqlite.org/lang.html) (Go deeper): The reference for the database the kit uses
- [Python docs: sqlite3](https://docs.python.org/3/library/sqlite3.html) (Go deeper): Running SQL from Python, with placeholders

## Chapter 8: Self-Correction: A Text-to-SQL Agent

- [Uber: QueryGPT](https://www.uber.com/us/en/blog/query-gpt/) (Start here): A real natural-language-to-SQL system and what it took
- [Claude docs: Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations) (Start here): Techniques for grounding answers in real data
- [OWASP: SQL injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) (Go deeper): Why the SQL tools use read-only connections and placeholders
- [Reflexion paper (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366) (Go deeper): Research on agents that learn from their own errors

## Interlude: Measuring an Agent

- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (Start here): Tasks, trials and graders, and why agents need repeated runs
- [Claude docs: Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) (Start here): Writing test cases and checks for a model-based system
- [Wikipedia: Binomial proportion confidence interval](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval) (Go deeper): The Wilson interval used in `i_measure.py`, and why simpler formulas fail for small samples

## Chapter 9: Human-in-the-Loop Approval

- [Google PAIR: People + AI Guidebook](https://pair.withgoogle.com/guidebook/) (Start here): Designing AI that people can trust, check and correct
- [Claude Code: permission modes](https://code.claude.com/docs/en/permission-modes) (Go deeper): How a production agent decides what needs your approval
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) (Go deeper): The standard framework for rating and controlling AI risk

## Chapter 10: Feedback Loops

- [Python docs: subprocess](https://docs.python.org/3/library/subprocess.html) (Start here): Running tests and commands from Python, with timeouts
- [Docker: Engine security](https://docs.docker.com/engine/security/) (Go deeper): What containers do and don't isolate
- [SWE-bench](https://www.swebench.com) (Go deeper): The benchmark for agents that fix real GitHub issues
- [Claude Code: Security](https://code.claude.com/docs/en/security) (Go deeper): Guardrails a production coding agent uses

## Interlude: Asynchronous Python

- [Real Python: Async IO in Python](https://realpython.com/async-io-python/) (Start here): async, await and the event loop, with examples
- [Python docs: asyncio](https://docs.python.org/3/library/asyncio.html) (Go deeper): The official reference, including gather and timeouts
- [Claude docs: Python SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) (Go deeper): Installing the SDK, and AsyncAnthropic for parallel calls

## Chapter 11: Multi-Agent Systems

- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Start here): A lead agent with subagents, and what it costs
- [Cognition: Don't build multi-agents](https://cognition.com/blog/dont-build-multi-agents) (Go deeper): The case against splitting work too early
- [Claude Code: Subagents](https://code.claude.com/docs/en/sub-agents) (Go deeper): Subagents in a production tool
- [Agent2Agent (A2A) protocol](https://a2a-protocol.org/latest/) (Go deeper): An open standard for agents talking to other agents

## Chapter 12: MCP Fundamentals and Your First Server

- [MCP: Introduction](https://modelcontextprotocol.io/docs/getting-started/intro) (Start here): What MCP is and why it exists
- [MCP: Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server) (Start here): The official server quickstart
- [Anthropic Academy: Introduction to MCP](https://anthropic.skilljar.com/introduction-to-model-context-protocol) (Start here): A free video course that pairs well with this chapter
- [MCP blog: The 2026-07-28 specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/) (Start here): What the stateless protocol, multi round-trip requests and deprecations mean for you
- [DeepLearning.AI: MCP, Build Rich-Context AI Apps with Anthropic](https://www.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic) (Start here): A free short course building MCP servers and clients
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) (Go deeper): The library used for servers and clients in this book
- [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) (Go deeper): The testing tool from section 12.5
- [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course) (Go deeper): A free, vendor-neutral MCP course
- [MCP blog: MCP Apps](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) (Go deeper): Tools that show an interactive UI inside the chat
- [MCP blog: The new MCP roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/) (Go deeper): Where the protocol is heading: agent identity, progressive discovery, transports

## Chapter 13: Build Your Own MCP Client

- [MCP: Build an MCP client](https://modelcontextprotocol.io/docs/develop/build-client) (Start here): The official client quickstart
- [MCP: Architecture overview](https://modelcontextprotocol.io/docs/learn/architecture) (Start here): Hosts, clients, servers and the messages between them
- [MCP specification](https://modelcontextprotocol.io/specification) (Go deeper): The full protocol, for when you need exact details
- [Claude docs: MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) (Go deeper): Letting the API connect to remote MCP servers for you

## Chapter 14: Using Servers You Didn't Write

- [MCP reference servers](https://github.com/modelcontextprotocol/servers) (Start here): The filesystem, git, fetch, memory and time servers used here
- [MCP Registry](https://registry.modelcontextprotocol.io) (Start here): The official catalogue of public MCP servers
- [MCP: Security best practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices) (Go deeper): The protocol's own guidance on attacks and defenses
- [GitHub MCP server](https://github.com/github/github-mcp-server) (Go deeper): The GitHub server used in this chapter and in capstone 4

## Chapter 15: MCP in 2026: From Tool Calling to Agent Infrastructure

- [MCP blog: The 2026-07-28 specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/) (Start here): Every change in this chapter, from stateless requests to deprecations
- [MCP blog: The new MCP roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/) (Go deeper): Agent identity, progressive discovery and the other priorities
- [MCP joins the Agentic AI Foundation](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/) (Go deeper): Who runs MCP now, and how it's governed

## Chapter 16: Context Engineering

- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Start here): What to put in the context window, and what to leave out
- [Redis: The state of context engineering 2026](https://redis.io/resources/state-of-context-engineering-2026/) (Go deeper): Survey of how teams build, feed and govern agent context, and where it breaks
- [Claude docs: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) (Start here): Cache modes, minimum sizes and prices
- [Claude docs: Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) (Go deeper): Letting the API clear old tool results (section 16.6)
- [Claude docs: Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) (Go deeper): Roles, clear instructions and examples in system prompts
- [Claude docs: Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling) (Go deeper): Tools called from code in a sandbox (section 16.9)
- [Claude docs: Compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) (Go deeper): Server-side summaries of long conversations, on demand or at a threshold

## Chapter 17: Agent Memory Engineering

- [Claude docs: Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) (Start here): A standard tool interface for memory your own code stores
- [OWASP GenAI: Memory is a feature. It is also an attack surface](https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/) (Start here): How memory poisoning works and how to defend against it (section 17.8)
- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) (Go deeper): The industry risk list that includes memory and context poisoning
- [Torra and Bras-Amorós: Memory poisoning and secure multi-agent systems](https://arxiv.org/abs/2603.20357) (Go deeper): Research on poisoning semantic, episodic and short-term memory, and defenses
- [SQLite: FTS5 full-text search](https://www.sqlite.org/fts5.html) (Go deeper): The search engine behind both memory stores in this chapter

## Chapter 18: Agentic RAG and Knowledge Systems

- [Anthropic: Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) (Start here): Hybrid search, reranking and chunk context, with measurements
- [Claude docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings) (Start here): What embeddings are and which providers to use
- [Claude docs: Citations](https://platform.claude.com/docs/en/build-with-claude/citations) (Go deeper): Built-in citations to the source text
- [Wikipedia: Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25) (Go deeper): The keyword-ranking formula in the hybrid search
- [model2vec](https://github.com/MinishLab/model2vec) (Go deeper): The small, fast local embedding model used in the kit
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) (Go deeper): Compare embedding models on standard benchmarks
- [Singh et al.: Agentic Retrieval-Augmented Generation, a survey](https://arxiv.org/abs/2501.09136) (Go deeper): The patterns behind agentic RAG: planning, reflection, tool use and multi-agent retrieval

## Chapter 19: Long-Running Agents

- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (Start here): The initializer, progress file, feature list and one-feature-at-a-time approach from section 19.8
- [AWS Builders' Library: Timeouts, retries and backoff with jitter](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter) (Go deeper): Why retries need backoff, limits and jitter, from people who run very large systems
- [Stripe: Idempotent requests](https://docs.stripe.com/api/idempotent_requests) (Go deeper): A real payment API's idempotency keys (section 19.5)
- [microservices.io: The Saga pattern](https://microservices.io/patterns/data/saga.html) (Go deeper): Long transactions as steps with compensating steps (section 19.7)
- [Temporal documentation](https://docs.temporal.io/) (Go deeper): A durable execution platform: workflows, activities, retries and timers (section 19.9)

## Chapter 20: Planning and Model Routing

- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Start here): When to use workflows, when agents, and the planning patterns between them
- [Python docs: graphlib](https://docs.python.org/3/library/graphlib.html) (Start here): The topological sorter used to order and parallelize plan steps
- [Yao et al.: ReAct](https://arxiv.org/abs/2210.03629) (Go deeper): The research behind deciding step by step, reasoning between actions
- [Chen, Zaharia and Zou: FrugalGPT](https://arxiv.org/abs/2305.05176) (Go deeper): Cascades of models: try a cheap model first, escalate when needed
- [Ong et al.: RouteLLM](https://arxiv.org/abs/2406.18665) (Go deeper): Learning which requests a cheaper model can handle

## Chapter 21: Multi-Agent Orchestration

- [Microsoft: Multi-agent patterns](https://learn.microsoft.com/en-us/agents/architecture/multi-agent-patterns) (Start here): Serial, concurrent and orchestrated agents, and when to use MCP or A2A (section 21.8)
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Start here): A lead and subagents in production: briefs, effort and cost
- [Cemri et al.: Why do multi-agent LLM systems fail?](https://arxiv.org/abs/2503.13657) (Go deeper): Fourteen ways teams of agents fail, in three families: design, misalignment and verification
- [jsonschema for Python](https://python-jsonschema.readthedocs.io/) (Go deeper): The library that checks each result against its contract (section 21.2)
- [Agent2Agent (A2A) protocol](https://a2a-protocol.org/latest/) (Go deeper): The specification: agent cards, tasks, artifacts and security (section 21.7)
- [A2A Python SDK (a2a-sdk)](https://pypi.org/project/a2a-sdk/) (Go deeper): The official SDK used in section 21.7, with install options
- [A2A samples](https://github.com/a2aproject/a2a-samples) (Go deeper): Official example agents and clients in several languages

## Chapter 22: Hybrid Architectures: Probabilistic Intelligence, Deterministic Control

- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Start here): Workflows with model calls versus open-ended agents, and when each fits
- [Salesforce: AI agent trends for 2026](https://www.salesforce.com/blog/ai-agent-trends-2026/) (Start here): Deterministic guardrails and harnesses as the basis of enterprise agents
- [Python docs: sqlite3 set_authorizer](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.set_authorizer) (Go deeper): Letting code, not the prompt, decide what SQL may do (exercise 22.6)

## Chapter 23: Computer-Use Agents

- [Playwright for Python](https://playwright.dev/python/) (Start here): The browser automation library behind the harness: locators, waits and screenshots
- [Claude docs: Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) (Start here): Screenshot-and-click computer use for desktops, with recommended safeguards
- [OWASP GenAI: Prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) (Go deeper): Direct and indirect injection, including instructions hidden in web pages

## Chapter 24: Skills, Frameworks and Agent Runtimes

- [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) (Start here): The framework behind Claude Code, for building your own agents
- [Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python) (Start here): Install, examples and API
- [Agent Skills specification](https://agentskills.io/specification) (Start here): The open SKILL.md format used in section 24.7
- [LangChain documentation](https://docs.langchain.com) (Go deeper): LangChain and LangGraph agents
- [Pydantic AI](https://pydantic.dev/docs/ai/overview/) (Go deeper): A type-checked agent framework from the Pydantic team
- [Hugging Face smolagents](https://huggingface.co/docs/smolagents) (Go deeper): A minimal open-source agent library
- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) (Go deeper): Agents, environments, sessions and events (section 24.8)
- [Agent2Agent (A2A) protocol](https://a2a-protocol.org/latest/) (Go deeper): The open protocol for agents talking to other agents

## Chapter 25: Agentic Security

- [Simon Willison: The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (Start here): Private data plus untrusted content plus a way out (section 25.4)
- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (Start here): The ten agent risks mapped in section 25.9
- [Simon Willison: The Dual LLM pattern](https://simonwillison.net/2023/Apr/25/dual-llm-pattern/) (Go deeper): Separating the model that reads untrusted text from the one that acts (section 25.5)
- [Debenedetti et al.: Defeating prompt injections by design (CaMeL)](https://arxiv.org/abs/2503.18813) (Go deeper): Google DeepMind's design that turns the dual-LLM idea into a system
- [OWASP: SSRF prevention cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) (Go deeper): The SSRF attack section 25.4 defends against, and the standard defenses
- [NSA: MCP security design considerations](https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/nsa-releases-security-design-considerations-for-ai-driven-automation-leveraging/) (Go deeper): Government guidance on securing agents built with MCP

## Chapter 26: Agent Identity and Authorization

- [MCP: Authorization](https://modelcontextprotocol.io/docs/tutorials/security/authorization) (Start here): How MCP servers receive and check OAuth tokens
- [PyJWT documentation](https://pyjwt.readthedocs.io/) (Start here): The token library used in this chapter
- [OAuth 2.0 Token Exchange (RFC 8693)](https://www.rfc-editor.org/rfc/rfc8693) (Go deeper): The standard for 'this agent, acting for this user' tokens (section 26.8)
- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (Go deeper): ASI03, identity and privilege abuse, among the ten agent risks

## Chapter 27: Agent Evaluation: Dimensions, Trajectories and Scorecards

- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (Start here): How to build evals for agents, from a team that runs many
- [Claude docs: Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) (Start here): Writing test cases and graders
- [LangChain: State of Agent Engineering](https://www.langchain.com/state-of-agent-engineering) (Go deeper): Survey of 1,340 practitioners: how teams evaluate, observe and ship agents
- [Hamel Husain: Your AI product needs evals](https://hamel.dev/blog/posts/evals/) (Go deeper): A practical guide from someone who builds them for clients
- [Claude docs: Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing) (Go deeper): Running a judge over many cases at half price
- [Wikipedia: Binomial proportion confidence interval](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval) (Go deeper): The Wilson interval behind 'one run proves little'

## Chapter 28: AgentOps: Observability, Telemetry and SLOs for Agents

- [OpenTelemetry GenAI semantic conventions (repository)](https://github.com/open-telemetry/semantic-conventions-genai) (Start here): The span and attribute names for model and agent calls, in their own repository since 2026
- [OpenTelemetry: GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/) (Go deeper): The `gen_ai.*` attribute names used in ch28_otel.py
- [Google SRE book: Service level objectives](https://sre.google/sre-book/service-level-objectives/) (Go deeper): How to choose SLOs and use error budgets (section 28.10)
- [LangChain: State of Agent Engineering](https://www.langchain.com/state-of-agent-engineering) (Go deeper): How widely teams trace, and what they trace
- [Moffatt v. Air Canada, 2024 BCCRT 149](https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html) (Go deeper): The tribunal decision on a chatbot's invented refund policy (section 28.8)
- [Invariant Labs: GitHub MCP exploited](https://invariantlabs.ai/blog/mcp-github-vulnerability) (Go deeper): A 'toxic agent flow': prompt injection plus an over-broad token (section 28.8)
- [AI Incident Database](https://incidentdatabase.ai/) (Go deeper): Documented AI incidents, searchable, with sources

## Chapter 29: Agent Performance Engineering: Latency, Throughput and Cost

- [Claude docs: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) (Start here): The biggest single cost lever for agents (section 29.3)
- [Claude docs: Rate limits](https://platform.claude.com/docs/en/api/rate-limits) (Start here): Request and token limits, and how they're measured (section 29.7)
- [Gil Tene: How NOT to measure latency](https://www.infoq.com/presentations/latency-response-time/) (Go deeper): Percentiles and coordinated omission (section 29.6)
- [Wikipedia: Little's law](https://en.wikipedia.org/wiki/Little%27s_law) (Go deeper): Concurrency, arrival rate and latency (section 29.7)

## Chapter 30: Deploying Agents: From One Service to an Agent Platform

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) (Start here): Build a web API step by step; the base of ch30_service.py
- [MDN: Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) (Start here): How streaming responses reach the browser
- [Docker Compose documentation](https://docs.docker.com/compose/) (Go deeper): Running the agent and its servers together
- [MCP: Authorization](https://modelcontextprotocol.io/docs/tutorials/security/authorization) (Go deeper): OAuth for remote MCP servers, explained step by step
- [MCP: Tasks extension](https://modelcontextprotocol.io/extensions/tasks) (Start here): How tasks are created, polled, updated and cancelled (section 30.8)
- [The MCP Registry](https://modelcontextprotocol.io/registry/about) (Start here): What the registry stores and how publishers are verified (section 30.10)
- [MCP: Enterprise-Managed Authorization](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization) (Go deeper): Company-wide access control through the identity provider (section 30.11)
- [OAuth 2.0 Simplified](https://www.oauth.com) (Go deeper): Tokens, scopes and flows in plain language
- [OWASP API Security Top 10](https://owasp.org/API-Security/) (Go deeper): The common ways web APIs get attacked

## Capstone Projects

- [Capstone 1: Intercom Help, Fin AI Agent](https://www.intercom.com/help/en/collections/6485365-fin-ai-agent) (Go deeper): How a production support agent is set up, measured and handed off
- [Capstone 2: Uber, QueryGPT](https://www.uber.com/us/en/blog/query-gpt/) (Go deeper): Lessons from a large natural-language-to-SQL system
- [Capstone 3: Google SRE book, Managing incidents](https://sre.google/sre-book/managing-incidents/) (Go deeper): How on-call teams run an incident
- [Capstone 3 extension: Gil Tene, How NOT to measure latency](https://www.infoq.com/presentations/latency-response-time/) (Go deeper): Percentiles and coordinated omission, for the performance-regression extension
- [Capstone 4: SWE-bench](https://www.swebench.com) (Go deeper): How code-fixing agents are measured
- [Capstone 5: Anthropic, multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Go deeper): The design this capstone is modeled on
- [Capstone 6: Anthropic, Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (Start here): Progress files, feature lists and git checkpoints for agents that work across many sessions
- [Capstone 6: Playwright for Python](https://playwright.dev/python/) (Go deeper): The browser automation library the computer-use agent drives
