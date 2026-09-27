"""Exercise 16.8 (solution): the Chapter 11 research team, with isolated briefs.

Each worker gets only its subtask plus the library passages retrieved for it (at most 600
tokens, via isolated_brief) and answers in one call, instead of exploring with tools and
carrying its whole transcript. The lead is unchanged. Compare tokens and answers."""
import asyncio
import sys

import ch11_research_team as team
import ch18_rag as rag
from ch16_assemble import ContextItem, isolated_brief

async def briefed_subagent(task: str) -> str:
    hits = rag._index.search(task, k=4)
    items = [ContextItem("library", h["text"], priority=90 - i * 10,
                         origin=f"{h['source']}:{h['line']}") for i, h in enumerate(hits)]
    brief = isolated_brief(task, items, budget=600)
    r = await team._call(system="You are a research assistant. Use only the context you're "
                                "given. Answer in at most 150 words; cite origins in parentheses.",
                         messages=[{"role": "user", "content": brief}])
    return "".join(b.text for b in r.content if b.type == "text")

async def compare(question: str) -> dict:
    rows = {}
    for name, worker in (("original", team.run_subagent), ("briefed", briefed_subagent)):
        for k in team.usage:
            team.usage[k] = 0
        original = team.run_subagent
        team.run_subagent = worker                     # research() calls run_subagent
        try:
            answer = await team.research(question)
        finally:
            team.run_subagent = original
        rows[name] = {**team.usage, "citations": answer.count("("), "answer": answer}
    return rows

QUESTIONS = [
    "Compare agentic search and RAG for our internal docs: cost, freshness, and exact error codes.",
    "What are the main causes of latency in agent loops, and how do we reduce them?",
    "When should we use hybrid retrieval instead of keyword search?",
]

def main(questions=QUESTIONS):
    rag.build(roots=("library",))
    table = []
    for q in questions:
        rows = asyncio.run(compare(q))
        for name, r in rows.items():
            table.append((q[:40], name, r["input_tokens"], r["output_tokens"], r["calls"],
                          r["citations"]))
    print(f"{'question':<42}{'version':<10}{'input':>8}{'output':>8}{'calls':>7}{'cites':>7}")
    for row in table:
        print(f"{row[0]:<42}{row[1]:<10}{row[2]:>8}{row[3]:>8}{row[4]:>7}{row[5]:>7}")
    return table

if __name__ == "__main__":
    main(QUESTIONS[:1] if "--one" in sys.argv else QUESTIONS)
