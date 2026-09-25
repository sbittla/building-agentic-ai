"""Exercise 6.7 (Complex): agentic search vs 'read everything' on 2,000 notes.

Setup (once):  ./course.sh data notes --count 2000 --out notes_big
The 15 hidden facts are listed in notes_big_answers.txt.
"""
import re
import time
from pathlib import Path
import ch06_notes_tools as notes
from ch04_agent import run_agent, get_client, MODEL

BIG = Path("notes_big")
CONTEXT_BUDGET_CHARS = 400_000          # roughly what fits in one large prompt

def questions():
    facts = Path("notes_big_answers.txt").read_text().splitlines()
    out = []
    for f in facts:
        m = re.match(r"FACT-\d+: the secret code for project (\w) is (\d+)", f)
        out.append((f"What is the secret code for project {m[1]}?", m[2]))
    return out

def agent_answer(q):
    notes.ROOT = BIG.resolve()
    answer, _, s = run_agent(q, notes.TOOLS, notes.run_tool, system=notes.SYSTEM, verbose=False)
    return answer, s["input_tokens"] + s["output_tokens"]

def baseline_answer(q):
    """Paste files into one prompt until the budget is full, then ask."""
    chunks, size = [], 0
    for p in sorted(BIG.rglob("*.md")):
        t = f"## {p.relative_to(BIG)}\n{p.read_text()}"
        if size + len(t) > CONTEXT_BUDGET_CHARS:
            break
        chunks.append(t); size += len(t)
    r = get_client().messages.create(model=MODEL, max_tokens=2000, messages=[
        {"role": "user", "content": "\n".join(chunks) + f"\n\nQuestion: {q}"}])
    return "".join(b.text for b in r.content if b.type == "text"), r.usage.input_tokens + r.usage.output_tokens, len(chunks)

def main(limit=None):
    rows = []
    for q, truth in questions()[:limit]:
        t0 = time.perf_counter(); a, tok_a = agent_answer(q); ta = time.perf_counter() - t0
        t0 = time.perf_counter(); b, tok_b, files = baseline_answer(q); tb = time.perf_counter() - t0
        rows.append((q, truth in a, tok_a, ta, truth in b, tok_b, tb))
    n = len(rows)
    agent_acc = sum(r[1] for r in rows) / n; base_acc = sum(r[4] for r in rows) / n
    print(f"| approach | accuracy | mean tokens | mean seconds |\n"
          f"| agentic search | {agent_acc:.0%} | {sum(r[2] for r in rows) / n:,.0f} | {sum(r[3] for r in rows) / n:.1f} |\n"
          f"| read everything (first {files} files fit) | {base_acc:.0%} | {sum(r[5] for r in rows) / n:,.0f} | {sum(r[6] for r in rows) / n:.1f} |")
    print("Read-everything can only answer facts that happen to be in the files that fit; "
          "agentic search finds any fact with one regex search, at far fewer tokens.")
    return rows

if __name__ == "__main__":
    main()
