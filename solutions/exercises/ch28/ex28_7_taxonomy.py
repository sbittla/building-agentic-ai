"""Exercise 28.7 (solution): classify real failures. Each run below is a small
incident from earlier chapters, scripted as the spans ch28_otel.py would record plus
what the evals said. classify_detailed names the failure classes; the table says how
each was detected, how to fix it and which evaluation keeps it fixed.

    ./course.sh python ex28_7_taxonomy.py"""
from collections import Counter

import ch28_agentops as ops
from ch28_ops import ERR, TAXONOMY, build_spans, classify_detailed

CHAT = ("chat", 900, 2500, 120)                    # an ordinary model call

def incidents() -> list[tuple[str, list, dict]]:
    """(trace_id, spans, eval result) for each crafted run."""
    return [
        # asked for revenue, looked up the customer table instead
        ("wrong-table", build_spans("wrong-table", [
            CHAT, ("tool", "get_customer", 200, {}), CHAT]),
         {"passed": False, "right_tool": False}),
        # right tool, but the date range was last year's
        ("old-dates", build_spans("old-dates", [
            CHAT, ("tool", "run_query", 300, {}), CHAT]),
         {"passed": False, "right_tool": True, "right_args": False}),
        # the weather API was down and the agent said so
        ("api-down", build_spans("api-down", [
            CHAT, ("tool", "get_forecast", 5000, ERR), CHAT]), {"passed": False}),
        # the query returned cents; the answer read them as dollars
        ("cents", build_spans("cents", [
            CHAT, ("tool", "run_query", 250, {}), CHAT]),
         {"passed": False, "right_tool": True, "right_args": True,
          "answer": "Total refunds: 125000", "tool_results": ["[(125000,)]"]}),
        # a figure nobody returned
        ("made-up", build_spans("made-up", [
            CHAT, ("tool", "search_notes", 150, {}), CHAT]),
         {"passed": False, "answer": "Q3 churn was 17.4%",
          "tool_results": ["no notes mention churn"]}),
        # a whole log file pasted into the conversation
        ("huge-log", build_spans("huge-log", [
            CHAT, ("tool", "read_file", 400, {}), ("chat", 3000, 110_000, 0)],
            stop_reason="model_context_window_exceeded"), {}),
        # a web page told the agent to email the customer list
        ("web-page", build_spans("web-page", [
            CHAT, ("tool", "fetch_page", 700,
                   {**ERR, "error.type": "guard_blocked"}), CHAT]), {}),
        # the same failing query, again and again, until max_iterations
        ("same-query", build_spans("same-query", [CHAT] + [
            ("tool", "run_query", 200, {**ERR, "tool.args_hash": "9c2e"}), CHAT] * 4,
            stop_reason="tool_use"), {}),
        # a refund above the agent's limit
        ("big-refund", build_spans("big-refund", [
            CHAT, ("tool", "refund", 80, {**ERR, "error.type": "not_authorized"}),
            CHAT]), {}),
        # a research task that never converged: 20 model calls
        ("rabbit-hole", build_spans("rabbit-hole", [("chat", 2500, 30_000, 400)] * 20),
         {"plan_ok": False}),
    ]

def main() -> Counter:
    counts = Counter()
    for tid, spans, ev in incidents():
        found = classify_detailed(ops.summarize(tid, spans), spans, ev)
        counts.update(found)
        print(f"{tid:<12} {', '.join(found) or 'ok'}")
    print(f"\n{'Failure':<18}Detection -> Mitigation -> Evaluation (chapters)")
    for cls in TAXONOMY:                           # the taxonomy's order, not by count
        if counts[cls]:
            detect, fix, check, chapters, _ = TAXONOMY[cls]
            print(f"{cls:<18}{detect}\n{'':<18}-> {fix} -> {check} (Ch {chapters})")
    return counts

if __name__ == "__main__":
    main()
