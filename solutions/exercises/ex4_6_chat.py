"""Exercise 4.6 (Medium): a multi-turn chat that remembers earlier answers."""
from ch03_tools import TOOLS, run_tool
from ch04_agent import run_agent

def chat(questions=None):
    history, answers = [], []
    source = iter(questions) if questions else None
    while True:
        q = next(source, "quit") if source else input("You: ")
        if q in ("quit", "exit"):
            return answers, history
        answer, history, stats = run_agent(q, TOOLS, run_tool, messages=history, verbose=False)
        answers.append(answer)
        print("Agent:", answer, f"  [{stats['tool_calls']} tool calls]")

if __name__ == "__main__":
    chat()
