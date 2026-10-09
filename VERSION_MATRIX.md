# Version matrix

Which book, code, environment and models belong together, and what the book was tested against. Every version here is pinned by a file in this repository, and `dev/check_references.py` fails CI if a version or price in this file differs from `requirements.lock`, the `Dockerfile` or `PRICES` in the code.

## Release matrix

Read across one row: a printing of the book, the repository tag that matches it, and what that tag was verified with.

| Book printing | Repository tag | Exercises | Python | Default models | MCP specification | Main libraries | Verified |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| First printing, September 2026 | `edition-1.0` | 231 | 3.12 | `claude-sonnet-5`, `claude-haiku-4-5`, `qwen3.5:9b` | 2026-07-28 | `anthropic` 1.8.0, `mcp` 2.2.0 | September 2026 |
| Second printing, October 2026 | `edition-1.1` | 246 | 3.12 | `claude-sonnet-5`, `claude-haiku-4-5`, `qwen3.5:9b` | 2026-07-28 | `anthropic` 1.8.0, `mcp` 2.2.0, `claude-agent-sdk` 0.2.159, `langchain` 1.4.2, `a2a-sdk` 1.1.5 | 6 October 2026: 569 offline tests passed, 5 need the course image; 12 of 12 security controls caught ([verification/](verification/README.md)) |

| Third printing, October 2026 | `edition-1.2` | 252 | 3.12 | `claude-sonnet-5`, `claude-haiku-4-5`, `qwen3.5:9b` | 2026-07-28 | `anthropic` 1.8.0, `mcp` 2.2.0, `claude-agent-sdk` 0.2.159, `langchain` 1.4.2, `a2a-sdk` 1.1.5 | 9 October 2026: 571 offline tests passed outside the course image (13 skipped there); rerun in the image before tagging |

ISBNs of the second and third printings: paperback 979-8177506326, hardcover 979-8177514734.

How to tell which you have:
- **The book:** the copyright page names its printing and its tag.
- **The code:** `git describe --tags` prints the tag; `./course.sh check` prints the Python and library versions inside the image.
- **The environment:** the Docker image is built from this tag's `Dockerfile` and `requirements.lock`; every run summary records the commit and the lock file's hash (`provenance`).
- **The results:** `verification/offline.json` names the commit it was run on.

The printed book makes one promise: `git checkout edition-1.2` gives you code, data and solutions that run as printed, with the versions below. Tags are never moved. Newer versions go on `main` and into a new tag, with notes in [CHANGELOG.md](CHANGELOG.md) and [MIGRATION.md](MIGRATION.md). Mistakes in the printed text are listed in [ERRATA.md](ERRATA.md).

**Details as of:** 9 October 2026 · **Tag:** `edition-1.2`

## Runtime

| Component | Version | Pinned in |
| --- | --- | --- |
| Base image | Ubuntu 24.04 | `Dockerfile` |
| Python | 3.12 | `Dockerfile`, `dev/update-lock.sh` |
| pip / uv | 26.2.1 / 0.12.18 | `Dockerfile` |
| Node.js | 24.19.0 (`nodejs-wheel-binaries`) | `requirements.lock` |

## Python libraries

Every package, including indirect dependencies, is pinned to an exact version in `requirements.lock`. The ones the book's code calls directly:

| Package | Version | Used in |
| --- | --- | --- |
| `anthropic` | 1.8.0 | Every chapter (Messages API, tool runner, Managed Agents) |
| `mcp` | 2.2.0 | Chapters 12–15, 30 |
| `claude-agent-sdk` | 0.2.159 | Section 24.3 |
| `langchain` / `langchain-core` / `langchain-anthropic` | 1.4.2 / 1.6.5 / 1.7.4 | Section 24.4 |
| `langgraph` | 1.2.12 | Installed with LangChain's agents (section 24.4) |
| `a2a-sdk` | 1.1.5 | Section 21.7 |
| `fastapi` / `starlette` / `uvicorn` | 0.141.1 / 1.7.0 / 0.53.0 | Chapters 21, 23, 30 |
| `pydantic` | 2.13.5 | Chapters 3, 30 |
| `httpx` | 0.28.1 | Chapters 7, 11, 15, 21, 30 |
| `opentelemetry-sdk` | 1.44.0 | Chapter 28 |
| `model2vec` / `voyageai` | 0.9.0 / 0.5.0 | Chapter 18 |
| `playwright` | 1.56.0 | Chapter 23 |
| `numpy` | 2.5.3 | Chapter 18 |
| `pytest` | 9.1.1 | Interlude T, the checkers and the solution tests |

