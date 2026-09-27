"""Exercise 24.7: the managed analyst, once to completion and once with a budget too small
to finish, so you see the session stop with budget_reached."""
import ch24_managed_agent as ma

QUESTION = ("Build a revenue report by product category, save it as revenue.csv in your "
            "sandbox and show me the first lines of the file.")

def run_with_budget(cents: int, client=None, approve=ma.console_approve) -> str:
    saved = ma.BUDGET
    ma.BUDGET = {"type": "limit", "max_list_cost": {"amount": str(cents), "currency": "USD"}}
    try:
        return ma.run(QUESTION, client=client, approve=approve)
    finally:
        ma.BUDGET = saved

if __name__ == "__main__":
    print("== Normal budget ($1.00) ==")
    print("ended:", run_with_budget(100))
    print("\n== Tiny budget ($0.02) ==")
    print("ended:", run_with_budget(2))
