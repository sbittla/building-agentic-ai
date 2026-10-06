"""Exercise 30.12: catch it in shadow.

In the chapter's demo, support-agent 1.6 is right on every question but slow. It passes
offline evaluation and shadow, and only the canary catches it, after real users have
waited nine seconds for answers. Shadow traffic has everything needed to catch it
earlier: run both versions through `serve`, measure each side's SLOs from the traces
with `measure_arm`, and reject a candidate that misses a latency or cost SLO, or that
costs more than 20% above the current version per task. Free: fake agents, no model."""
import ch30_improvement_loop as loop

PLAIN_SHADOW = loop.shadow
MAX_COST_RISE = 0.20


def _value(arm: dict, name: str):
    return next(s["value"] for s in arm["slos"] if s["name"].startswith(name))


def shadow_with_slos(current, candidate, requests, gates=loop.GATES,
                     max_cost_rise=MAX_COST_RISE) -> dict:
    """The chapter's shadow stage, plus latency and cost measured on the same mirrored
    requests. Nothing here reaches a user: both sides' traces stay in the shadow."""
    result = PLAIN_SHADOW(current, candidate, requests, gates)
    live = loop.measure_arm([loop.serve(current, r) for r in requests])
    trial = loop.measure_arm([loop.serve(candidate, r) for r in requests])
    for name in trial["missed"]:
        if not name.startswith("Task"):            # success is the plain shadow's job
            result["reasons"].append(f"missed {name}")
    rise = _value(trial, "Cost") / _value(live, "Cost") - 1
    if rise > max_cost_rise:
        result["reasons"].append(f"costs {rise:.0%} more per task")
    result.update(passed=not result["reasons"], live_slos=live, trial_slos=trial,
                  cost_rise=round(rise, 3))
    return result


def run(candidates) -> list[dict]:
    """One improvement turn per candidate, with the stricter shadow stage."""
    v14 = loop.releases()[0]
    production = [loop.serve(v14, r) for r in loop.traffic(200, seed=1)]
    loop.shadow = shadow_with_slos                 # improvement_turn looks it up by name
    try:
        return [loop.improvement_turn(v14, c, production, loop.SUITE,
                                      loop.traffic(100, seed=2), loop.traffic(400, seed=3))
                for c in candidates]
    finally:
        loop.shadow = PLAIN_SHADOW


if __name__ == "__main__":
    _, v15, v16 = loop.releases()
    for turn in run([v15, v16]):
        loop.show(turn)
        served = [s for s in turn["stages"] if s["stage"] == "canary"]
        users = sum(r["version"] == turn["release"]
                    for s in served for r in s["records"])
        print(f"  {turn['release']}: {turn['decision']} at "
              f"{turn['stopped_at'] or 'the end'}; requests it served to users: {users}\n")
