# Version matrix

Which book, code, environment and models belong together, and what the book was tested against. Every version here is pinned by a file in this repository, and `dev/check_references.py` fails CI if a version or price in this file differs from `requirements.lock`, the `Dockerfile` or `PRICES` in the code.

## Release

| Book | Repository tag | Exercises | Capstones | Python | Default models | MCP specification | Main libraries | Verified |
| --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| First edition (2026) | `book-v1.0.0` | 249 | 7 | 3.12 | `claude-sonnet-5`, `claude-haiku-4-5`, `qwen3.5:9b` | 2026-07-28 | `anthropic` 1.8.0, `mcp` 2.2.0, `claude-agent-sdk` 0.2.159, `langchain` 1.4.2, `a2a-sdk` 1.1.5 | See [RELEASE_MANIFEST.json](RELEASE_MANIFEST.json) and "What verified means" below |

ISBNs of the First edition: paperback 979-8177506326, hardcover 979-8177514734.

**Release status.** `book-v1.0.0` is **not published yet**. The current release candidate is `book-v1.0.0-rc4`, matching the RC4 manuscript; its deterministic suite ran on commit `cf2a8a4`, and the tag may sit on a later commit that changes only documentation (`release_manifest.py --check` fails otherwise). The final tag goes on the same code once every `open_gates` entry in [RELEASE_MANIFEST.json](RELEASE_MANIFEST.json) is closed. `book-v1.0.0-rc1` and `-rc2` are earlier candidates whose verification no longer applies.

**Development history.** This repository was developed through several internal manuscript and code snapshots before the book's first public edition. The historical tags `edition-1.0`, `edition-1.1` and `edition-1.2` are kept for traceability. They are development snapshots, not earlier commercial printings, and nothing in the book refers to them.

How to tell which you have:
- **The book:** the copyright page names the edition and the repository tag (`book-v1.0.0`).
- **The code:** `git describe --tags` prints the tag; `./course.sh check` prints the Python and library versions inside the image.
- **The environment:** the Docker image is built from this tag's `Dockerfile` and `requirements.lock`. Every run summary records the commit and the lock file's hash (`provenance`).
- **The results:** `verification/offline.json` names the commit it was run on, and `RELEASE_MANIFEST.json` names the tag, commit, lock hash and test status together.

The book makes one promise: `git checkout book-v1.0.0` gives you the code, data and solutions it was written against, with the versions below. The two runtime images that come from other publishers (the GitHub MCP server and Ollama) are pinned by digest too, so the promise covers them as long as their registries keep serving those digests. Tags never move. Fixes go on `main` and into patch releases such as `book-v1.0.1`, with notes in [CHANGELOG.md](CHANGELOG.md). Mistakes in the printed text are listed in [ERRATA.md](ERRATA.md).

### What "verified" means

The repository provides three different kinds of evidence. Keep them apart.

| Kind of evidence | What it proves | What it doesn't | Where it is |
| --- | --- | --- | --- |
| **Deterministic tests** with a scripted stand-in model | Every code path, control and checker behaves as the book says. The tests are offline and give the same result on any machine, and the security tests use a model that obeys the attacker completely | How well a real model chooses tools or answers | `verification/offline.json`, `verification/README.md` (`python dev/verify.py run`) |
| **Live-model exercise runs**, on the free local model or the paid Claude API | Each exercise works end to end with a real model on the recorded date | That it always will: answers vary from run to run and between models | `solutions/outputs/*/summary.json` and logs (`./course.sh run-chapter`), summarized in README "Verified results" |
| **Production readiness** | Not provided by this kit | — | Needs your own evaluation suite, load test, security review and operations; see Appendix M of the book and [SECURITY_MODEL.md](SECURITY_MODEL.md) |

"Passed" in a deterministic test, "passed" in a live-model run and "ready for production" are three different claims. This repository makes only the first two, and for each one it says which commit and environment the claim covers.

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
| GitHub MCP server | v1.12.2 (`sha256:508a0857…`) | `Dockerfile` and `compose.yaml` (`GITHUB_MCP_IMAGE`) |
| Ollama (local model server) | 0.34.4 (`sha256:8262851b…`) | `compose.yaml` |

