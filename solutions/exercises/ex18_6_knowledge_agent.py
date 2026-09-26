"""Exercise 18.6 (solution): a cited knowledge agent, evaluated on accuracy,
citation validity and honest refusals."""
import re
from pathlib import Path
import ch18_rag as rag
from ch04_agent import run_agent

SYSTEM = rag.SYSTEM + (" If the knowledge base does not contain the answer, reply exactly: "
                       "'Not in the knowledge base.' and nothing else.")
REFUSAL = "not in the knowledge base"

CASES = [  # question, words the answer must contain (empty = must refuse)
    ("What was the root cause of the Kafka lag incident?", ["12", "4"]),
    ("What p95 did the search load test reach?", ["240"]),
    ("When is the production Kafka upgrade?", ["August 5"]),
    ("How fast must the primary on-call answer pages?", ["15"]),
    ("What did the latency review decide about fraud checks?", ["asynchronous"]),
    ("Which transports does MCP define?", ["stdio", "Streamable HTTP"]),
    ("What is the router admin address?", ["192.168.1.1"]),
    ("What is our AWS monthly bill?", []),
    ("Who won the 2026 football world cup?", []),
    ("What is the Wi-Fi password?", []),              # deliberately NOT in the notes
]

CITATION = re.compile(r"\(([\w./-]+\.\w+):(\d+)\)")
STOP = set("the a an and or of to in on for is was with it at by from as that this be are were "
           "we our what".split())

def _words(s):
    return {w for w in re.findall(r"[a-z0-9][a-z0-9.-]*", s.lower()) if w not in STOP}

def check_citations(answer: str) -> tuple[int, int]:
    """(valid, total). A citation is valid if the file exists, the line exists, and the
    cited chunk (that line and the few after it) shares a key word with the sentence."""
    valid = total = 0
    previous = ""
    for sentence in re.split(r"(?<=[.!?])\s+", answer):
        claim = CITATION.sub("", sentence)
        if not _words(claim):                 # "Fact. (file:3)": the citation belongs to "Fact."
            claim = previous
        previous = claim
        for path, n in CITATION.findall(sentence):
            total += 1
            f = Path(path)
            if not f.exists():
                continue
            lines = f.read_text(errors="ignore").splitlines()
            n = int(n)
            if 1 <= n <= len(lines) and _words(claim) & _words(
                    " ".join(lines[n - 1:n + 8])):
                valid += 1
    return valid, total

def grade(question, must, answer):
    refused = REFUSAL in answer.lower()
    if not must:
        return {"ok": refused, "kind": "refusal"}
    ok = not refused and all(m.lower() in answer.lower() for m in must)
    return {"ok": ok, "kind": "answer"}

def main(cases=CASES):
    rag.build()
    rows, cit_valid, cit_total = [], 0, 0
    for q, must in cases:
        answer, _, stats = rag_answer(q)
        g = grade(q, must, answer)
        v, t = check_citations(answer)
        cit_valid, cit_total = cit_valid + v, cit_total + t
        if g["kind"] == "answer" and t == 0:
            g["ok"] = False                                  # an uncited answer fails
        rows.append({"q": q, **g, "citations": f"{v}/{t}", "answer": answer[:120]})
        print(f"{'PASS' if g['ok'] else 'FAIL'}  {q}  [{v}/{t} citations valid]")
    answers = [r for r in rows if r["kind"] == "answer"]
    refusals = [r for r in rows if r["kind"] == "refusal"]
    summary = {"answer_accuracy": f"{sum(r['ok'] for r in answers)}/{len(answers)}",
               "correct_refusals": f"{sum(r['ok'] for r in refusals)}/{len(refusals)}",
               "citation_validity": f"{cit_valid}/{cit_total}"}
    print(summary)
    return rows, summary

def rag_answer(q):
    return run_agent(q, rag.TOOLS, rag.run_tool, system=SYSTEM, verbose=False)

if __name__ == "__main__":
    main()
