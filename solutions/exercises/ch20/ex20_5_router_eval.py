"""Exercise 20.5 (solution): score two routers against labels you wrote yourself."""
from ch20_router import LARGE, SMALL, by_model, by_rules

LABELLED = [   # (task, "easy" or "hard"): your judgement is the gold standard here
    ("How many customers are there?", "easy"),
    ("List the product categories.", "easy"),
    ("What is the most expensive product?", "easy"),
    ("How many orders are pending?", "easy"),
    ("Which city has the most customers?", "easy"),
    ("What was the total revenue last month?", "easy"),
    ("Why did revenue drop in March compared with February?", "hard"),
    ("Compare repeat customers with one-time customers by average order value.", "hard"),
    ("Which categories grow fastest, and what would you stock more of?", "hard"),
    ("Find customers who ordered in every month and describe what they buy.", "hard"),
    ("Is there a seasonal pattern in cancellations? Explain it.", "hard"),
    ("Suggest three KPIs for this shop and compute each one.", "hard"),
]

def evaluate(route, name):
    rows, correct, hard_to_small = [], 0, 0
    for task, label in LABELLED:
        chose = "hard" if route(task) == LARGE else "easy"
        correct += chose == label
        hard_to_small += label == "hard" and chose == "easy"
        rows.append((task[:50], label, chose))
    return {"router": name, "accuracy": correct / len(LABELLED),
            "hard_sent_small": hard_to_small, "rows": rows}

def main():
    import ch20_router
    out = [evaluate(by_rules, "rules"), evaluate(by_model, "small model")]
    print(f"{'task':<52} {'label':<6} {'rules':<6} {'model':<6}")
    for (task, label, by_r), (_, _, by_m) in zip(out[0]["rows"], out[1]["rows"]):
        print(f"{task:<52} {label:<6} {by_r:<6} {by_m:<6}")
    for r in out:
        print(f"{r['router']:<12} accuracy {r['accuracy']:.0%}, hard tasks sent to "
              f"the small model: {r['hard_sent_small']}")
    # Improving the rules: the hard tasks above ask for reasons, patterns or proposals.
    saved = ch20_router.HARD_WORDS
    ch20_router.HARD_WORDS = saved + ("suggest", "pattern", "every", "fastest", "describe")
    better = evaluate(ch20_router.by_rules, "rules + 5 words")
    ch20_router.HARD_WORDS = saved
    print(f"change: add 'suggest', 'pattern', 'every', 'fastest', 'describe' to HARD_WORDS -> "
          f"rules accuracy {out[0]['accuracy']:.0%} -> {better['accuracy']:.0%}, hard tasks "
          f"sent small {out[0]['hard_sent_small']} -> {better['hard_sent_small']}")
    return out + [better]

if __name__ == "__main__":
    main()
