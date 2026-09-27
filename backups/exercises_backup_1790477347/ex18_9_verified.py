"""Exercise 18.9 (solution): two more checks in verify(), plus one revision round.

  * a quotation ("...") must appear word for word in the cited evidence
  * a sentence must share at least one key word with the evidence it cites"""
import re

import ch18_agentic as ka
from ch04_agent import MODEL, get_client

STOP = set("the a an and or of to in on for with was were is are it this that by as at from be "
           "has have had not but which what when who how".split())

def _cited_text(sentence: str, evidence: list[dict]) -> str:
    cites = ka.CITATION.findall(sentence)
    return " ".join(e["text"] for e in evidence
                    if any(e["origin"].startswith(c) or c.startswith(e["origin"][:40]) for c in cites))

def verify_plus(answer: str, evidence: list[dict]) -> list[str]:
    problems = ka.verify(answer, evidence)
    for sentence in re.split(r"(?<=[.!?])\s+", answer.strip()):
        text = _cited_text(sentence, evidence)
        if not text:
            continue
        for quote in re.findall(r'"([^"]{8,})"', sentence):
            if quote.lower() not in text.lower():
                problems.append(f"quotation not in the cited evidence: {quote[:50]}")
        words = {w for w in re.findall(r"[a-z]{4,}", ka.CITATION.sub("", sentence).lower())} - STOP
        if words and not any(w in text.lower() for w in words):
            problems.append(f"cited source doesn't support the sentence: {sentence[:60]}")
    return problems

def answer_verified(question: str, max_rounds: int = 2) -> dict:
    result = ka.answer(question, max_rounds=max_rounds, verbose=False)
    result["problems"] = verify_plus(result["answer"], result["evidence"])
    result["revised"] = False
    if result["problems"]:
        shown = "\n\n".join(f"({e['origin']}) {e['text'][:800]}" for e in result["evidence"])
        reply = get_client().messages.create(
            model=MODEL, max_tokens=2000,
            system="Revise the answer so that every problem listed is fixed. Use only the "
                   "evidence; cite origins in parentheses; drop anything you can't support.",
            messages=[{"role": "user", "content": f"Question: {question}\n\nEvidence:\n{shown}\n\n"
                       f"Answer:\n{result['answer']}\n\nProblems:\n" + "\n".join(result["problems"])}])
        result["answer"] = "".join(b.text for b in reply.content if b.type == "text").strip()
        result["problems"] = verify_plus(result["answer"], result["evidence"])
        result["revised"] = True
    result["verified"] = not result["problems"]
    return result

if __name__ == "__main__":
    import ch18_rag as rag
    from ex18_8_know_when_to_stop import CASES
    rag.build()
    before = after = 0
    for q, _ in CASES:
        first = ka.answer(q, verbose=False)
        before += not verify_plus(first["answer"], first["evidence"])
        after += answer_verified(q)["verified"]
    print(f"verified before revision: {before}/{len(CASES)}, after: {after}/{len(CASES)}")
