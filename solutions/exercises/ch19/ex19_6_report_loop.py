"""Exercise 19.6 (solution): run harness sessions until the report is finished, one
item needs a person, or the session limit is reached. A crash between sessions loses
nothing, and a final check recomputes the cancellation share with our own SQL."""
import re
import sqlite3

import ch19_harness as h

def true_cancel_share() -> float:
    con = sqlite3.connect("shop.db")
    total, cancelled = con.execute("SELECT COUNT(*), SUM(status='cancelled') "
                                   "FROM orders").fetchone()
    return 100 * cancelled / total

def cross_check(tolerance: float = 0.5) -> tuple[bool, str]:
    """The report's percentage must match the database, whatever the model wrote."""
    path = h.FEATURES.parent / "cancellations.md"
    if not path.exists():
        return False, "cancellations.md is missing"
    shares = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*%", path.read_text())]
    truth = true_cancel_share()
    ok = any(abs(s - truth) <= tolerance for s in shares)
    return ok, f"report says {shares}, database says {truth:.1f}%"

def main(max_sessions: int = 10, crash_after_session: int = 1, verbose=False):
    history = []
    for n in range(1, max_sessions + 1):
        result = h.session(verbose=verbose)
        history.append(result)
        if n == crash_after_session:
            h.note("(the process crashed here; the next session starts from the files)")
        if result["done"] or result["needs_human"] or not result["left"]:
            break
    ok, why = cross_check()
    h.note(f"cross-check: {'ok' if ok else 'FAILED'} ({why})")
    return history, ok, why

if __name__ == "__main__":
    history, ok, why = main(verbose=True)
    print(h.PROGRESS.read_text())