> [!WARNING]
> **Two images come from other publishers.** The GitHub MCP server and Ollama are pinned to the versions the release was tested with, by tag and digest (checked 15 October 2026: the digests match the images used for the recorded runs). A publisher can still delete an old image, and newer versions won't reach you until you change the pin.

| Image | What depends on it | If it changes or is unavailable |
| --- | --- | --- |
| `ghcr.io/github/github-mcp-server:v1.12.2` | Exercises 14.3 and 14.4 and Capstone 4. Nothing else uses it | Build without it: put `GITHUB_MCP_IMAGE=nogithub` in `.env` (or pass `--build-arg GITHUB_MCP_IMAGE=nogithub`). The `nogithub` stage in the `Dockerfile` builds an image without the GitHub server, and every other exercise runs unchanged |
| `ollama/ollama:0.34.4` (`compose.yaml`; `compose.gpu.yaml` adds the GPU to the same service) | The free local model (`PROVIDER=local`, Appendix H), through its Anthropic-compatible `/v1/messages` endpoint (plus `/api/tags` and `/api/pull` to check and download the model) | Use the Claude API (`PROVIDER=claude`), which needs no local image, or pin another version you have tested |

Both publishers ship fixes often and the book uses only their stable surface, so a newer version usually works. To move to one, find its digest and test it:

```bash
docker pull ghcr.io/github/github-mcp-server:latest
docker inspect --format '{{index .RepoDigests 0}}' ghcr.io/github/github-mcp-server:latest
# put the result in .env (it overrides the pin):  GITHUB_MCP_IMAGE=ghcr.io/github/github-mcp-server@sha256:...

docker pull ollama/ollama:latest
docker inspect --format '{{index .RepoDigests 0}}' ollama/ollama:latest
# replace the ollama/ollama image in compose.yaml with ollama/ollama@sha256:...
```

Then rebuild and run the checks under "Upgrading the pinned versions". The release's verification (`verification/offline.json`) runs without either image: the GitHub exercises need a personal token and aren't part of it, and the deterministic suite never calls the local model.

## Models and prices

| Model | Where | Price at release (per million tokens, input / output) |
| --- | --- | --- |
| `claude-sonnet-5` | Default `MODEL` (`Dockerfile`, `.env`) | $2.00 / $10.00 |
| `claude-haiku-4-5` | The small model in Chapters 20 and 29 | $1.00 / $5.00 |
| `qwen3.5:9b` | The free local model (Appendix H) | free |

Prices live in one place, `PRICES` in `course/code/ch20/ch20_router.py`, which Chapters 20 and 29 and Appendix E use.

**Model lifecycle (checked 14 October 2026)** against Anthropic's deprecations page ([platform.claude.com/docs/en/about-claude/model-deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)). Both Claude models are the ones the recorded tests used, and both are still active:

| Model | Status | Tentative retirement | Newer model in the same tier |
| --- | --- | --- | --- |
| Claude Sonnet 5 (`claude-sonnet-5`) | Active (legacy: a newer Sonnet exists) | Not sooner than 30 June 2027 | `claude-sonnet-5-5`, same price |
| Claude Haiku 4.5 (`claude-haiku-4-5`) | Active | Not sooner than 15 October 2026 | `claude-haiku-5-5`, $0.10 / $0.50 |

Anthropic gives at least 60 days' notice before it retires a model. If `claude-haiku-4-5` is deprecated, set `MODEL` (or the small model in `PRICES`) to `claude-haiku-5-5`. That replacement **has not been tested** with this release. It thinks by default and its effort default is `medium`, so rerun Chapters 20 and 29 and `python dev/cost_model.py --check` after switching. Any change to the default model goes into `CHANGELOG.md` and a patch release.

**Evidence for the First edition.** On 8 October 2026 the model ids and prices above were checked against Anthropic's pricing page ([platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing)): Claude Sonnet 5 at $2 / $10 and Claude Haiku 4.5 at $1 / $5 per million tokens, matching `PRICES`. `dev/check_references.py` fails CI if this file, the `Dockerfile` and `PRICES` disagree, and `dev/cost_model.py --check` fails if Appendix E's cost figures are stale. Model ids and prices change more often than anything else in this file; check the Claude docs' models overview before changing `MODEL`.

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
