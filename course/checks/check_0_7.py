import csv, json

def test_report(ex, tmp_path):
    rows = [["date", "category", "amount"], ["2026-01-05", "food", "10"], ["2026-01-20", "food", "5.5"],
            ["2026-02-01", "travel", "100"], ["2026-02-03", "books", ""], ["2026-02-04", "fun", "twelve"],
            ["bad-date", "books", "3"]]
    src, out = tmp_path / "e.csv", tmp_path / "r.json"
    with open(src, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    r = ex.report(str(src), str(out))
    assert r["skipped_rows"] == 3, "3 bad rows: missing amount, not a number, bad date"
    assert r["per_category"] == {"food": 15.5, "travel": 100.0}
    assert r["per_month"] == {"2026-01": 15.5, "2026-02": 100.0}
    assert json.loads(out.read_text())["skipped_rows"] == 3, "the report must also be saved as JSON"
