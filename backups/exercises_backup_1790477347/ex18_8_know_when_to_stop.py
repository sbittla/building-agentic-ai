"""Exercise 18.8 (solution): answerable and unanswerable questions, one round versus two.
A correct abstention counts as a pass."""
import re

import ch18_agentic as ka
import ch18_rag as rag

CASES = [  # (question, words a correct answer contains, or None if it should abstain)
    ("What caused the consumer lag spike in the Kafka incident?", ["partition"]),
    ("How fast must the primary on-call respond?", ["minute"]),
    ("How many orders were cancelled in total?", ["88"]),
    ("Why did checkout get slower after the May release?", ["fraud"]),
    ("On what date will ZooKeeper be fully removed from production?", None),
    ("What is the office Wi-Fi password?", None),
    ("How many customers live in Tokyo?", ["0"]),
    ("Who approved the Postgres vacuum change?", None),
]
ABSTAIN = re.compile(r"(doesn't|does not|don't|do not|not) (say|mention|contain|include|state)|"
                     r"no (information|record|evidence)|couldn't find|could not find|not in the",
                     re.I)

def grade(answer: str, expected) -> str:
    if expected is None:
        return "abstained" if ABSTAIN.search(answer) else "wrong"
    return "correct" if all(w.lower() in answer.lower() for w in expected) else "wrong"

def main(cases=CASES):
    rag.build()
    table = {}
    for rounds in (1, 2):
        results = [grade(ka.answer(q, max_rounds=rounds, verbose=False)["answer"], exp)
                   for q, exp in cases]
        table[rounds] = {k: results.count(k) for k in ("correct", "abstained", "wrong")}
        print(f"max_rounds={rounds}: {table[rounds]}")
    return table

if __name__ == "__main__":
    main()
