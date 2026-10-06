"""Exercise 21.7 (solution): where does the team pay for itself?

Two questions, both answered offline:
1. On multi-part questions, how slow must the tools be before a lead with parallel
   workers beats one agent on p95 latency? Sweep the tool latency on the simulator
   from section 29.8 and compare the team with one agent that runs its tool calls one
   after another, and with one that runs them at the same time.
2. How many workers can a team have before the chance that every part is right drops
   below 80%, at 97% per step with a lead that plans and synthesizes? With failures
   contained, and with one retry per worker."""
from ch21_coordination import coordination_report, failure_propagation, simulated_runs

TOOL_MS = (500, 1000, 1500, 2000, 3000, 4000)

def sweep(tool_ms=TOOL_MS, reps: int = 5) -> list[dict]:
    rows = []
    for ms in tool_ms:
        single, team = simulated_runs(True, reps=reps, tool_ms=ms)
        fast, _ = simulated_runs(True, reps=reps, tool_ms=ms, parallel_tools=True)
        r = coordination_report(single, team)
        rows.append({"tool_ms": ms, "single_p95": r["single"]["p95_s"],
                     "parallel_p95": coordination_report(fast, team)["single"]["p95_s"],
                     "team_p95": r["team"]["p95_s"],
                     "extra_cost": r["overhead"]["extra_cost_per_task"]})
    return rows

def crossover(rows: list[dict], against: str = "single_p95"):
    """The smallest tool latency at which the team's p95 beats the single agent's."""
    return next((r["tool_ms"] for r in rows if r["team_p95"] < r[against]), None)

def max_workers(p_step: float = 0.97, floor: float = 0.80, retries: int = 0,
                lead_steps: int = 2, limit: int = 1000) -> int:
    """The largest n with p_task >= floor (0 if even one worker is too many)."""
    n = 0
    while n < limit and failure_propagation(p_step, n + 1, parallel=True, retries=retries,
                                            lead_steps=lead_steps)["p_task"] >= floor:
        n += 1
    return n

if __name__ == "__main__":
    rows = sweep()
    print(f"{'tool ms':>8}{'one agent p95':>15}{'parallel tools':>16}{'team p95':>10}"
          f"{'extra $/task':>14}")
    for r in rows:
        print(f"{r['tool_ms']:>8}{r['single_p95']:>15.1f}{r['parallel_p95']:>16.1f}"
              f"{r['team_p95']:>10.1f}{r['extra_cost']:>14.4f}")
    print(f"\nThe team beats one agent with sequential tools from {crossover(rows)} ms "
          f"tools; it beats one agent with parallel tool calls at: "
          f"{crossover(rows, 'parallel_p95') or 'none of these latencies'}.")
    print(f"Workers before every-part-right drops below 80%: {max_workers()} contained, "
          f"{max_workers(retries=1)} with one retry each.")
