"""Exercise 3.3 (Simple): which tool does each question go to?"""
from ch03_tools import TOOLS, run_tool
from sol_ch02_calculator_agent import client, MODEL

def ask_and_report(question: str):
    messages = [{"role": "user", "content": question}]
    used = []
    for _ in range(5):
        r = client.messages.create(model=MODEL, max_tokens=2000, tools=TOOLS, messages=messages)
        if r.stop_reason != "tool_use":
            return "".join(b.text for b in r.content if b.type == "text"), used
        messages.append({"role": "assistant", "content": r.content})
        results = []
        for b in r.content:
            if b.type == "tool_use":
                used.append(b.name)
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "content": run_tool(b.name, b.input)})
        messages.append({"role": "user", "content": results})
    return "stopped", used

if __name__ == "__main__":
    for q in ["What day is it?", "How many km is 26.2 miles?"]:
        answer, used = ask_and_report(q)
        print(f"{q}\n  tools: {used}\n  answer: {answer}\n")
