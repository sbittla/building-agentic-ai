"""Exercise 17.5 (solution): questions that share almost no words with their answers.
Keyword search struggles here; a semantic embedder (EMBEDDER=local or voyage) should not."""
import ch17_rag as rag

PARAPHRASED = [
    ("Which slowdown was caused by synchronous checks?", "notes/work/2026-05-10-latency-review.md"),
    ("Why did messages pile up waiting to be processed?", "notes/work/2026-06-02-incident-kafka-lag.md"),
    ("Which table had too much wasted disk space?", "notes/work/2026-04-18-postgres-vacuum.md"),
    ("How quickly do I need to react when I'm paged?", "notes/work/2026-08-01-on-call-handbook.md"),
    ("What's the spiced milk tea method?", "notes/personal/recipes.md"),
    ("When am I going home for the festival of lights?", "notes/personal/travel-2026.md"),
    ("How can spending on assistants stay under control?", "library/cost-of-agents.md"),
    ("Is splitting work across several bots good for programming?", "library/multi-agent.md"),
]

def evaluate_set(index, cases, k=3, modes=("keyword", "vector", "hybrid")):
    report = {}
    for mode in modes:
        hits, rr, misses = 0, 0.0, []
        for q, expected in cases:
            ranked = [c["source"] for c in index.search(q, k=20, mode=mode)]
            if expected in ranked[:k]:
                hits += 1
            else:
                misses.append(q)
            rr += 1 / (ranked.index(expected) + 1) if expected in ranked else 0
        report[mode] = {"recall@k": round(hits / len(cases), 2), "mrr": round(rr / len(cases), 2),
                        "misses": misses}
    return report

def main(embedder=None):
    index = rag.build(embedder=embedder)
    print(f"embedder = {index.embedder.name}")
    for name, cases in [("original", rag.EVAL), ("paraphrased", PARAPHRASED)]:
        print(f"\n{name} questions ({len(cases)}):")
        report = evaluate_set(index, cases)
        for mode, r in report.items():
            print(f"  {mode:<8} recall@3 = {r['recall@k']:<5} MRR = {r['mrr']}")
    print("\nWith the hashing embedder, 'vector' is still word-based, so expect little gain;"
          "\nwith EMBEDDER=local, vector and hybrid should beat keyword on the paraphrases.")
    return report

if __name__ == "__main__":
    main()
