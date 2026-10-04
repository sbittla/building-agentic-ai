"""Dev tool: write solutions/SOLUTIONS.md, an index of every exercise's solution and what
it shows, from solutions/index.json, course/exercises.json and each file's docstring.
Safe to rerun.   python dev/solution_tables.py <md folder>"""
import ast
import json
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
MD = Path(sys.argv[1])
INDEX = json.loads((KIT / "solutions/index.json").read_text())
EX = json.loads((KIT / "course/exercises.json").read_text())

KEY = {  # one line: what the solution shows. Used where a file's docstring isn't specific.
 # chapter 0 and interludes
 "0.1": "A command's journey: wrapper script, image, container, workspace volume, clean-up",
 "0.2": "Required fields, types and ranges; extra fields are allowed unless the schema forbids them",
 "0.3": "The workspace folder is shared both ways between your computer and the container",
 "T.1": "A failing test names the broken function and shows the wrong value",
 "P.1": "Filtered lists and dictionaries in one line, and totals with dict.get",
 "P.2": "Look a function up by name, call it with **args, and turn any failure into text",
 "P.3": "A class holding dataclass objects, with ids and no shared state",
 "P.4": "A decorator that registers a function, and one that wraps it (functools.wraps)",
 "P.5": "Mutable defaults, off-by-one ranges and swallowed errors",
 # chapter 1
 "1.1": "Could you draw the flowchart in advance? Then it's a workflow, not an agent",
 "1.2": "Resending history makes total input grow quadratically with turns (47,500 tokens)",
 "1.4": "Each failure maps to a missing tool: a clock, a calculator, a file reader",
 "1.7": "Name the tools, the risks and the cost before choosing an agent",
 # chapter 2
 "2.1": "Tool results are sent as role user; only the model writes assistant messages",
 "2.2": "Never eval model input: the safe calculator rejects calls and attributes, but huge powers still need a cap",
 "2.5": "Return errors as tool results with is_error, so the model can recover",
 # chapter 3
 "3.1": "Merge overlapping tools and write descriptions that say when to use each",
 "3.2": "auto, any, a named tool or none: pick by how much freedom the model needs",
 "3.3": "A new tool needs the function, the registry entry and a schema with an enum",
 # chapter 4
 "4.1": "Two tool round-trips, then an answer: every tool_use is followed by its tool_result",
 "4.2": "Multi-step questions show two or more tool calls in the trace",
 # chapter 5
 "5.1": "Only what's written to disk survives; the conversation doesn't",
 "5.2": "Retrying a tool call must not duplicate or damage data",
 "5.3": "State in tasks.json survives restarts; the chat history doesn't",
 "5.4": "Delete and rename tools that address tasks by id",
 "5.5": "An overdue filter computed in code, not guessed by the model",
 "5.6": "When two items match, the agent asks instead of guessing",
 # chapter 6
 "6.1": "Path checks must resolve the real path; test ../, absolute paths and symlinks",
 "6.2": "Answers cite (file:line), and unanswerable questions say so",
 # chapter 7
 "7.1": "Every failure mode needs a planned response: retry, explain or stop",
 "7.2": "Cache by how fast the data changes and how costly a stale answer is",
 "7.3": "The packing list must follow the forecast numbers in the trace",
 # chapter 8
 "8.1": "A read-only connection is enforced by the database; a prompt is only a request",
 "8.2": "Write definitions (revenue, active customer) the agent must follow",
 "8.3": "Check the agent's numbers with your own SQL: Customer 13, 19,238",
 "8.5": "A retry budget and a query log for the SQL tool",
 "8.6": "Confirm the tables with the user before running an expensive query",
 # chapter 9
 "9.1": "Auto-approve reads and reversible steps, approve risky ones, forbid destructive ones",
 "9.2": "Even if the model is fooled, the approval gate in code still stops apply_plan",
 "9.3": "Plan first; declining changes nothing",
 "9.4": "Every applied plan can be undone from its log",
 "9.5": "Approve some moves and reject others in one plan",
 "9.6": "A policy file that blocks risky moves, tested on 200 files",
 # chapter 10
 "10.1": "Every task needs a checkable signal: a reference query, a schema, a measurement",
 "10.2": "Agents can game tests (special cases, skipped tests); defend in code",
 "10.3": "Run tests, read, make small edits, rerun until green; never touch the tests",
 "10.6": "Targeted replace_in_file edits instead of rewriting whole files",
 # chapter 11
 "11.1": "Use many agents only for broad, parallel, loosely coupled work",
 "11.2": "Each subtask needs an objective, boundaries, an output format and an effort level",
 "11.3": "Plan, parallel findings, cited synthesis, plus time and tokens",
 "11.4": "Structured subtasks with an effort level that sets each subagent's step budget",
 "11.5": "A critic pass that checks the draft against the findings",
 # chapter 12
 "12.1": "Host, client and server: who runs the model and who runs the tools",
 "12.2": "Tools act, resources are read, prompts are templates the user picks",
 "12.3": "Tools, a resource and a prompt, all visible in the Inspector",
 "12.5": "Claude Desktop runs your server through Docker and asks before each call",
 "12.7": "The same server over stdio and Streamable HTTP, tested both ways",
 # chapter 13
 "13.1": "Namespace tools as server__tool so names never collide",
 "13.3": "One question, tools from two servers",
 "13.4": "Read servers' resources at start-up and give them to the model",
 "13.5": "Add a server by configuration only, no host code changes",
 "13.6": "Restart a crashed server, reconnect and retry the call once",
 "13.7": "A resolver asks the user mid-call (elicitation); the host shows the question and fills the answer",
 # chapter 14
 "14.1": "A policy layer in code hides and blocks dangerous tools even if the model is convinced",
 "14.2": "Six questions: publisher, permissions, readable source, pinned version, narrowing, secrets passed",
 "14.3": "A read-only token and --read-only remove write tools entirely",
 # chapter 27
 "27.1": "Cases with deterministic checks, grown from real failures",
 "27.2": "A scorecard read critically: overlapping intervals, a pass^k drop and weak escalation mean not yet",
 "27.3": "Six more SQL cases, each with a check that can fail",
 # chapter 16-19
 "16.1": "Trim tool results first, cache the stable prefix second, compact last",
 "16.2": "Role, tool use, rules, output format and boundaries, each testable",
 "16.3": "Watch trimming or compaction keep a conversation under budget",
 "16.4": "The report explains every inclusion and drop; routing decides which sources are fetched",
 "16.6": "Newest item per origin, failed refreshes reported, max_age enforced, with unit tests",
 "16.8": "Workers get isolated briefs and answer in one call: fewer tokens, same citations",
 "17.1": "Each memory classified by kind, scope, lifetime and store, or not stored at all",
 "17.2": "A one-page memory policy whose rules can be enforced in code",
 "17.4": "Every output line explained: stored, replaced, refused, quarantined, expired or recalled",
 "17.5": "Episodes about one topic become one semantic memory that records its sources",
 "17.6": "Five poisoning attempts, all quarantined by layered defenses",
 "17.7": "Only the lead writes team memory; workers read it and keep private notes",
 "18.7": "A weather source the planner uses only for forecasts",
 "18.8": "Answerable and unanswerable questions scored for one and two search rounds",
 "18.9": "Quotations and wrong-source citations caught, then one revision round",
 "17.3": "Memory survives restarts in memory.db; forget really deletes",
 "18.1": "Chunk size follows the document type; overlap protects boundaries",
 "18.2": "Keyword for exact codes, vectors for meaning, hybrid for both",
 "18.3": "Keyword and vector search disagree; see where and why",
 "18.4": "Recall@3 and MRR for each embedder and search mode",
 "24.1": "Every hand-built part has a framework equivalent",
 "24.2": "Choose by need: minimal loop, full runtime, portability or teaching",
 "24.3": "A DELETE is denied by can_use_tool and the database is unchanged",
 "3.7": "Deferred tools found by search, against loading every tool: accuracy, searches and tokens",
 "25.2": "Each OWASP agentic risk, how it could happen here, the defense in place and the gap to close first",
 "16.7": "Many calls feeding one summary favor a program; step-by-step reasoning favors the plain loop",
 "24.6": "A second skill with a reference file, validated, and a trace showing only the needed skill loads",
 "24.7": "A managed session to completion, and one stopped by a tiny budget",
 "11.7": "Router, evaluator-optimizer, voting and handoff, each matched to a job, with its cost in model calls",
 "13.8": "A coordinator hub that delegates data questions to an analyst agent served over MCP",
 "30.1": "401, 429, 422, 404, 502 and 409, and why each one",
 "30.7": "Build, run and smoke-test the production image, then deploy with secrets and limits",
 "30.2": "Sessions carry context between requests; streaming shows progress",
 "30.3": "Per-key rate limits give 429 with Retry-After; bad keys give 401",
 "30.4": "Stream every model call and forward text as it arrives",
 "19.1": "Each failure matched to checkpoints, retries, keys, leases, escalation, compensation or checks in code",
 "19.2": "Setting a value is idempotent; adding, sending and moving money need a key or a design change",
 "19.3": "A resumed job skips finished steps and reuses their results; deleting the checkpoint repeats everything",
 "20.1": "Plan when the task is long, predictable in shape or costly to get wrong; approve plans for risky bulk work",
 "20.2": "Small models for lookups and formatting, the large model with more effort for the judgement step",
 "21.1": "Supervisor for most systems; pipelines for fixed sequences; A2A networks across companies; a board for many loosely coupled agents",
 "21.2": "A result schema with required sources and dates, numeric prices and a maximum size; a brief with objective, scope and answer form",
 "21.3": "Every board row explained; refused delegations reach the lead as errors it must handle",
 "21.5": "Two agents published with A2A (analyst and to-do keeper), found by their cards and used by one coordinator",
 "22.1": "Judgement on text goes to the model with an evaluation; limits, currency and approvals go to code",
 "22.2": "Amounts and ids from the model, identity in arguments, prompt-only limits: each fixed by a control in code",
 "22.3": "Five requests, five paths; the amount always comes from the order record",
 "23.1": "APIs and exports first; a browser or desktop agent only where nothing else exists",
 "23.2": "Harms from page content and from mistakes, each with a control that holds even if the model is fooled",
 "24.9": "The runtime follows from where state must live, how long work runs, and who operates the infrastructure",
 "25.1": "Each agent's three legs identified; one removed in code or configuration",
 "25.3": "The canary and egress guards block the fetch; sanitizing removes the image channel",
 "26.1": "Three identities per action, minimal scopes, step-up for money and sensitive data",
 "26.2": "A token for one trip: one employee, one audience, capped amount and dates, a short life",
 "28.2": "A span per state transition, redacted text, and an SLO on the reply-guard fallback rate",
 "28.3": "Every report number explained; a failing tool shows up as a failure class and a named alert",
 "29.3": "History and the repeated prefix dominate; caching saves about 30%, routing plus caching about 46%",
 "M.1": "Both 95% intervals overlap (64-95% and 76-99%): not proven better yet",
 "M.2": "About 3,000 runs separate 78% from 80%; a few hundred separate 70% from 80%",
 "M.3": "The SQL analyst measured with three trials per case, before and after one prompt change",
 "15.1": "Each 2026-07-28 protocol change matched to who benefits and the problem it removes",
 "15.2": "Sampling, roots, logging and SSE replaced; per-user state moved to storage keyed by an id",
 "15.3": "Discover, list and call over raw HTTP; a header that disagrees with the body is refused",
 "15.4": "1, 10 and 10 of 10 list requests reach the server",
 "30.8": "Tasks, the gateway and company sign-on matched to who benefits and the problem each removes",
 "30.9": "search_tools filtered by the caller's token scopes",
 "30.10": "A long-polling job_status: one call instead of several; the same request_id gives the same job",
 "30.11": "The Chapter 13 agent behind a stdio gateway: tools found by search, writes allowed, the order query refused and audited",
 "1.8": "Three systems scored on the nine dimensions of agency, with a dimension to turn down for each",
 "27.8": "A ten-dimension scorecard over k trials, used as a CI gate",
 "28.6": "A one-page static dashboard: headline tiles, SLOs met or missed, failure classes, per-tool latency",
 "28.7": "Runs classified with the 12-class taxonomy, printed as failure, detection, mitigation, evaluation",
 "29.6": "A concurrency sweep with the real agent: throughput, goodput, percentiles and the knee",
}

