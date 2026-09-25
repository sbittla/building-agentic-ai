"""Exercise 7.6 (Medium): run independent tool calls at the same time."""
import json
import time
from concurrent.futures import ThreadPoolExecutor
import ch04_agent as a4

def run_agent_parallel(question, tools, run_tool, system="You are a helpful assistant.",
                       max_iterations=8, max_workers=8):
    messages = [{"role": "user", "content": question}]
    stats = {"steps": 0, "tool_calls": 0, "tool_seconds": 0.0}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for step in range(1, max_iterations + 1):
            r = a4.get_client().messages.create(model=a4.MODEL, max_tokens=4096, system=system,
                                                tools=tools, messages=messages)
            stats["steps"] = step
            messages.append({"role": "assistant", "content": r.content})
            action, note = a4.next_action(r)
            if action == "done":
                return "".join(b.text for b in r.content if b.type == "text"), stats
            if action == "stop":
                return f"Stopped: {note}", stats
            if action == "continue":
                continue
            calls = [b for b in r.content if b.type == "tool_use"]
            t0 = time.perf_counter()
            outputs = list(pool.map(lambda b: run_tool(b.name, b.input), calls))  # keeps order
            stats["tool_seconds"] += time.perf_counter() - t0
            stats["tool_calls"] += len(calls)
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": b.id, "content": out}
                for b, out in zip(calls, outputs)]})
    return f"Stopped at max_iterations={max_iterations}", stats

def compare(question, tools, run_tool, system):
    """The same question twice: tools one at a time (max_workers=1), then in parallel.
    The cache is cleared between runs so both make the same HTTP calls."""
    import ch07_weather_tools as w
    results = {}
    for name, workers in [("sequential", 1), ("parallel", 8)]:
        w._cache.clear()
        answer, s = run_agent_parallel(question, tools, run_tool, system=system, max_workers=workers)
        results[name] = s
        print(f"{name:<10} tool time {s['tool_seconds']:.2f}s  ({s['tool_calls']} calls)")
    seq, par = results["sequential"]["tool_seconds"], results["parallel"]["tool_seconds"]
    if par:
        print(f"parallel tools were {seq / par:.1f}x faster")
    return results

if __name__ == "__main__":
    import ch07_weather_tools as w
    compare("Compare the next 3 days' weather in Seattle, Pune and Berlin.",
            w.TOOLS, w.run_tool, w.SYSTEM)
