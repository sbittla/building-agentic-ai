"""Exercise 3.5 (Medium): a 20-question routing eval, run 3 times."""
import statistics
from ch03_tools import TOOLS
from sol_ch02_calculator_agent import client, MODEL

CASES = [
    ("What day is it today?", "get_current_date"),
    ("Is today a weekend?", "get_current_date"),
    ("What's the date this coming Friday?", "get_current_date"),
    ("How many km is 26.2 miles?", "convert_units"),
    ("Convert 70 kg to pounds.", "convert_units"),
    ("How many grams in 2.5 lb?", "convert_units"),
    ("What is 1234 * 5678?", "calculate"),
    ("What is 17.5% of 84,213?", "calculate"),
    ("Compute (19.99 + 5.49) * 3.", "calculate"),
    ("How many days from 2026-01-01 to 2026-07-04?", "days_between"),
    ("What weekday is 2027-01-01, counting from 2026-12-25?", "days_between"),
    ("Days between 2025-02-10 and 2025-03-10?", "days_between"),
    ("What is a prime number?", None),
    ("Who wrote Hamlet?", None),
    ("Explain what a kilometer is.", None),
    ("How many days until 2026-12-25?", "get_current_date"),   # ambiguous: needs today first
    ("Double 26.2 miles and give it in km.", "calculate"),      # ambiguous: calc or convert
    ("How old is someone born 1990-05-01 today, in days?", "get_current_date"),
    ("Convert 10 mi to km and 5 kg to lb.", "convert_units"),
    ("What's 3 + 4?", "calculate"),
]

def first_tool(question):
    r = client.messages.create(model=MODEL, max_tokens=2000, tools=TOOLS,
                               messages=[{"role": "user", "content": question}])
    calls = [b.name for b in r.content if b.type == "tool_use"]
    return calls[0] if calls else None

def run(n_runs=3):
    runs = []
    for _ in range(n_runs):
        runs.append({q: first_tool(q) for q, _ in CASES})
    scores = [sum(run[q] == exp for q, exp in CASES) / len(CASES) for run in runs]
    flips = [q for q, _ in CASES if len({run[q] for run in runs}) > 1]
    failures = {q: (exp, [run[q] for run in runs]) for q, exp in CASES
                if any(run[q] != exp for run in runs)}
    print(f"accuracy per run: {[f'{s:.0%}' for s in scores]}  mean={statistics.mean(scores):.0%}")
    print(f"flipping questions: {flips or 'none'}")
    for q, (exp, got) in failures.items():
        print(f"  FAIL expected={exp} got={got}  {q}")
    return scores, flips, failures

if __name__ == "__main__":
    run()
