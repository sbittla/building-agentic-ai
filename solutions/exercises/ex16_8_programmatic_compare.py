"""Exercise 16.8: programmatic tool calling against the normal SQL agent on the same
question. Counts model calls and tokens for each; the fan-out question favors the program,
the step-by-step question favors the plain loop."""
import ch08_sql_tools as sql
import ch16_programmatic as pg
from ch04_agent import run_agent

FAN_OUT = "For each product category, what share of total revenue does it earn? Query each category separately."
STEP_BY_STEP = ("Find our best customer by revenue, then tell me which category they spend most on, "
                "then whether that category is growing month over month.")

def plain(question):
    answer, _, stats = run_agent(question, sql.TOOLS, sql.run_tool, system=sql.SYSTEM, verbose=False)
    return answer, {"model_calls": stats["steps"], "input_tokens": stats["input_tokens"],
                    "tool_calls": stats["tool_calls"]}

def programmatic(question):
    answer, stats = pg.ask(question, verbose=False)
    return answer, {"model_calls": stats["steps"], "tool_calls": stats["tool_calls"],
                    "result_chars_kept_out": stats["result_chars_kept_out"]}

if __name__ == "__main__":
    for q in (FAN_OUT, STEP_BY_STEP):
        print(f"\n{q}")
        for name, fn in (("plain loop", plain), ("programmatic", programmatic)):
            answer, row = fn(q)
            print(f"  {name:<13} {row}\n    {answer[:150]}")
    print("\nRule: use programmatic calling when many calls feed one summary; use the plain loop "
          "when each step depends on the model reading the last result.")
