"""Exercise 28.6 (solution): a production dashboard. From spans to one HTML page:
run summaries, failure classes, the fleet report, the agent SLOs, and the page.

    ./course.sh python ex28_6_dashboard.py              # the built-in sample
    ./course.sh python ex28_6_dashboard.py spans.jsonl  # your own traces"""
import sys
from collections import Counter

import ch28_agentops as ops
import ch28_ops

def main(path: str | None = None, out: str = "dashboard.html") -> str:
    if path:
        by_trace, evals = ops.load_spans(path), {}  # no evals: those SLOs say n/a
    else:
        by_trace, evals = ch28_ops.sample()
    runs = [ops.summarize(tid, spans) for tid, spans in by_trace.items()]
    passed = [evals.get(r["trace_id"], {}).get("passed") for r in runs]
    rep = ops.report(runs, [ops.classify(r, p) for r, p in zip(runs, passed)])
    # the 12-class taxonomy says more than the one-class-per-run report
    rep["taxonomy"] = dict(Counter(c for r in runs for c in ch28_ops.classify_detailed(
        r, by_trace[r["trace_id"]], evals.get(r["trace_id"]))).most_common())
    slos = ch28_ops.measure_slos(runs, evals)
    print(ch28_ops.slo_table(slos))
    written = ch28_ops.dashboard(rep, slos, out)
    print(f"\nDashboard: {written}  (open it in a browser, or print it)")
    return written

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
