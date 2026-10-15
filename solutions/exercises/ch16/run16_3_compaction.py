"""Exercise 16.3, run end to end: the chapter's three questions with a context budget this
model's context actually crosses, printing the context size before each call, so a trim or
compaction happens and the third answer still uses facts from the first two."""
import ch06_notes_tools as notes
import ch16_context as c

BUDGET = 450        # tokens: this run peaks near 600; the book's 3,000 assumes Claude's larger results

if __name__ == "__main__":
    history, totals = [], {"trims": 0, "compactions": 0}
    for q in ["Which notes mention Kafka?",
              "What was the root cause of the lag incident?",
              "And what follow-up did we agree?"]:
        size = c.estimate_tokens(history + [{"role": "user", "content": q}],
                                 notes.SYSTEM, notes.TOOLS)
        print(f"\ncontext before the call: ~{size} tokens (budget {BUDGET})")
        answer, history, stats = c.run_managed_agent(q, notes.TOOLS, notes.run_tool,
                                                     system=notes.SYSTEM, messages=history,
                                                     budget_tokens=BUDGET)
        totals["trims"] += stats["trims"]
        totals["compactions"] += stats["compactions"]
        print(f"Q: {q}\nA: {answer}\n{stats}")
    print(f"\ntotal trims {totals['trims']}, compactions {totals['compactions']}")
