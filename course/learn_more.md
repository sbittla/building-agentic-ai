# Learn more: every link, by chapter

The book prints up to three **Start here** links per chapter; this file has the full lists, including the **Go deeper** reading. `python dev/make_resources.py` turns it into `RESOURCES.md`. Links were checked in September 2026; `dev/check_links.py` checks them every week.

## How to Use This Book

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic Academy (free courses)**<br>[anthropic.skilljar.com](https://anthropic.skilljar.com) | Free video courses on the Claude API, MCP and Claude Code, with certificates | Start here |
| **Claude Developer Platform docs**<br>[platform.claude.com/docs/en/home](https://platform.claude.com/docs/en/home) | The official reference for everything the book calls through the API | Start here |
| **Anthropic courses on GitHub**<br>[github.com/anthropics/courses](https://github.com/anthropics/courses) | Free notebooks: API fundamentals, prompt engineering, tool use | Start here |
| **Claude Cookbooks**<br>[github.com/anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks) | Short, runnable recipes for common tasks (tools, RAG, caching, agents) | Go deeper |
| **Hugging Face AI Agents Course**<br>[huggingface.co/learn/agents-course](https://huggingface.co/learn/agents-course) | A free, vendor-neutral course on agents, good as a second viewpoint | Go deeper |

## Chapter 0: Foundations

| Resource | What you'll find | Level |
| --- | --- | --- |
| **MDN: Command line crash course**<br>[developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Command_line](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Command_line) | The terminal from zero: folders, paths, running commands | Start here |
| **Docker: Get started**<br>[docs.docker.com/get-started](https://docs.docker.com/get-started/) | What images and containers are, with a guided first run | Start here |
| **Docker Desktop install guide**<br>[docs.docker.com/desktop](https://docs.docker.com/desktop/) | Step-by-step install for Windows, macOS and Linux | Start here |
| **Claude docs: Get your API key**<br>[platform.claude.com/docs/en/get-api-key](https://platform.claude.com/docs/en/get-api-key) | The official step-by-step guide to creating a key | Start here |
| **Claude Console: API keys**<br>[platform.claude.com/settings/keys](https://platform.claude.com/settings/keys) | Where you create API keys, add billing and set spending limits | Start here |
| **JSON introduction**<br>[json.org/json-en.html](https://www.json.org/json-en.html) | The whole JSON format on one page | Start here |
| **JSON Schema: Getting started**<br>[json-schema.org/learn/getting-started-step-by-step](https://json-schema.org/learn/getting-started-step-by-step) | How schemas describe data, the format every tool uses | Go deeper |
| **MDN: An overview of HTTP**<br>[developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview) | Requests, responses, status codes and headers | Go deeper |
| **The Twelve-Factor App: Config**<br>[12factor.net/config](https://12factor.net/config) | Why secrets live in environment variables, not in code | Go deeper |

## Interlude: The Python You'll Need

| Resource | What you'll find | Level |
| --- | --- | --- |
| **The official Python tutorial**<br>[docs.python.org/3/tutorial](https://docs.python.org/3/tutorial/) | Free and complete; chapters 3 to 5 and 9 cover this interlude | Start here |
| **Python for Everybody**<br>[py4e.com](https://www.py4e.com) | A free beginner course with videos, for people who have never programmed | Start here |
| **CS50's Introduction to Programming with Python**<br>[cs50.harvard.edu/python](https://cs50.harvard.edu/python/) | Harvard's free Python course with lectures and problem sets | Start here |
| **Automate the Boring Stuff with Python**<br>[automatetheboringstuff.com](https://automatetheboringstuff.com) | Free online book of practical Python for everyday tasks | Start here |
| **Python Tutor**<br>[pythontutor.com/visualize.html](https://pythontutor.com/visualize.html) | Paste a few lines and watch them run step by step: variables, lists, function calls | Start here |
| **Exercism: Python track**<br>[exercism.org/tracks/python](https://exercism.org/tracks/python) | Free small exercises with automated feedback, to practice the fundamentals | Start here |
| **Real Python: Primer on decorators**<br>[realpython.com/primer-on-python-decorators](https://realpython.com/primer-on-python-decorators/) | Decorators explained step by step (section 5) | Go deeper |
| **Python docs: dataclasses**<br>[docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html) | Reference for @dataclass and field() | Go deeper |
| **mypy: Type hints cheat sheet**<br>[mypy.readthedocs.io/en/stable/cheat_sheet_py3.html](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) | The type-hint syntax MCP uses to build tool schemas (Chapter 12) | Go deeper |

## Chapter 1: What an Agent Is (and Isn't)

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic: Building effective agents**<br>[anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents) | The workflows-versus-agents distinction this chapter uses | Start here |
| **Claude docs: Get started**<br>[platform.claude.com/docs/en/get-started](https://platform.claude.com/docs/en/get-started) | Your first API call, in Python and other languages | Start here |
| **Claude docs: Messages API reference**<br>[platform.claude.com/docs/en/api/messages](https://platform.claude.com/docs/en/api/messages) | Every parameter of messages.create | Go deeper |
| **Claude docs: Models overview**<br>[platform.claude.com/docs/en/models/overview](https://platform.claude.com/docs/en/models/overview) | Which models exist, their prices and context sizes | Go deeper |
| **Anthropic Python SDK**<br>[github.com/anthropics/anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python) | The library the book uses: README, examples and changelog | Go deeper |

## Interlude: Testing with pytest

| Resource | What you'll find | Level |
| --- | --- | --- |
| **pytest: Get started**<br>[docs.pytest.org/en/stable/getting-started.html](https://docs.pytest.org/en/stable/getting-started.html) | Install, write and run your first tests | Start here |
| **Real Python: Effective testing with pytest**<br>[realpython.com/pytest-python-testing](https://realpython.com/pytest-python-testing/) | A friendly tour of fixtures, marks and parametrize | Start here |
| **pytest: How to parametrize tests**<br>[docs.pytest.org/en/stable/how-to/parametrize.html](https://docs.pytest.org/en/stable/how-to/parametrize.html) | One test, many inputs (exercise T.2) | Go deeper |
| **pytest: How to monkeypatch**<br>[docs.pytest.org/en/stable/how-to/monkeypatch.html](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) | Replacing functions and settings in tests (exercise T.4) | Go deeper |

## Chapter 2: Tool Calling (Function Calling)

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Claude docs: Tool use overview**<br>[platform.claude.com/docs/en/agents-and-tools/tool-use/overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) | How tool calling works, with examples | Start here |
| **Claude docs: How to implement tool use**<br>[platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use) | Writing tool definitions, tool_choice and handling results | Start here |
| **Anthropic: Writing effective tools for agents**<br>[anthropic.com/engineering/writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | How to name, describe and test tools so models use them well | Go deeper |
| **Python docs: ast module**<br>[docs.python.org/3/library/ast.html](https://docs.python.org/3/library/ast.html) | The syntax trees the safe calculator walks | Go deeper |
| **OWASP Top 10 for LLM Applications**<br>[genai.owasp.org/llm-top-10](https://genai.owasp.org/llm-top-10/) | The standard list of LLM security risks, including tool misuse | Go deeper |

## Chapter 3: Tool Selection, Routing and Tool Search

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Claude docs: Structured outputs**<br>[platform.claude.com/docs/en/build-with-claude/structured-outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) | messages.parse, JSON schemas and strict tools | Start here |
| **Pydantic documentation**<br>[pydantic.dev/docs/validation/latest/get-started](https://pydantic.dev/docs/validation/latest/get-started/) | The data classes used for structured outputs | Start here |
| **Claude docs: How to implement tool use**<br>[platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use) | tool_choice settings and writing descriptions | Go deeper |
| **Python docs: zoneinfo**<br>[docs.python.org/3/library/zoneinfo.html](https://docs.python.org/3/library/zoneinfo.html) | Time zones for exercise 3.3 | Go deeper |
| **Claude docs: Tool search tool**<br>[platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) | Deferring tools and letting the model search for them (section 3.6) | Go deeper |

## Chapter 4: The Agent Loop

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic: Building effective agents**<br>[anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents) | When to use a loop, and how to keep it simple | Start here |
| **Claude docs: Handling stop reasons**<br>[platform.claude.com/docs/en/build-with-claude/handling-stop-reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons) | What each `stop_reason` means (including refusals) and what to do next | Start here |
| **Claude docs: Thinking**<br>[platform.claude.com/docs/en/build-with-claude/thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) | Adaptive thinking, display options, effort and turning thinking off (section 4.8) | Go deeper |
| **Claude docs: Streaming messages**<br>[platform.claude.com/docs/en/build-with-claude/streaming](https://platform.claude.com/docs/en/build-with-claude/streaming) | Showing output as it arrives | Go deeper |
| **ReAct paper (Yao et al., 2022)**<br>[arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629) | The research idea behind 'think, act, observe' loops | Go deeper |
| **Claude docs: Migrating to Claude Sonnet 5**<br>[platform.claude.com/docs/en/models/sonnet-5/migration-guide](https://platform.claude.com/docs/en/models/sonnet-5/migration-guide) | What changed in the current default model: thinking, sampling settings, tokenizer | Go deeper |

## Chapter 5: State and Short-Term Memory

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Claude docs: Context windows**<br>[platform.claude.com/docs/en/build-with-claude/context-windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) | How much a model can hold, and what happens at the limit | Start here |
| **Python docs: json module**<br>[docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html) | Saving and loading conversation state | Start here |
| **Claude docs: Memory tool**<br>[platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) | Anthropic's built-in approach to long-term memory | Go deeper |
| **Claude docs: Token counting**<br>[platform.claude.com/docs/en/build-with-claude/token-counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) | Measuring how big a conversation has become | Go deeper |

## Interlude: Regular Expressions

| Resource | What you'll find | Level |
| --- | --- | --- |
| **RegexOne**<br>[regexone.com](https://regexone.com) | Interactive beginner lessons, one idea at a time | Start here |
| **regex101**<br>[regex101.com](https://regex101.com) | Test a pattern and see each part explained (choose the Python flavor) | Start here |
| **Python docs: Regular expression HOWTO**<br>[docs.python.org/3/howto/regex.html](https://docs.python.org/3/howto/regex.html) | The official gentle introduction | Go deeper |
| **Python docs: re module**<br>[docs.python.org/3/library/re.html](https://docs.python.org/3/library/re.html) | Every function and flag | Go deeper |

## Chapter 6: Agentic Search: Exploring an Environment

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Python docs: pathlib**<br>[docs.python.org/3/library/pathlib.html](https://docs.python.org/3/library/pathlib.html) | Working with files and folders safely | Start here |
| **Claude docs: Text editor tool**<br>[platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool) | Anthropic's built-in tool for viewing and editing files | Go deeper |
| **Claude Code overview**<br>[code.claude.com/docs/en/overview](https://code.claude.com/docs/en/overview) | A production agent that explores codebases with the same ideas | Go deeper |
| **OWASP: Path traversal**<br>[owasp.org/www-community/attacks/Path_Traversal](https://owasp.org/www-community/attacks/Path_Traversal) | Why tools must stay inside their folder | Go deeper |

## Chapter 7: Real APIs

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Open-Meteo API documentation**<br>[open-meteo.com/en/docs](https://open-meteo.com/en/docs) | The free weather API used in this chapter; no key needed | Start here |
| **MDN: HTTP response status codes**<br>[developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status) | What 200, 404, 429 and 503 mean | Start here |
| **HTTPX documentation**<br>[python-httpx.org](https://www.python-httpx.org) | The Python HTTP client used for API calls | Start here |
| **AWS: Exponential backoff and jitter**<br>[aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) | Why retries wait longer each time, with randomness | Go deeper |
| **MDN: Retry-After header**<br>[developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After) | How a server tells you when to try again | Go deeper |
| **Claude docs: Rate limits**<br>[platform.claude.com/docs/en/api/rate-limits](https://platform.claude.com/docs/en/api/rate-limits) | The limits on your own API usage, and how to read them | Go deeper |
| **Public APIs list**<br>[github.com/public-apis/public-apis](https://github.com/public-apis/public-apis) | Hundreds of free APIs to build your own tools against | Go deeper |

## Interlude: SQL in One Sitting

| Resource | What you'll find | Level |
| --- | --- | --- |
| **SQLBolt**<br>[sqlbolt.com](https://sqlbolt.com) | Free interactive SQL lessons in the browser | Start here |
| **W3Schools SQL tutorial**<br>[w3schools.com/sql](https://www.w3schools.com/sql/) | Short pages with a try-it editor for each statement | Start here |
| **SQLite: SQL as understood by SQLite**<br>[sqlite.org/lang.html](https://www.sqlite.org/lang.html) | The reference for the database the kit uses | Go deeper |
| **Python docs: sqlite3**<br>[docs.python.org/3/library/sqlite3.html](https://docs.python.org/3/library/sqlite3.html) | Running SQL from Python, with placeholders | Go deeper |

## Chapter 8: Self-Correction: A Text-to-SQL Agent

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Uber: QueryGPT**<br>[uber.com/us/en/blog/query-gpt](https://www.uber.com/us/en/blog/query-gpt/) | A real natural-language-to-SQL system and what it took | Start here |
| **Claude docs: Reduce hallucinations**<br>[platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations) | Techniques for grounding answers in real data | Start here |
| **OWASP: SQL injection prevention**<br>[cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) | Why the SQL tools use read-only connections and placeholders | Go deeper |
| **Reflexion paper (Shinn et al., 2023)**<br>[arxiv.org/abs/2303.11366](https://arxiv.org/abs/2303.11366) | Research on agents that learn from their own errors | Go deeper |

## Interlude: Measuring an Agent

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic: Demystifying evals for AI agents**<br>[anthropic.com/engineering/demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Tasks, trials and graders, and why agents need repeated runs | Start here |
| **Claude docs: Define success criteria and build evaluations**<br>[platform.claude.com/docs/en/test-and-evaluate/develop-tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) | Writing test cases and checks for a model-based system | Start here |
| **Wikipedia: Binomial proportion confidence interval**<br>[en.wikipedia.org/wiki/Binomial_proportion_confidence_interval](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval) | The Wilson interval used in `i_measure.py`, and why simpler formulas fail for small samples | Go deeper |

## Chapter 9: Human-in-the-Loop Approval

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Google PAIR: People + AI Guidebook**<br>[pair.withgoogle.com/guidebook](https://pair.withgoogle.com/guidebook/) | Designing AI that people can trust, check and correct | Start here |
| **Claude Code: permission modes**<br>[code.claude.com/docs/en/permission-modes](https://code.claude.com/docs/en/permission-modes) | How a production agent decides what needs your approval | Go deeper |
| **NIST AI Risk Management Framework**<br>[nist.gov/itl/ai-risk-management-framework](https://www.nist.gov/itl/ai-risk-management-framework) | The standard framework for rating and controlling AI risk | Go deeper |

## Chapter 10: Feedback Loops

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Python docs: subprocess**<br>[docs.python.org/3/library/subprocess.html](https://docs.python.org/3/library/subprocess.html) | Running tests and commands from Python, with timeouts | Start here |
| **Docker: Engine security**<br>[docs.docker.com/engine/security](https://docs.docker.com/engine/security/) | What containers do and don't isolate | Go deeper |
| **SWE-bench**<br>[swebench.com](https://www.swebench.com) | The benchmark for agents that fix real GitHub issues | Go deeper |
| **Claude Code: Security**<br>[code.claude.com/docs/en/security](https://code.claude.com/docs/en/security) | Guardrails a production coding agent uses | Go deeper |

## Interlude: Asynchronous Python

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Real Python: Async IO in Python**<br>[realpython.com/async-io-python](https://realpython.com/async-io-python/) | async, await and the event loop, with examples | Start here |
| **Python docs: asyncio**<br>[docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html) | The official reference, including gather and timeouts | Go deeper |
| **Claude docs: Python SDK**<br>[platform.claude.com/docs/en/cli-sdks-libraries/sdks/python](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) | Installing the SDK, and AsyncAnthropic for parallel calls | Go deeper |

## Chapter 11: Multi-Agent Systems

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic: How we built our multi-agent research system**<br>[anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system) | A lead agent with subagents, and what it costs | Start here |
| **Cognition: Don't build multi-agents**<br>[cognition.com/blog/dont-build-multi-agents](https://cognition.com/blog/dont-build-multi-agents) | The case against splitting work too early | Go deeper |
| **Claude Code: Subagents**<br>[code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents) | Subagents in a production tool | Go deeper |
| **Agent2Agent (A2A) protocol**<br>[a2a-protocol.org/latest](https://a2a-protocol.org/latest/) | An open standard for agents talking to other agents | Go deeper |

## Chapter 12: MCP Fundamentals and Your First Server

| Resource | What you'll find | Level |
| --- | --- | --- |
| **MCP: Introduction**<br>[modelcontextprotocol.io/docs/getting-started/intro](https://modelcontextprotocol.io/docs/getting-started/intro) | What MCP is and why it exists | Start here |
| **MCP: Build an MCP server**<br>[modelcontextprotocol.io/docs/develop/build-server](https://modelcontextprotocol.io/docs/develop/build-server) | The official server quickstart | Start here |
| **Anthropic Academy: Introduction to MCP**<br>[anthropic.skilljar.com/introduction-to-model-context-protocol](https://anthropic.skilljar.com/introduction-to-model-context-protocol) | A free video course that pairs well with this chapter | Start here |
| **MCP blog: The 2026-07-28 specification**<br>[blog.modelcontextprotocol.io/posts/2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28/) | What the stateless protocol, multi round-trip requests and deprecations mean for you | Start here |
| **DeepLearning.AI: MCP, Build Rich-Context AI Apps with Anthropic**<br>[deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic](https://www.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic) | A free short course building MCP servers and clients | Start here |
| **MCP Python SDK**<br>[github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | The library used for servers and clients in this book | Go deeper |
| **MCP Inspector**<br>[modelcontextprotocol.io/docs/tools/inspector](https://modelcontextprotocol.io/docs/tools/inspector) | The testing tool from section 12.5 | Go deeper |
| **Hugging Face MCP Course**<br>[huggingface.co/learn/mcp-course](https://huggingface.co/learn/mcp-course) | A free, vendor-neutral MCP course | Go deeper |
| **MCP blog: MCP Apps**<br>[blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) | Tools that show an interactive UI inside the chat | Go deeper |
| **MCP blog: The new MCP roadmap**<br>[blog.modelcontextprotocol.io/posts/mcp-roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/) | Where the protocol is heading: agent identity, progressive discovery, transports | Go deeper |

## Chapter 13: Build Your Own MCP Client

| Resource | What you'll find | Level |
| --- | --- | --- |
| **MCP: Build an MCP client**<br>[modelcontextprotocol.io/docs/develop/build-client](https://modelcontextprotocol.io/docs/develop/build-client) | The official client quickstart | Start here |
| **MCP: Architecture overview**<br>[modelcontextprotocol.io/docs/learn/architecture](https://modelcontextprotocol.io/docs/learn/architecture) | Hosts, clients, servers and the messages between them | Start here |
| **MCP specification**<br>[modelcontextprotocol.io/specification](https://modelcontextprotocol.io/specification) | The full protocol, for when you need exact details | Go deeper |
| **Claude docs: MCP connector**<br>[platform.claude.com/docs/en/agents-and-tools/mcp-connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) | Letting the API connect to remote MCP servers for you | Go deeper |

## Chapter 14: Using Servers You Didn't Write

| Resource | What you'll find | Level |
| --- | --- | --- |
| **MCP reference servers**<br>[github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | The filesystem, git, fetch, memory and time servers used here | Start here |
| **MCP Registry**<br>[registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io) | The official catalog of public MCP servers | Start here |
| **MCP: Security best practices**<br>[modelcontextprotocol.io/docs/tutorials/security/security_best_practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices) | The protocol's own guidance on attacks and defenses | Go deeper |
| **GitHub MCP server**<br>[github.com/github/github-mcp-server](https://github.com/github/github-mcp-server) | The GitHub server used in this chapter and in capstone 4 | Go deeper |

## Chapter 15: MCP in 2026: From Tool Calling to Agent Infrastructure

| Resource | What you'll find | Level |
| --- | --- | --- |
| **MCP blog: The 2026-07-28 specification**<br>[blog.modelcontextprotocol.io/posts/2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28/) | Every change in this chapter, from stateless requests to deprecations | Start here |
| **MCP blog: The new MCP roadmap**<br>[blog.modelcontextprotocol.io/posts/mcp-roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/) | Agent identity, progressive discovery and the other priorities | Go deeper |
| **MCP joins the Agentic AI Foundation**<br>[blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/) | Who runs MCP now, and how it's governed | Go deeper |

## Chapter 16: Context Engineering

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic: Effective context engineering for AI agents**<br>[anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | What to put in the context window, and what to leave out | Start here |
| **Redis: The state of context engineering 2026**<br>[redis.io/resources/state-of-context-engineering-2026](https://redis.io/resources/state-of-context-engineering-2026/) | Survey of how teams build, feed and govern agent context, and where it breaks | Go deeper |
| **Claude docs: Prompt caching**<br>[platform.claude.com/docs/en/build-with-claude/prompt-caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | Cache modes, minimum sizes and prices | Start here |
| **Claude docs: Context editing**<br>[platform.claude.com/docs/en/build-with-claude/context-editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) | Letting the API clear old tool results (section 16.6) | Go deeper |
| **Claude docs: Prompting best practices**<br>[platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) | Roles, clear instructions and examples in system prompts | Go deeper |
| **Claude docs: Programmatic tool calling**<br>[platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling) | Tools called from code in a sandbox (section 16.9) | Go deeper |
| **Claude docs: Compaction**<br>[platform.claude.com/docs/en/build-with-claude/compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) | Server-side summaries of long conversations, on demand or at a threshold | Go deeper |

## Chapter 17: Agent Memory Engineering

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Claude docs: Memory tool**<br>[platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) | A standard tool interface for memory your own code stores | Start here |
| **OWASP GenAI: Memory is a feature. It is also an attack surface**<br>[genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface](https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/) | How memory poisoning works and how to defend against it (section 17.8) | Start here |
| **OWASP Top 10 for Agentic Applications**<br>[genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) | The industry risk list that includes memory and context poisoning | Go deeper |
| **Torra and Bras-Amorós: Memory poisoning and secure multi-agent systems**<br>[arxiv.org/abs/2603.20357](https://arxiv.org/abs/2603.20357) | Research on poisoning semantic, episodic and short-term memory, and defenses | Go deeper |
| **SQLite: FTS5 full-text search**<br>[sqlite.org/fts5.html](https://www.sqlite.org/fts5.html) | The search engine behind both memory stores in this chapter | Go deeper |

## Chapter 18: Agentic RAG and Knowledge Systems

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic: Introducing Contextual Retrieval**<br>[anthropic.com/news/contextual-retrieval](https://www.anthropic.com/news/contextual-retrieval) | Hybrid search, reranking and chunk context, with measurements | Start here |
| **Claude docs: Embeddings**<br>[platform.claude.com/docs/en/build-with-claude/embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings) | What embeddings are and which providers to use | Start here |
| **Claude docs: Citations**<br>[platform.claude.com/docs/en/build-with-claude/citations](https://platform.claude.com/docs/en/build-with-claude/citations) | Built-in citations to the source text | Go deeper |
| **Wikipedia: Okapi BM25**<br>[en.wikipedia.org/wiki/Okapi_BM25](https://en.wikipedia.org/wiki/Okapi_BM25) | The keyword-ranking formula in the hybrid search | Go deeper |
| **model2vec**<br>[github.com/MinishLab/model2vec](https://github.com/MinishLab/model2vec) | The small, fast local embedding model used in the kit | Go deeper |
| **MTEB leaderboard**<br>[huggingface.co/spaces/mteb/leaderboard](https://huggingface.co/spaces/mteb/leaderboard) | Compare embedding models on standard benchmarks | Go deeper |
| **Singh et al.: Agentic Retrieval-Augmented Generation, a survey**<br>[arxiv.org/abs/2501.09136](https://arxiv.org/abs/2501.09136) | The patterns behind agentic RAG: planning, reflection, tool use and multi-agent retrieval | Go deeper |

## Chapter 19: Long-Running Agents

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic: Effective harnesses for long-running agents**<br>[anthropic.com/engineering/effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | The initializer, progress file, feature list and one-feature-at-a-time approach from section 19.8 | Start here |
| **AWS Builders' Library: Timeouts, retries and backoff with jitter**<br>[builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter) | Why retries need backoff, limits and jitter, from people who run very large systems | Go deeper |
| **Stripe: Idempotent requests**<br>[docs.stripe.com/api/idempotent_requests](https://docs.stripe.com/api/idempotent_requests) | A real payment API's idempotency keys (section 19.5) | Go deeper |
| **microservices.io: The Saga pattern**<br>[microservices.io/patterns/data/saga.html](https://microservices.io/patterns/data/saga.html) | Long transactions as steps with compensating steps (section 19.7) | Go deeper |
| **Temporal documentation**<br>[docs.temporal.io](https://docs.temporal.io/) | A durable execution platform: workflows, activities, retries and timers (section 19.9) | Go deeper |

## Chapter 20: Planning and Model Routing

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic: Building effective agents**<br>[anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents) | When to use workflows, when agents, and the planning patterns between them | Start here |
| **Python docs: graphlib**<br>[docs.python.org/3/library/graphlib.html](https://docs.python.org/3/library/graphlib.html) | The topological sorter used to order and parallelize plan steps | Start here |
| **Yao et al.: ReAct**<br>[arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629) | The research behind deciding step by step, reasoning between actions | Go deeper |
| **Chen, Zaharia and Zou: FrugalGPT**<br>[arxiv.org/abs/2305.05176](https://arxiv.org/abs/2305.05176) | Cascades of models: try a cheap model first, escalate when needed | Go deeper |
| **Ong et al.: RouteLLM**<br>[arxiv.org/abs/2406.18665](https://arxiv.org/abs/2406.18665) | Learning which requests a cheaper model can handle | Go deeper |

## Chapter 21: Multi-Agent Orchestration

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Microsoft: Multi-agent patterns**<br>[learn.microsoft.com/en-us/agents/architecture/multi-agent-patterns](https://learn.microsoft.com/en-us/agents/architecture/multi-agent-patterns) | Serial, concurrent and orchestrated agents, and when to use MCP or A2A (section 21.8) | Start here |
| **Anthropic: How we built our multi-agent research system**<br>[anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system) | A lead and subagents in production: briefs, effort and cost | Start here |
| **Cemri et al.: Why do multi-agent LLM systems fail?**<br>[arxiv.org/abs/2503.13657](https://arxiv.org/abs/2503.13657) | Fourteen ways teams of agents fail, in three families: design, misalignment and verification | Go deeper |
| **jsonschema for Python**<br>[python-jsonschema.readthedocs.io](https://python-jsonschema.readthedocs.io/) | The library that checks each result against its contract (section 21.2) | Go deeper |
| **Agent2Agent (A2A) protocol**<br>[a2a-protocol.org/latest](https://a2a-protocol.org/latest/) | The specification: agent cards, tasks, artifacts and security (section 21.7) | Go deeper |
| **A2A Python SDK (a2a-sdk)**<br>[pypi.org/project/a2a-sdk](https://pypi.org/project/a2a-sdk/) | The official SDK used in section 21.7, with install options | Go deeper |
| **A2A samples**<br>[github.com/a2aproject/a2a-samples](https://github.com/a2aproject/a2a-samples) | Official example agents and clients in several languages | Go deeper |

## Chapter 22: Hybrid Architectures: Probabilistic Intelligence, Deterministic Control

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic: Building effective agents**<br>[anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents) | Workflows with model calls versus open-ended agents, and when each fits | Start here |
| **Salesforce: AI agent trends for 2026**<br>[salesforce.com/blog/ai-agent-trends-2026](https://www.salesforce.com/blog/ai-agent-trends-2026/) | Deterministic guardrails and harnesses as the basis of enterprise agents | Start here |
| **Python docs: sqlite3 set_authorizer**<br>[docs.python.org/3/library/sqlite3.html#sqlite3.Connection.set_authorizer](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.set_authorizer) | Letting code, not the prompt, decide what SQL may do (exercise 22.6) | Go deeper |

## Chapter 23: Computer-Use Agents

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Playwright for Python**<br>[playwright.dev/python](https://playwright.dev/python/) | The browser automation library behind the harness: locators, waits and screenshots | Start here |
| **Claude docs: Computer use tool**<br>[platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) | Screenshot-and-click computer use for desktops, with recommended safeguards | Start here |
| **OWASP GenAI: Prompt injection**<br>[genai.owasp.org/llmrisk/llm01-prompt-injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | Direct and indirect injection, including instructions hidden in web pages | Go deeper |

## Chapter 24: Skills, Frameworks and Agent Runtimes

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Claude Agent SDK overview**<br>[code.claude.com/docs/en/agent-sdk/overview](https://code.claude.com/docs/en/agent-sdk/overview) | The framework behind Claude Code, for building your own agents | Start here |
| **Claude Agent SDK for Python**<br>[github.com/anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) | Install, examples and API | Start here |
| **Agent Skills specification**<br>[agentskills.io/specification](https://agentskills.io/specification) | The open SKILL.md format used in section 24.7 | Start here |
| **LangChain documentation**<br>[docs.langchain.com](https://docs.langchain.com) | LangChain and LangGraph agents | Go deeper |
| **Pydantic AI**<br>[pydantic.dev/docs/ai/overview](https://pydantic.dev/docs/ai/overview/) | A type-checked agent framework from the Pydantic team | Go deeper |
| **Hugging Face smolagents**<br>[huggingface.co/docs/smolagents](https://huggingface.co/docs/smolagents) | A minimal open-source agent library | Go deeper |
| **Claude Managed Agents overview**<br>[platform.claude.com/docs/en/managed-agents/overview](https://platform.claude.com/docs/en/managed-agents/overview) | Agents, environments, sessions and events (section 24.8) | Go deeper |
| **Agent2Agent (A2A) protocol**<br>[a2a-protocol.org/latest](https://a2a-protocol.org/latest/) | The open protocol for agents talking to other agents | Go deeper |

## Chapter 25: Agentic Security

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Simon Willison: The lethal trifecta**<br>[simonwillison.net/2025/Jun/16/the-lethal-trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) | Private data plus untrusted content plus a way out (section 25.4) | Start here |
| **OWASP Top 10 for Agentic Applications**<br>[genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | The ten agent risks mapped in section 25.9 | Start here |
| **Simon Willison: The Dual LLM pattern**<br>[simonwillison.net/2023/Apr/25/dual-llm-pattern](https://simonwillison.net/2023/Apr/25/dual-llm-pattern/) | Separating the model that reads untrusted text from the one that acts (section 25.5) | Go deeper |
| **Debenedetti et al.: Defeating prompt injections by design (CaMeL)**<br>[arxiv.org/abs/2503.18813](https://arxiv.org/abs/2503.18813) | Google DeepMind's design that turns the dual-LLM idea into a system | Go deeper |
| **OWASP: SSRF prevention cheat sheet**<br>[cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) | The SSRF attack section 25.4 defends against, and the standard defenses | Go deeper |
| **NSA: MCP security design considerations**<br>[nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/nsa-releases-security-design-considerations-for-ai-driven-automation-leveraging](https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/nsa-releases-security-design-considerations-for-ai-driven-automation-leveraging/) | Government guidance on securing agents built with MCP | Go deeper |

## Chapter 26: Agent Identity and Authorization

| Resource | What you'll find | Level |
| --- | --- | --- |
| **MCP: Authorization**<br>[modelcontextprotocol.io/docs/tutorials/security/authorization](https://modelcontextprotocol.io/docs/tutorials/security/authorization) | How MCP servers receive and check OAuth tokens | Start here |
| **PyJWT documentation**<br>[pyjwt.readthedocs.io](https://pyjwt.readthedocs.io/) | The token library used in this chapter | Start here |
| **OAuth 2.0 Token Exchange (RFC 8693)**<br>[rfc-editor.org/rfc/rfc8693](https://www.rfc-editor.org/rfc/rfc8693) | The standard for 'this agent, acting for this user' tokens (section 26.8) | Go deeper |
| **OWASP Top 10 for Agentic Applications**<br>[genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | ASI03, identity and privilege abuse, among the ten agent risks | Go deeper |

## Chapter 27: Agent Evaluation: Dimensions, Trajectories and Scorecards

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Anthropic: Demystifying evals for AI agents**<br>[anthropic.com/engineering/demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | How to build evals for agents, from a team that runs many | Start here |
| **Claude docs: Define success criteria and build evaluations**<br>[platform.claude.com/docs/en/test-and-evaluate/develop-tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) | Writing test cases and graders | Start here |
| **LangChain: State of Agent Engineering**<br>[langchain.com/state-of-agent-engineering](https://www.langchain.com/state-of-agent-engineering) | Survey of 1,340 practitioners: how teams evaluate, observe and ship agents | Go deeper |
| **Hamel Husain: Your AI product needs evals**<br>[hamel.dev/blog/posts/evals](https://hamel.dev/blog/posts/evals/) | A practical guide from someone who builds them for clients | Go deeper |
| **Claude docs: Batch processing**<br>[platform.claude.com/docs/en/build-with-claude/batch-processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing) | Running a judge over many cases at half price | Go deeper |
| **Wikipedia: Binomial proportion confidence interval**<br>[en.wikipedia.org/wiki/Binomial_proportion_confidence_interval](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval) | The Wilson interval behind 'one run proves little' | Go deeper |

## Chapter 28: AgentOps: Observability, Telemetry and SLOs for Agents

| Resource | What you'll find | Level |
| --- | --- | --- |
| **OpenTelemetry GenAI semantic conventions (repository)**<br>[github.com/open-telemetry/semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai) | The span and attribute names for model and agent calls, in their own repository since 2026 | Start here |
| **OpenTelemetry: GenAI semantic conventions**<br>[opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/) | The `gen_ai.*` attribute names used in ch28_otel.py | Go deeper |
| **Google SRE book: Service level objectives**<br>[sre.google/sre-book/service-level-objectives](https://sre.google/sre-book/service-level-objectives/) | How to choose SLOs and use error budgets (section 28.10) | Go deeper |
| **LangChain: State of Agent Engineering**<br>[langchain.com/state-of-agent-engineering](https://www.langchain.com/state-of-agent-engineering) | How widely teams trace, and what they trace | Go deeper |
| **Moffatt v. Air Canada, 2024 BCCRT 149**<br>[canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html](https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html) | The tribunal decision on a chatbot's invented refund policy (section 28.8) | Go deeper |
| **Invariant Labs: GitHub MCP exploited**<br>[invariantlabs.ai/blog/mcp-github-vulnerability](https://invariantlabs.ai/blog/mcp-github-vulnerability) | A 'toxic agent flow': prompt injection plus an over-broad token (section 28.8) | Go deeper |
| **AI Incident Database**<br>[incidentdatabase.ai](https://incidentdatabase.ai/) | Documented AI incidents, searchable, with sources | Go deeper |

## Chapter 29: Agent Performance Engineering: Latency, Throughput and Cost

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Claude docs: Prompt caching**<br>[platform.claude.com/docs/en/build-with-claude/prompt-caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | The biggest single cost lever for agents (section 29.3) | Start here |
| **Claude docs: Rate limits**<br>[platform.claude.com/docs/en/api/rate-limits](https://platform.claude.com/docs/en/api/rate-limits) | Request and token limits, and how they're measured (section 29.7) | Start here |
| **Gil Tene: How NOT to measure latency**<br>[infoq.com/presentations/latency-response-time](https://www.infoq.com/presentations/latency-response-time/) | Percentiles and coordinated omission (section 29.6) | Go deeper |
| **Wikipedia: Little's law**<br>[en.wikipedia.org/wiki/Little%27s_law](https://en.wikipedia.org/wiki/Little%27s_law) | Concurrency, arrival rate and latency (section 29.7) | Go deeper |

## Chapter 30: Deploying Agents: From One Service to an Agent Platform

| Resource | What you'll find | Level |
| --- | --- | --- |
| **FastAPI tutorial**<br>[fastapi.tiangolo.com/tutorial](https://fastapi.tiangolo.com/tutorial/) | Build a web API step by step; the base of ch30_service.py | Start here |
| **MDN: Using server-sent events**<br>[developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) | How streaming responses reach the browser | Start here |
| **Docker Compose documentation**<br>[docs.docker.com/compose](https://docs.docker.com/compose/) | Running the agent and its servers together | Go deeper |
| **MCP: Authorization**<br>[modelcontextprotocol.io/docs/tutorials/security/authorization](https://modelcontextprotocol.io/docs/tutorials/security/authorization) | OAuth for remote MCP servers, explained step by step | Go deeper |
| **MCP: Tasks extension**<br>[modelcontextprotocol.io/extensions/tasks](https://modelcontextprotocol.io/extensions/tasks) | How tasks are created, polled, updated and cancelled (section 30.8) | Start here |
| **The MCP Registry**<br>[modelcontextprotocol.io/registry/about](https://modelcontextprotocol.io/registry/about) | What the registry stores and how publishers are verified (section 30.10) | Start here |
| **MCP: Enterprise-Managed Authorization**<br>[modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization) | Company-wide access control through the identity provider (section 30.11) | Go deeper |
| **OAuth 2.0 Simplified**<br>[oauth.com](https://www.oauth.com) | Tokens, scopes and flows in plain language | Go deeper |
| **OWASP API Security Top 10**<br>[owasp.org/API-Security](https://owasp.org/API-Security/) | The common ways web APIs get attacked | Go deeper |

## Chapter 31: The Forward-Deployed Playbook

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Palantir: A Day in the Life of a Forward Deployed Software Engineer**<br>[blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1) | The role where it began, described by the people who do it | Start here |
| **Palantir: Dev versus Delta**<br>[blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87](https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87) | How forward-deployed and product engineering divide the work | Start here |
| **PostHog: WTF is a forward deployed engineer?**<br>[posthog.com/blog/forward-deployed-engineer](https://posthog.com/blog/forward-deployed-engineer) | Why AI companies are hiring them, and what the work looks like day to day | Start here |
| **Aced: Forward Deployed Engineer Interview, the 2026 guide**<br>[aced.io/blog/forward-deployed-engineer-interview-the-definitive-2026-guide-fde](https://www.aced.io/blog/forward-deployed-engineer-interview-the-definitive-2026-guide-fde) | The interview loop round by round, with example questions (Appendix M) | Go deeper |

## Capstone Projects

| Resource | What you'll find | Level |
| --- | --- | --- |
| **Capstone 1: Intercom Help, Fin AI Agent**<br>[intercom.com/help/en/collections/6485365-fin-ai-agent](https://www.intercom.com/help/en/collections/6485365-fin-ai-agent) | How a production support agent is set up, measured and handed off | Go deeper |
| **Capstone 2: Uber, QueryGPT**<br>[uber.com/us/en/blog/query-gpt](https://www.uber.com/us/en/blog/query-gpt/) | Lessons from a large natural-language-to-SQL system | Go deeper |
| **Capstone 3: Google SRE book, Managing incidents**<br>[sre.google/sre-book/managing-incidents](https://sre.google/sre-book/managing-incidents/) | How on-call teams run an incident | Go deeper |
| **Capstone 3 extension: Gil Tene, How NOT to measure latency**<br>[infoq.com/presentations/latency-response-time](https://www.infoq.com/presentations/latency-response-time/) | Percentiles and coordinated omission, for the performance-regression extension | Go deeper |
| **Capstone 4: SWE-bench**<br>[swebench.com](https://www.swebench.com) | How code-fixing agents are measured | Go deeper |
| **Capstone 5: Anthropic, multi-agent research system**<br>[anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system) | The design this capstone is modeled on | Go deeper |
| **Capstone 6: Anthropic, Effective harnesses for long-running agents**<br>[anthropic.com/engineering/effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Progress files, feature lists and git checkpoints for agents that work across many sessions | Start here |
| **Capstone 6: Playwright for Python**<br>[playwright.dev/python](https://playwright.dev/python/) | The browser automation library the computer-use agent drives | Go deeper |
| **Capstone 7: Palantir, A Day in the Life of a Forward Deployed Software Engineer**<br>[blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1) | What the work around Capstone 7 looks like at a customer | Go deeper |
