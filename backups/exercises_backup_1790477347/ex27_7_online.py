"""Exercise 27.7 (solution): a simulated week of production. Sample flagged runs and
10% of the rest each day, grade the sample, and check the daily rates for drift."""
import random

from ch27_trajectory import drift, sample_for_review

def simulate_day(day: int, runs: int = 200, good: float = 0.92, bad: float = 0.70,
                 drop_day: int = 6, seed: int = 0) -> list[dict]:
    rng = random.Random(seed * 100 + day)
    p = bad if day >= drop_day else good
    out = []
    for i in range(runs):
        ok = rng.random() < p
        out.append({"day": day, "id": i, "ok": ok,
                    "flagged": (not ok) and rng.random() < 0.3})   # some failures flagged
    return out

def graded_rate(sample: list[dict]) -> float:
    """Flagged runs are graded but not counted in the rate: they'd bias it."""
    unbiased = [r for r in sample if not r["flagged"]]
    return sum(r["ok"] for r in unbiased) / len(unbiased) if unbiased else 1.0

def main(days: int = 14, drop_day: int = 12, rate: float = 0.10, window: int = 7):
    daily, alerts = [], []
    for day in range(1, days + 1):
        sample = sample_for_review(simulate_day(day, drop_day=drop_day), rate=rate,
                                   seed=day)
        daily.append(graded_rate(sample))
        if drift(daily, window=window, drop=0.1):
            alerts.append(day)
        print(f"day {day:>2}: sample {len(sample):>3}, pass rate {daily[-1]:.0%}"
              + ("  DRIFT" if day in alerts else ""))
    return daily, alerts

if __name__ == "__main__":
    main()
