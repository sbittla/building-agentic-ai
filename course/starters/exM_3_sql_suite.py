import sqlite3
import ch08_sql_tools as sql
from ch04_agent import run_agent
from i_measure import compare, load_cases, report, run_suite


def expected_value(case):
    """Run case["answer_sql"] on a read-only connection and return the first value."""
    # TODO: sqlite3.connect(f"file:{sql.DB_PATH}?mode=ro", uri=True), then fetchone()[0]
    return None


def states_value(answer: str, case) -> bool:
    """True when the answer states the expected value (numbers may contain commas)."""
    # TODO
    return False


def analyst(system):
    """The Chapter 8 analyst as a function of the question, for run_suite."""
    return lambda question: run_agent(question, sql.TOOLS, sql.run_tool, system=system,
                                      verbose=False)[0]


def main(trials=3, path="eval_sql.jsonl"):
    cases = [c for c in load_cases(path) if "answer_sql" in c]
    # TODO: run_suite with sql.SYSTEM, then with one more sentence in the system prompt;
    #       report() both, print the flaky cases and compare()
    return None, None


if __name__ == "__main__":
    main()
