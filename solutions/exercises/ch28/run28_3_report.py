"""Exercise 28.3, run end to end: five traced runs with different questions and the
report; then make one tool fail on purpose (convert_units reads a missing file), run
again, and the second report classifies the failing runs and raises an alert naming it."""
import json
import os
import subprocess
import sys

import ch28_otel as otel
from ch03_tools import TOOLS, run_tool

QUESTIONS = ["How many days until July 4 next year?", "What is 17.5% of 84,213?",
             "How many km is 26.2 miles?", "What day of the week is 2027-01-01?",
             "Convert 70 kg to pounds."]
FAILING = ["How many km is 26.2 miles?", "Convert 70 kg to pounds.",
           "How many grams in 2.5 lb?", "Convert 5 km to miles."]

def broken_tool(name, args):
    if name == "convert_units":                    # e.g. a rates file that went missing
        try:
            return open("conversion_rates_missing.json").read()
        except OSError as exc:
            return f"ERROR: {type(exc).__name__}: {exc}"
    return run_tool(name, args)

def report(title):
    print(f"\n=== {title} ===", flush=True)
    subprocess.run([sys.executable, "ch28_agentops.py", "spans.jsonl"], check=True)

if __name__ == "__main__":
    if os.path.exists("spans.jsonl"):
        os.remove("spans.jsonl")
    for q in QUESTIONS:
        print(f"Q: {q}\nA: {otel.run_traced(q, TOOLS, run_tool)[0]}")
    report("report: five healthy runs")
    os.remove("spans.jsonl")
    for q in FAILING:
        print(f"Q: {q}\nA: {otel.run_traced(q, TOOLS, broken_tool)[0]}")
    report("report: convert_units broken on purpose")
