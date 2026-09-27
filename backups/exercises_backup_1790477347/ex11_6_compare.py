"""Exercise 11.6 (Complex): single agent vs research team, scored with a rubric."""
import asyncio
import statistics
import time
import ch06_notes_tools as notes
import ch11_research_team as base
import sol_ch11_research_team as team
from ch04_agent import run_agent, get_client, MODEL

QUESTIONS = [
    "Compare agentic search and RAG on cost and freshness.",
    "What are the main security risks of MCP servers and how do you reduce them?",
    "Why do agents get slow under load, and what helps?",
    "When is a multi-agent system a bad idea?",
    "How should we evaluate an agent before launch?",
]
RUBRIC = {"name": "score", "description": "Score an answer 1-5 on each criterion.",
          "input_schema": {"type": "object", "properties": {
              k: {"type": "integer", "minimum": 1, "maximum": 5}
              for k in ("completeness", "accuracy", "citations")},
              "required": ["completeness", "accuracy", "citations"]}}

def single(q):
    notes.ROOT = notes.Path("library").resolve()
    t0 = time.perf_counter()
    answer, _, s = run_agent(q, notes.TOOLS, notes.run_tool, system=notes.SYSTEM, verbose=False)
    return answer, time.perf_counter() - t0, s["input_tokens"] + s["output_tokens"]

def multi(q):
    before = base.usage["input_tokens"] + base.usage["output_tokens"]
    r = asyncio.run(team.research(q))
    return r["answer"], r["seconds"], base.usage["input_tokens"] + base.usage["output_tokens"] - before

def grade(q, answer):
    r = get_client().messages.create(model=MODEL, max_tokens=2000, tools=[RUBRIC],
                                     tool_choice={"type": "tool", "name": "score"},
                                     messages=[{"role": "user", "content":
                                                f"Question: {q}\n\nAnswer:\n{answer}"}])
    s = next(b.input for b in r.content if b.type == "tool_use")
    return sum(s.values()) / 3

def main():
    rows = []
    for q in QUESTIONS:
        for label, fn in (("single", single), ("team", multi)):
            answer, secs, tokens = fn(q)
            rows.append({"approach": label, "q": q, "score": grade(q, answer),
                         "seconds": secs, "tokens": tokens})
    print("| approach | mean score (1-5) | mean seconds | mean tokens |")
    for label in ("single", "team"):
        rs = [r for r in rows if r["approach"] == label]
        print(f"| {label} | {statistics.mean(r['score'] for r in rs):.2f} | "
              f"{statistics.mean(r['seconds'] for r in rs):.1f} | "
              f"{statistics.mean(r['tokens'] for r in rs):,.0f} |")
    return rows

if __name__ == "__main__":
    main()
