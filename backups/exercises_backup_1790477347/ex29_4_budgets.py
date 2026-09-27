"""Exercise 29.4 (solution): a per-request and a per-user daily budget around the
Chapter 8 analyst, both enforced in code."""
import ch08_sql_tools as sql
from ch04_agent import run_agent
from ch29_costs import DailyBudget, request_budget

DAILY = DailyBudget(limit=0.10)

def ask(user: str, question: str, per_request: float = 0.02, max_iterations: int = 20):
    if not DAILY.allow(user):
        return f"Sorry, {user} has used today's budget.", None
    answer, _, stats = run_agent(question, sql.TOOLS, sql.run_tool, system=sql.SYSTEM,
                                 verbose=False, max_iterations=max_iterations,
                                 should_stop=request_budget(per_request))
    DAILY.charge(user, stats)
    return answer, stats

if __name__ == "__main__":
    for q in ["How many customers are there?", "Which city has the most orders?"]:
        print(ask("ana", q)[0])
