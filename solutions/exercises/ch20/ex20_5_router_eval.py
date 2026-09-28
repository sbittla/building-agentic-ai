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
    out = [evaluate(by_rules, "rules"), evaluate(by_model, "small model")]
    for r in out:
        print(f"{r['router']:<12} accuracy {r['accuracy']:.0%}, hard tasks sent to "
              f"the small model: {r['hard_sent_small']}")
    # Improving the rules: "which", "find" and "suggest" questions were often hard.
    return out

if __name__ == "__main__":
    main()
