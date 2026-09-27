"""Exercise 29.6 (solution): find the knee. Sweep the Chapter 8 SQL analyst at 1, 2
and 4 tasks in flight on the configured model, then break one run's latency down.

Run:  ./course.sh python exercises/ex29_6_experiment.py     (18 runs: a few cents)
Pass model_slots=2 to main() to see the knee a client-side limit creates."""
import json

from ch29_perf import (experiment, format_experiment, format_latency, interpret,
                      latency_model, real_agent)

def questions(path="eval_sql.jsonl"):
    return [json.loads(l)["question"] for l in open(path) if l.strip()]

def main(levels=(1, 2, 4), n=6, model_slots=None):
    rows = experiment(real_agent, questions(), levels, n=n, model_slots=model_slots)
    print(format_experiment(rows))
    one = rows[0]["results"][0]                    # unloaded: no queueing in it
    print("\nOne run at concurrency 1, in ms:\n ",
          format_latency(latency_model({**one, "total_ms": one["ms"]})))
    print(interpret(rows))
    return rows

if __name__ == "__main__":
    main()
