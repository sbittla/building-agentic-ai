"""Exercise 8.4 (Simple): sabotage the prompt and watch the agent self-correct."""
import ch08_sql_tools as sql
from ch04_agent import run_agent

WRONG_SYSTEM = sql.SYSTEM + " Customer data is in the clients table."   # there is no such table

def main(question="Which city has the most customers?"):
    answer, messages, stats = run_agent(question, sql.TOOLS, sql.run_tool, system=WRONG_SYSTEM)
    errors = [c["content"] for m in messages if m["role"] == "user" and isinstance(m["content"], list)
              for c in m["content"] if c["content"].startswith("ERROR")]
    print(f"\n{answer}\n\nfailed queries along the way: {len(errors)}")
    return answer, errors

if __name__ == "__main__":
    main()
