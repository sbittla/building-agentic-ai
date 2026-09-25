"""Chapter 16: programmatic tool calling. Instead of calling run_query once per step and
reading every result, the model writes a short Python program that calls run_query as many
times as it needs, filters and sums the rows, and prints only the answer. The program runs
in Anthropic's code-execution sandbox; each run_query call still comes to YOUR code, but its
result goes back to the program, not into the model's context.

Run:  python ch16_programmatic.py"""
import json
from ch04_agent import get_client, MODEL, next_action
import ch08_sql_tools as sql

CODE_EXECUTION = {"type": "code_execution_20260120", "name": "code_execution"}

RUN_QUERY = {
    "name": "run_query",
    "description": "Run one read-only SQL SELECT on the shop database. Returns the rows as a "
                   "JSON list of objects (at most 50 rows).",
    "input_schema": {"type": "object", "properties": {"sql": {"type": "string"}},
                     "required": ["sql"]},
    # Only code running in the sandbox may call it, so every result is processed in code.
    "allowed_callers": ["code_execution_20260120"],
}

def run_query_json(sql_text: str) -> str:
    """run_query's result as JSON rows, which is easier for a program than a text table."""
    try:
        with sql._connect(sql.QUERY_SECONDS) as con:
            con.row_factory = lambda cur, row: {d[0]: v for d, v in zip(cur.description, row)}
            rows = con.execute(sql_text).fetchmany(50)
        return json.dumps(rows)
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

def ask(question: str, max_steps: int = 20, verbose: bool = True):
    """The usual loop, with two differences: keep reusing the same container, and count how
    many tool results went to the program instead of into the conversation."""
    messages = [{"role": "user", "content": question}]
    container, stats = None, {"tool_calls": 0, "result_chars_kept_out": 0, "steps": 0}
    for stats["steps"] in range(1, max_steps + 1):
        kwargs = {"container": container} if container else {}
        r = get_client().messages.create(model=MODEL, max_tokens=4096, tools=[CODE_EXECUTION, RUN_QUERY],
                                          messages=messages, **kwargs)
        container = getattr(getattr(r, "container", None), "id", None) or container
        messages.append({"role": "assistant", "content": r.content})
        action, note = next_action(r)
        if action == "done":
            return "".join(b.text for b in r.content if b.type == "text"), stats
        if action == "stop":
            return f"Stopped: {note}", stats
        results = []
        for b in r.content:
            if b.type == "tool_use":                     # called from inside the program
                out = run_query_json(b.input["sql"])
                stats["tool_calls"] += 1
                stats["result_chars_kept_out"] += len(out)
                if verbose:
                    print(f"  [program called run_query] {b.input['sql'][:70]}")
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        if results:
            messages.append({"role": "user", "content": results})
    return "Stopped at max_steps.", stats

if __name__ == "__main__":
    answer, stats = ask("For each product category, what share of total revenue does it earn? "
                        "Query each category separately.")
    print(answer)
    print(f"\n{stats['tool_calls']} queries; {stats['result_chars_kept_out']:,} characters of "
          "results stayed in the sandbox instead of the model's context.")
