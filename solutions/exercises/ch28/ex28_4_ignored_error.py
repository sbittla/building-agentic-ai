"""Exercise 28.4 (solution): a failure class for runs that finished after a tool error
that was never followed by a successful call of the same tool."""
import ch28_agentops as ops

def ignored_error(run: dict) -> bool:
    for i, (name, _, err) in enumerate(run["tools"]):
        if err and not any(n == name and not e for n, _, e in run["tools"][i + 1:]):
            return True
    return False

def classify(run: dict, passed_eval: bool | None = None, slow_ms: float = 30_000) -> str:
    """Chapter 28's order, with the new class after the stop-reason classes and
    loops (more fundamental causes) and before wrong answers."""
    base = ops.classify(run, passed_eval, slow_ms)
    if base in ("refusal", "cut_off", "step_limit", "tool_loop"):
        return base
    if ignored_error(run):
        return "ignored_error"
    return base

FAILURES = ops.FAILURES[:5] + ["ignored_error"] + ops.FAILURES[5:]

if __name__ == "__main__":
    runs = {   # (tool, ms, error?) per call
        "error never retried": [("fetch", 10, True), ("read", 10, False), ("read", 10, False)],
        "error, then retried OK": [("fetch", 10, True), ("fetch", 10, False)],
        "same error three times": [("fetch", 10, True)] * 3,
        "no errors": [("read", 10, False), ("fetch", 10, False)],
    }
    for name, tools in runs.items():
        run = {"stop_reason": "end_turn", "tool_calls": len(tools), "ms": 1000, "tools": tools}
        print(f"{name:<24} -> {classify(run)}")
    print("classes in order:", FAILURES)