## MCP servers and tools

| Server | Version | Pinned in |
| --- | --- | --- |
| MCP Inspector | 2.8.0 | `Dockerfile` |
| `server-filesystem`, `server-memory` | 2026.8.31 | `Dockerfile` |
| `mcp-server-git`, `mcp-server-fetch`, `mcp-server-time` | 2026.8.18 | `Dockerfile` |
| GitHub MCP server | `latest` at build time (**not pinned**) | `Dockerfile` (`GITHUB_MCP_IMAGE`) |
| Ollama (local model server) | `latest` at pull time (**not pinned**) | `compose.yaml` |

Two images are not pinned, because their publishers ship fixes often and the book uses only their stable surface (exercises 14.3, 14.4 and Capstone 4 for GitHub; the OpenAI-compatible chat endpoint for Ollama). To pin one, replace `latest` with a version tag from the publisher's release page, rebuild and run the checks below.

## Models and prices

| Model | Where | Price at printing (per million tokens, input / output) |
| --- | --- | --- |
| `claude-sonnet-5` | Default `MODEL` (`Dockerfile`, `.env`) | $2.00 / $10.00 |
| `claude-haiku-4-5` | The small model in Chapters 20 and 29 | $1.00 / $5.00 |
| `qwen3.5:9b` | The free local model (Appendix H) | free |

Prices live in one place, `PRICES` in `course/code/ch20/ch20_router.py`, which Chapters 20 and 29 and Appendix E use. Model ids and prices change more often than anything else in this file; check the Claude docs' models overview before changing `MODEL`.

## Protocols

| Protocol | Version the book teaches | Spoken by |
| --- | --- | --- |
| Model Context Protocol | Specification **2026-07-28** (stateless requests, `server/discover`, list cache hints; sampling, roots and logging deprecated) | `mcp` 2.2.0, which also speaks the earlier revisions |
| Agent2Agent (A2A) | The specification that `a2a-sdk` 1.1.5 implements | `a2a-sdk` 1.1.5 |

### Protocol behavior and SDK behavior are different promises

When something breaks after an upgrade, first decide which layer changed, because the fix is different.

| | Protocol (the specification) | SDK (the library) |
| --- | --- | --- |
| What it defines | Messages on the wire: method names, fields, versions, what a server must refuse | Class and function names, defaults, callbacks, how a connection is opened |
| How it changes | New dated revisions; old revisions keep working for a deprecation period, and both sides agree on a version per request | Any release; major versions may rename or remove things |
| Example in this book | Since 2026-07-28 elicitation returns an *input required* result (section 12.8) | `Client(...)` (section 13.4) and `elicitation_callback=` (exercise 13.7) |
| When it changes | The *behavior* of your agent may change: re-read the section and rerun the evaluations | Your *code* may stop running: update the call sites; behavior should be unchanged |
| How the kit catches it | `test_part5_mcp2026.py` checks the protocol version, cache hints and refusals that Chapter 15 describes | The solution tests and checkers fail on import or call errors |

The same split applies to the Claude API (the HTTP API is versioned with the `anthropic-version` header; the Python SDK wraps it) and to A2A.

## Sections that depend on fast-changing details

These sections carry an **API-dependent** note under their heading (Card 9). Their concepts last; their parameter names may not. They are the first places to check after an upgrade:

3.3 `tool_choice` · 3.6 tool search · 4.8 thinking and effort · 12.6 Claude Desktop · 12.8 other MCP features · 15.2 the protocol on the wire · 15.4 extensions · 16.7 prompt caching · 16.8 API-managed context · 16.11 programmatic tool calling · 23.8 desktop computer use · 24.2 the tool runner · 24.3 the Claude Agent SDK · 24.4 LangChain · 24.6 other providers · 24.7 Agent Skills · 24.8 Claude Managed Agents · 30.6 cloud deployment · 30.11 company authorization

## Upgrading the pinned versions

1. `./dev/update-lock.sh` re-resolves `requirements.in` into `requirements.lock`.
2. `./course.sh build`, then `./course.sh selftest` and `./course.sh check-solutions`.
3. `python3 dev/verify.py run` records the results with the commit and the lock file's hash (`verification/`).
4. Update this file's tables and the date, add a CHANGELOG entry, and add a MIGRATION.md entry for anything a reader's code must change.
