"""Exercise 27.6 (solution): grade six cases on outcome, process and cost, three times."""
import json
from pathlib import Path

import ch08_sql_tools as sql
from ch27_trajectory import grade

CASES = Path(__file__).with_name("ex27_6_trajectory.jsonl")

def main(trials: int = 3):
    cases = [json.loads(l) for l in CASES.read_text().splitlines() if l.strip()]
    rows = [grade(c, sql.TOOLS, sql.run_tool, sql.SYSTEM) for c in cases
            for _ in range(trials)]
    for r in rows:
        print(f"{r['id']:<18} outcome {'ok ' if r['outcome'] else 'BAD'} process "
              f"{'ok ' if r['process'] else 'BAD'} ${r['cost']:.4f} "
              f"{'; '.join(r['failures'])}")
    lucky = [r["id"] for r in rows if r["outcome"] and not r["process"]]
    print("Right answer, wrong path:", sorted(set(lucky)) or "none")
    return rows

if __name__ == "__main__":
    main()
