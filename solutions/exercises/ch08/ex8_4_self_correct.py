"""Exercise 8.4 (Simple): sabotage the prompt and watch the agent self-correct."""
import ch08_sql_tools as sql
from ch04_agent import run_agent

# There is no clients table. SYSTEM itself says "Look at the schema", so appending a
# wrong fact isn't enough: a model that reads the schema first never fails. Replace the
# prompt, as the exercise says, so the wrong name is the only description it has.
WRONG_SYSTEM = ("You are a data analyst. Customer data is in the clients table (columns "
                "id, name, town). You already know the schema: write SQLite SQL against it "
                "directly, run it, and answer with the numbers. Show the final SQL you used.")

def main(question="Which city has the most customers?"):
    answer, messages, stats = run_agent(question, sql.TOOLS, sql.run_tool, system=WRONG_SYSTEM)
    errors = [c["content"] for m in messages if m["role"] == "user" and isinstance(m["content"], list)
              for c in m["content"] if c["content"].startswith("ERROR")]
    print(f"\n{answer}\n\nfailed queries along the way: {len(errors)}")
    return answer, errors

if __name__ == "__main__":
    main()
