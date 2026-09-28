"""Exercise 4.3 (Simple): trigger the iteration cap, and watch repeated errors."""
from ch03_tools import TOOLS, REGISTRY, run_tool
from ch04_agent import run_agent

def always_fails() -> str:
    return "ERROR: service unavailable"

TOOLS_WITH_FAILURE = TOOLS + [{
    "name": "always_fails", "description": "Look up the live exchange rate. (Always fails.)",
    "input_schema": {"type": "object", "properties": {}}}]

def run_tool_with_failure(name, args):
    return always_fails() if name == "always_fails" else run_tool(name, args)

def main():
    capped, _, s1 = run_agent("How many days until July 4 next, and what weekday is it?",
                              TOOLS, run_tool, max_iterations=1)
    print("\nWith max_iterations=1:", capped, s1)
    failing, _, s2 = run_agent("What is the live USD to INR exchange rate?",
                               TOOLS_WITH_FAILURE, run_tool_with_failure, max_iterations=4)
    print("\nWith an always-failing tool:", failing, s2)
    return capped, failing

if __name__ == "__main__":
    main()
