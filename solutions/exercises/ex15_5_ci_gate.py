"""Exercise 15.5 (solution): fail the build when eval quality drops.

Run it in CI on pull requests, not as a pre-commit hook: every run makes real, paid
model calls (24 cases x 3 trials is about 72 agent runs, roughly $1-2 with Sonnet 5),
and you don't want that on every local commit.

GitHub Actions (.github/workflows/eval.yml):
    on: [pull_request]
    jobs:
      eval:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - run: docker compose build
          - run: docker compose run --rm -T -e ANTHROPIC_API_KEY course python exercises/ex15_5_ci_gate.py
            env:
              ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
"""
import json
import sys
import ch08_sql_tools as sql
from ch15_eval import run_suite, summarize

THRESHOLD = 0.85      # set it from your current results, a little below them
TRIALS = 3            # one run per case can't tell a real drop from bad luck

def gate(path="eval_sql.jsonl", threshold=THRESHOLD, trials=TRIALS, system=sql.SYSTEM) -> int:
    cases = [json.loads(line) for line in open(path) if line.strip()]
    s = summarize(run_suite(cases, sql.TOOLS, sql.run_tool, system, trials=trials))
    lo, hi = s["ci95"]
    print(f"\nCI gate: pass rate {s['pass_rate']:.0%} (95% CI {lo:.0%}-{hi:.0%}) vs threshold "
          f"{threshold:.0%}")
    if s["pass_rate"] < threshold:
        print("FAIL: quality dropped below the threshold.")
        return 1
    if lo < threshold:
        print("PASS, but borderline: the interval reaches below the threshold. "
              "More trials would make the result firmer.")
    else:
        print("PASS")
    return 0

if __name__ == "__main__":
    sys.exit(gate(*(sys.argv[1:2] or [])))
