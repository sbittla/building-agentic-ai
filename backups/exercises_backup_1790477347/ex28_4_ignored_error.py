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
