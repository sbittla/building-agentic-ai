import csv
import json


def make_sample(path="expenses.csv"):
    """Writes a small CSV with a few bad rows. Make yours bigger (30+ rows)."""
    rows = [["date", "category", "amount"],
            ["2026-01-05", "food", "12.50"], ["2026-01-09", "travel", "80"],
            ["2026-02-02", "food", "7.25"], ["2026-02-10", "books", ""],       # missing amount
            ["2026-02-11", "fun", "twelve"],                                    # not a number
            ["not-a-date", "books", "10"]]                                      # bad date
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    return path


def report(csv_path="expenses.csv", out_path="expense_report.json") -> dict:
    """Return and save {"per_category": {...}, "per_month": {"2026-01": ...},
    "total": ..., "skipped_rows": n}. Skip (and count) rows with a missing or
    non-numeric amount or a date that doesn't start with YYYY-MM. Never crash."""
    # TODO: csv.DictReader(open(csv_path, newline="")) gives each row as a dict
    raise NotImplementedError


if __name__ == "__main__":
    make_sample()
    print(json.dumps(report(), indent=2))