def doc_line(path: Path) -> str:
    try:
        d = ast.get_docstring(ast.parse(path.read_text())) or ""
    except SyntaxError:
        return ""
    line = " ".join(d.split("\n\n")[0].split())
    line = re.sub(r"^(Exercise [\w.]+|Chapter \d+ reference solution)[^:]*:\s*", "", line)
    line = re.sub(r"^Chapters? [\d-]+ reference solutions\.?", "", line).strip()
    return (line[:1].upper() + line[1:]).rstrip(".")

def row(e):
    files = INDEX.get(e["id"]) or (["ANSWERS.md"] if e["kind"] == "concept" else [])
    key = KEY.get(e["id"])
    if not key:
        for f in files:
            if f.endswith(".py") and not f.startswith("tests/test_ch"):
                key = doc_line(KIT / "solutions" / f)
                if key:
                    break
    shown = [f"`{f}`" for f in files if not re.match(r"tests/test_ch\d", f)] or [f"`{files[0]}`"]
    title = e["title"].replace("|", "\\|")
    key = re.sub(r"\bchapter (\d)", r"Chapter \1", (key or "").replace("|", "/")).replace(" — ", ": ")
    key = re.sub(r"\bcapstone (\d)", r"Capstone \1", key)
    return f"| {e['id']} {title} | {', '.join(shown)} | {key} |"

