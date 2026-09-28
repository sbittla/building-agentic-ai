"""Exercise 24.8 (solution): does the sql-report skill help? Run each request with and
without the skill and check the answer's shape in code."""
import re

import ch08_sql_tools as sql
import ch24_skills as skills
from ch04_agent import run_agent

REQUESTS = ["Give me a revenue report by product category.",
            "Report revenue by city.",
            "Summarize sales by month as a report.",
            "Which categories bring in the most money? A short report, please.",
            "Break down revenue by customer city for the team meeting."]

def check(answer: str) -> dict:
    """The skill's promised format, checked in code."""
    shares = [float(x) for x in re.findall(r"\|\s*([\d.]+)\s*%\s*\|", answer)]
    return {"total": "**Total revenue:**" in answer,
            "table": "| Revenue | Share |" in answer.replace("  ", " "),
            "shares_add_up": bool(shares) and abs(sum(shares) - 100) <= 2,
            "takeaway": "**Takeaway:**" in answer}

def run(request: str, with_skill: bool) -> dict:
    if with_skill:
        tools, system = skills.TOOLS + sql.TOOLS, skills.system_prompt()
    else:
        tools, system = sql.TOOLS, "You are a helpful analyst."
    def run_tool(name, args):
        if name != "read_skill":
            return sql.run_tool(name, args)
        try:                       # bad arguments go back to the model, as in ch08
            return skills.read_skill(**args)
        except TypeError as exc:
            return f"ERROR: {type(exc).__name__}: {exc}"
    answer, _, stats = run_agent(request, tools, run_tool, system=system, verbose=False)
    return {**check(answer), "tokens": stats["input_tokens"] + stats["output_tokens"]}

def main():
    skills.make_example_skill()
    table = {}
    for with_skill in (True, False):
        results = [run(r, with_skill) for r in REQUESTS]
        passed = sum(all(v for k, v in r.items() if k != "tokens") for r in results)
        table["with skill" if with_skill else "without"] = {
            "pass_rate": passed / len(REQUESTS),
            "avg_tokens": sum(r["tokens"] for r in results) / len(REQUESTS)}
    for name, row in table.items():
        print(f"{name:<12} pass rate {row['pass_rate']:.0%}, "
              f"{row['avg_tokens']:.0f} tokens per request")
    return table

if __name__ == "__main__":
    main()
