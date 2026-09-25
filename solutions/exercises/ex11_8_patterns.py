"""Exercise 11.8: one pattern per job, with the cost of each in model calls.

(a) support inbox -> ROUTER: one cheap choice, then one specialist.
(b) weekly report against a style guide -> EVALUATOR-OPTIMIZER: a stated quality bar.
(c) five reviews -> VOTING per review: a judgment call where one run can wobble.
(d) data answer -> slide note -> HANDOFF: two stages with different tools."""
import ch11_patterns as p

REVIEWS = ["Arrived fast, works great.", "It's a chair.", "Broke after two days, refund please.",
           "Fine, but the box was damaged.", "Best desk I've owned!"]

def main(verbose=False):
    results = {}
    choice, answer = p.route("My order 1042 hasn't arrived. Can you check when it shipped?")
    results["a router"] = {"route": choice["specialist"], "model_calls": "1 + the specialist's loop"}
    text, history = p.refine("Write a four-line weekly sales update. Style guide: numbers first, "
                             "no adjectives like 'great', end with one action item.")
    results["b evaluator-optimizer"] = {"reviews": len(history), "model_calls": 1 + 2 * len(history) - 1}
    labels = [p.vote(f"Classify this review: {r}", ["positive", "neutral", "negative"], n=3)[0]
              for r in REVIEWS]
    results["c voting"] = {"labels": labels, "model_calls": 3 * len(REVIEWS)}
    findings, summary = p.handoff("How many orders were shipped, and what was the total revenue?")
    results["d handoff"] = {"facts": len(findings["facts"]), "summary": summary,
                            "model_calls": "analyst loop + 2"}
    for job, row in results.items():
        print(f"{job:<24} {row}")
    return results

if __name__ == "__main__":
    main()
