"""This is a COPY of run_agent from ch04_agent.py for you to change. Later chapters
import ch04_agent, so keep the original working and experiment here."""
import json
import time
import ch04_agent as a4


def run_agent_traced(question, tools, run_tool, system="You are a helpful assistant.",
                     max_iterations=8):
    messages = [{"role": "user", "content": question}]
    trace = []                                    # one row per step
    answer = f"Stopped at max_iterations={max_iterations}"
    for step in range(1, max_iterations + 1):
        # TODO: time this call separately (model_ms)
        r = a4.get_client().messages.create(model=a4.MODEL, max_tokens=4096, system=system,
                                            tools=tools, messages=messages)
        row = {"step": step, "model_ms": 0.0, "tool_ms": 0.0,
               "in": r.usage.input_tokens, "out": r.usage.output_tokens}
        messages.append({"role": "assistant", "content": r.content})
        if a4.next_action(r)[0] != "tools":
            trace.append(row)
            answer = "".join(b.text for b in r.content if b.type == "text")
            break
        results = []
        for b in r.content:
            if b.type == "tool_use":
                out = run_tool(b.name, b.input)   # TODO: add this tool's time to row["tool_ms"]
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        messages.append({"role": "user", "content": results})
        trace.append(row)
    # TODO: print a table: step, model ms, tool ms, input tokens, output tokens, and totals
    return answer, trace


if __name__ == "__main__":
    from ch03_tools import TOOLS, run_tool
    print(run_agent_traced("How many days until July 4 next year, and what weekday is it?",
                           TOOLS, run_tool)[0])
