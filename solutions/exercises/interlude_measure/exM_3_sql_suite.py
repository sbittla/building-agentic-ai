"""Interlude exercise M.3: the Chapter 8 SQL analyst, measured with trials and a margin of
error. A case passes when the answer states the value its answer_sql returns."""
import re
import sqlite3
import ch08_sql_tools as sql
from ch04_agent import run_agent
from i_measure import compare, load_cases, report, run_suite

def expected_value(case):
    """The truth comes from the data, on a read-only connection."""
    with sqlite3.connect(f"file:{sql.DB_PATH}?mode=ro", uri=True) as con:
        row = con.execute(case["answer_sql"]).fetchone()
    return row[0] if row else None

def states_value(answer: str, case) -> bool:
    value = expected_value(case)
    if isinstance(value, (int, float)):
        numbers = [float(n.replace(",", "")) for n in re.findall(r"-?\d[\d,]*\.?\d*", answer)]
        return any(abs(n - value) <= 0.51 for n in numbers)
    return value is not None and str(value).lower() in answer.lower()

def analyst(system):
    return lambda question: run_agent(question, sql.TOOLS, sql.run_tool, system=system,
                                      verbose=False)[0]

def main(trials=3, path="eval_sql.jsonl"):
    cases = [c for c in load_cases(path) if "answer_sql" in c]
    before = run_suite(analyst(sql.SYSTEM), cases, trials, states_value)
    after = run_suite(analyst(sql.SYSTEM + " Exclude cancelled orders unless the question "
                              "says otherwise, and state the final number in your answer."),
                      cases, trials, states_value)
    report("before", before)
    report("after", after)
    print("flaky before:", before["flaky"] or "none", "| flaky after:", after["flaky"] or "none")
    print("verdict:", compare(before, after))
    return before, after

if __name__ == "__main__":
    main()
