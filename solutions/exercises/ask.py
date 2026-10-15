"""Ask a chapter's agent several questions, for run-chapter's "ask" exercises.

    python ask.py ch06_notes_tools "Question one?" "Question two?"

Each question starts a fresh conversation with the module's TOOLS, run_tool and SYSTEM;
the trace, the answer and the number of file:line citations in it are printed, then how
many answers carried at least one citation."""
import importlib
import os
import re
import sys

from ch04_agent import run_agent

if __name__ == "__main__":
    m = importlib.import_module(sys.argv[1])
    system = getattr(m, "SYSTEM", "You are a helpful assistant. Use the tools.")
    system += " " + os.environ.get("ASK_SYSTEM_EXTRA", "")     # a sharper rule, if any
    questions, cited = sys.argv[2:], 0
    for q in questions:
        print(f"\nQ: {q}")
        answer, messages, _ = run_agent(q, m.TOOLS, m.run_tool, system=system)
        # path:line, or the same facts as "line 3 of path": both point at one checkable line
        pattern = r"[\w./-]+\.\w+:\d+|lines? \d+ (?:of|in) [\w./-]+\.\w+"
        cites = re.findall(pattern, answer)
        looked = any(getattr(b, "type", "") == "tool_use" for msg in messages
                     if msg["role"] == "assistant" and not isinstance(msg["content"], str)
                     for b in msg["content"])
        if not cites and looked:      # it searched the notes but gave no source: ask once
            print("   [no citation, though it searched the notes: asking once for the source]")
            answer, _, _ = run_agent("Add the source of each fact as (path:line), from the "
                                     "lines you read.", m.TOOLS, m.run_tool, system=system,
                                     messages=messages)
            cites = re.findall(pattern, answer)
        cited += bool(cites)
        print(f"A: {answer}\n   [citations: {len(cites)}]")
    print(f"\nanswers with citations: {cited} of {len(questions)}")
