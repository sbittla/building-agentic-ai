"""Exercise 4.5 (Medium): a tracer that separates model time from tool time."""
import json
import time
import ch04_agent as a4

def run_agent_traced(question, tools, run_tool, system="You are a helpful assistant.",
                     max_iterations=8):
    messages = [{"role": "user", "content": question}]
    trace = []
    for step in range(1, max_iterations + 1):
        t0 = time.perf_counter()
        r = a4.get_client().messages.create(model=a4.MODEL, max_tokens=4096, system=system,
                                            tools=tools, messages=messages)
        model_ms = (time.perf_counter() - t0) * 1000
        row = {"step": step, "model_ms": model_ms, "tool_ms": 0.0, "tools": [],
               "in": r.usage.input_tokens, "out": r.usage.output_tokens}
        messages.append({"role": "assistant", "content": r.content})
        action, note = a4.next_action(r)
        if action != "tools":
            trace.append(row)
            answer = "".join(b.text for b in r.content if b.type == "text")
            if action == "stop":
                answer += f"\n\n[Stopped: {note}]"
            break
        results = []
        for b in r.content:
            if b.type == "tool_use":
                t1 = time.perf_counter()
                out = run_tool(b.name, b.input)
                row["tool_ms"] += (time.perf_counter() - t1) * 1000
                row["tools"].append(f"{b.name}({json.dumps(b.input)})")
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        messages.append({"role": "user", "content": results})
        trace.append(row)
    else:
        answer = f"Stopped at max_iterations={max_iterations}"
    print_table(trace)
    return answer, trace

def print_table(trace):
    print(f"{'step':>4} {'model ms':>9} {'tool ms':>8} {'in tok':>7} {'out tok':>8}  tools")
    for r in trace:
        print(f"{r['step']:>4} {r['model_ms']:>9.0f} {r['tool_ms']:>8.1f} {r['in']:>7} "
              f"{r['out']:>8}  {', '.join(r['tools'])}")
    print(f"{'total':>4} {sum(r['model_ms'] for r in trace):>9.0f} "
          f"{sum(r['tool_ms'] for r in trace):>8.1f} {sum(r['in'] for r in trace):>7} "
          f"{sum(r['out'] for r in trace):>8}")

if __name__ == "__main__":
    from ch03_tools import TOOLS, run_tool
    print(run_agent_traced("How many days until July 4 next, and what weekday is it?",
                           TOOLS, run_tool)[0])