by_chapter = {}
for e in EX:
    by_chapter.setdefault(e["chapter"], []).append(e)

HEAD = "## Solutions for this chapter"
# The book no longer prints these tables: every exercise box names its solution file.
# This script removes any old table from the chapters and writes one browsable index,
# solutions/SOLUTIONS.md, with what each solution shows.
out = ["# Solutions index", "",
       "Try each exercise before you look. `./course.sh solution <id>` prints a solution; "
       "paths are relative to this `solutions` folder. Written answers are in `ANSWERS.md`.", ""]
for md in sorted(MD.glob("[0-9][0-9]*.md")):
    text = md.read_text()
    new = re.sub(rf"\n{re.escape(HEAD)}\n.*?(?=\n## |\Z)", "", text, flags=re.S)
    if new != text:
        md.write_text(new.rstrip() + "\n")
        print(f"{md.name}: old table removed")
order = []
for md in sorted(MD.glob("[0-9][0-9]*.md")):
    m = re.search(r"^# (.+)$", md.read_text(), re.M)
    if m and m.group(1) in by_chapter:
        order.append(m.group(1))
for chapter in order:
    out += [f"## {chapter}", "", "| Exercise | Solution | What it shows |", "| --- | --- | --- |",
            *[row(e) for e in by_chapter[chapter]], ""]
(KIT / "solutions/SOLUTIONS.md").write_text("\n".join(out))
print("wrote solutions/SOLUTIONS.md")
