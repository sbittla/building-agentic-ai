"""Exercise 28.5 (solution): hourly SLO reports and an error-budget burn alert: more
than 10% failures (for a 90% objective) in two consecutive hours."""
import random

import ch28_agentops as ops

def simulate_hour(hour: int, incident: tuple = (14, 16), n: int = 60, seed: int = 0):
    rng = random.Random(seed * 1000 + hour)
    runs = []
    for i in range(n):
        broken = incident[0] <= hour < incident[1] and rng.random() < 0.4
        fail = broken or rng.random() < 0.03
        tools = [("run_query", rng.uniform(50, 400), fail)] * (3 if broken else 1)
        runs.append({"trace_id": f"{hour}-{i}", "ms": rng.uniform(1500, 6000),
                     "stop_reason": "end_turn", "model_calls": 2,
                     "tool_calls": len(tools), "tokens": 3000, "cost": 0.01,
                     "tools": tools})
    return runs

def main(hours=range(8, 20), objective: float = 0.90, incident=(14, 16)):
    rows, alerts, bad_streak = [], [], 0
    for hour in hours:
        runs = simulate_hour(hour, incident)
        classes = [ops.classify(r) for r in runs]
        rep = ops.report(runs, classes)
        burning = rep["success_rate"] < objective
        bad_streak = bad_streak + 1 if burning else 0
        if bad_streak == 2:
            alerts.append(hour)
        rows.append((hour, rep["success_rate"], burning))
        print(f"{hour:02d}:00 success {rep['success_rate']:.0%}"
              + ("  burning" if burning else "") + ("  ALERT" if hour in alerts else ""))
    return rows, alerts

if __name__ == "__main__":
    main()
