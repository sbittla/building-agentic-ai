"""Exercise 28.8 (solution): a network incident, found by correlation, then the same
diagnosis with and without span ids on the profiler's samples.

ch28_profile's synthetic traffic gets a new tool, fx_rates, that calls an external
exchange-rate API in parallel with each run's first model call: 60 ms of work plus
two network round trips. Between 8:00 and 9:00 the network to that API degrades
(150-400 ms round trips). The analysis must name the network for fx_rates and leave
the other verdicts unchanged. Free: everything is synthetic and offline."""
import random

import ch28_profile as p

NET_BAD = (480_000, 540_000)                     # 8:00 to 9:00

def with_network_incident(seed: int = 288):
    """ch28_profile.synthetic() plus fx_rates spans, the network incident in the
    resource samples and stack samples for the new spans (20 Hz, span-labelled)."""
    spans, samples, stacks = p.synthetic()
    rng = random.Random(seed)
    for s in samples:
        if NET_BAD[0] <= s["t"] < NET_BAD[1]:
            s["net_ms"] = round(rng.uniform(150, 400), 1)
    net = {s["t"]: s["net_ms"] for s in samples}
    roots = [s for s in spans if s["name"] == "invoke_agent"]
    for root in roots:
        tid = root["trace_id"]
        queue = next(s for s in spans if s["trace_id"] == tid
                     and s["name"].startswith("queue"))
        start = queue["start_ms"] + queue["ms"] + 20       # beside the first chat
        rtt = net[int(start) // 1000 * 1000]
        ms = round(60 + 2 * rtt + rng.uniform(-5, 5), 1)
        sid = f"{tid}-fx"
        spans.append({"name": "execute_tool fx_rates", "trace_id": tid,
                      "span_id": sid, "parent_id": f"{tid}-0", "start_ms": start,
                      "ms": ms, "attributes": {"gen_ai.tool.name": "fx_rates",
                                               "error": False}})
        base = ["agent_loop", "run_tool", "fx_rates"]
        k = 0
        while k * 50 < ms:                         # 20 Hz: one sample every 50 ms
            waiting = k * 50 < 2 * rtt             # the round trips come first
            stack = base + (["http.get", "socket.recv"] if waiting
                            else ["parse_rates", "json.loads"])
            stacks.append({"t": start + k * 50, "span_id": sid, "stack": stack})
            k += 1
    return spans, samples, stacks

def frames_with_and_without_ids(spans, samples, stacks, group="fx_rates"):
    """Top frames of the slowest 5% of `group`, joined on span id, then on time."""
    rows = p.attribute(spans, samples)
    worst = p.slowest(rows, group)
    unlabelled = [{"t": s["t"], "stack": s["stack"]} for s in stacks]
    return worst, p.top_frames(stacks, worst, 3), p.top_frames(unlabelled, worst, 3)

if __name__ == "__main__":
    spans, samples, stacks = with_network_incident()
    rows = p.attribute(spans, samples)
    corr = p.correlate(rows)
    print("DIAGNOSIS with a network incident at 8:00-9:00")
    for line in p.diagnose(corr):
        print("  - " + line)
    worst, by_id, by_time = frames_with_and_without_ids(spans, samples, stacks)
    print(f"\nSLOWEST 5% OF fx_rates ({len(worst)} spans)")
    print("joined on span id:\n" + p._frames(by_id))
    print("joined on time only (other requests' stacks mixed in):\n"
          + p._frames(by_time))
