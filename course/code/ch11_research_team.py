"""Chapter 11: a lead agent that plans, runs parallel subagents, and synthesizes."""
import asyncio
import json
import os
import re
import time
import httpx
from anthropic import AsyncAnthropic
import ch06_notes_tools as notes
from ch04_agent import next_action
from ch11_web import fetch_url          # https only, no private addresses, every redirect checked

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = AsyncAnthropic()
usage = {"input_tokens": 0, "output_tokens": 0, "calls": 0}

# ---------- tools for the SUBAGENTS: a local library + fetching web pages ----------
notes.ROOT = notes.Path("library").resolve()   # reuse chapter 6 tools on a new folder

SUB_REGISTRY = {**notes.REGISTRY, "fetch_url": fetch_url}
SUB_TOOLS = notes.TOOLS + [{
    "name": "fetch_url", "description": "Fetch an https web page's text (first "
    "4,000 characters). Use only for URLs you were given or found in the library.",
    "input_schema": {"type": "object", "properties": {"url": {"type": "string"}},
                     "required": ["url"]}}]

async def _call(**kwargs):
    r = await client.messages.create(model=MODEL, max_tokens=4096, **kwargs)
    usage["input_tokens"] += r.usage.input_tokens
    usage["output_tokens"] += r.usage.output_tokens
    usage["calls"] += 1
    return r

async def run_subagent(task: str, max_iterations: int = 6) -> str:
    """The chapter 4 loop, async. Tools run in threads so subagents overlap."""
    messages = [{"role": "user", "content": task}]
    system = ("You are a research assistant. Investigate ONLY the task given. "
              "Return 3-6 bullet findings, each with a source (file:line or URL).")
    for _ in range(max_iterations):
        r = await _call(system=system, tools=SUB_TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": r.content})
        action, note = next_action(r)
        if action == "done":
            return "".join(b.text for b in r.content if b.type == "text")
        if action == "stop":
            return f"Subagent stopped: {note}"
        if action == "continue":
            continue
        results = []
        for b in r.content:
            if b.type == "tool_use":
                try:
                    out = await asyncio.to_thread(SUB_REGISTRY[b.name], **b.input)
                except Exception as e:
                    out = f"ERROR: {e}"
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "content": str(out)})
        messages.append({"role": "user", "content": results})
    return "Subagent stopped at its iteration limit."

# ---------- the LEAD agent: plan -> delegate in parallel -> synthesize ----------
PLAN_TOOL = {"name": "make_plan", "description": "Split the question into 2-4 "
             "independent sub-questions that can be researched in parallel.",
             "input_schema": {"type": "object", "properties": {"subtasks": {
                 "type": "array", "items": {"type": "string"},
                 "minItems": 2, "maxItems": 4}}, "required": ["subtasks"]}}

async def research(question: str) -> str:
    t0 = time.perf_counter()
    plan = await _call(tools=[PLAN_TOOL],                       # forced tool =
                       tool_choice={"type": "tool", "name": "make_plan"},  # structured
                       messages=[{"role": "user", "content": question}])  # output
    subtasks = next(b.input["subtasks"] for b in plan.content if b.type == "tool_use")
    print("PLAN:", json.dumps(subtasks, indent=2))

    findings = await asyncio.gather(*(run_subagent(t) for t in subtasks))

    report = "\n\n".join(f"## Sub-question: {t}\n{f}" for t, f in zip(subtasks, findings))
    final = await _call(messages=[{"role": "user", "content":
        f"Question: {question}\n\nFindings from your research team:\n{report}\n\n"
        "Write a concise answer. Keep every source citation. Point out any "
        "disagreements between findings."}])
    print(f"\n[{time.perf_counter() - t0:.1f}s, {usage}]")
    return "".join(b.text for b in final.content if b.type == "text")

if __name__ == "__main__":
    print(asyncio.run(research(
        "Compare agentic search and RAG for our internal docs: cost, freshness, "
        "and accuracy on exact error codes.")))
