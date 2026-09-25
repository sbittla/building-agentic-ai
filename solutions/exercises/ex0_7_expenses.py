"""Exercise 0.7 (solution): an expense report from a CSV file, robust to bad rows."""
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

def make_sample(path="expenses.csv", rows=36, seed=7):
    rng = random.Random(seed)
    cats = ["food", "travel", "books", "rent", "fun"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "category", "amount"])
        for i in range(rows):
            w.writerow([f"2026-{rng.randint(1, 3):02d}-{rng.randint(1, 28):02d}",
                        rng.choice(cats), f"{rng.uniform(3, 300):.2f}"])
        w.writerow(["2026-02-10", "food", ""])              # missing amount
        w.writerow(["2026-02-11", "fun", "twelve"])          # not a number
        w.writerow(["not-a-date", "books", "10"])            # bad date
    return path

def report(csv_path="expenses.csv", out_path="expense_report.json") -> dict:
    by_cat, by_month, skipped = defaultdict(float), defaultdict(float), 0
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                amount = float(row["amount"])
                month = row["date"][:7]
                if len(month) != 7 or month[4] != "-" or not month.replace("-", "").isdigit():
                    raise ValueError("bad date")
                category = row["category"].strip() or "uncategorized"
            except (ValueError, KeyError, TypeError):
                skipped += 1
                continue
            by_cat[category] += amount
            by_month[month] += amount
    result = {"per_category": {k: round(v, 2) for k, v in sorted(by_cat.items())},
              "per_month": {k: round(v, 2) for k, v in sorted(by_month.items())},
              "total": round(sum(by_cat.values()), 2),
              "skipped_rows": skipped}
    Path(out_path).write_text(json.dumps(result, indent=2))
    return result

def main():
    make_sample()
    print(json.dumps(report(), indent=2))

if __name__ == "__main__":
    main()
