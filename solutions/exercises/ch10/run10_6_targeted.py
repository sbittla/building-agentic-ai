"""Exercise 10.6, run end to end: fix the same fresh buggy repo twice, once with write_file
(the chapter's agent) and once with replace_in_file (sol_ch10_fixer), and compare tokens."""
import difflib
import subprocess

import ch10_fixer as base
import sol_ch10_fixer as sol
from ch04_agent import run_agent

def fresh_repo():
    subprocess.run(["course", "data", "repo", "--fresh"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def fix(label, tools, run_tool, system):
    fresh_repo()
    base.history.clear()
    before = {p: p.read_text() for p in base.REPO.glob("*.py")}
    answer, messages, stats = run_agent("Make all tests pass.", tools, run_tool, system=system,
                                        max_iterations=15, should_stop=base.should_stop)
    used = [b.name for m in messages if m["role"] == "assistant"
            for b in m["content"] if getattr(b, "type", None) == "tool_use"]
    print(f"\n[{label}] tools used: {used}")
    print(f"[{label}] failing tests per run: {base.history}")
    for p, old in before.items():
        new = p.read_text()
        if new != old:
            print("".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                               f"a/{p.name}", f"b/{p.name}")))
    return stats["input_tokens"] + stats["output_tokens"], used, base.history[-1:] == [0]

if __name__ == "__main__":
    whole, _, ok_w = fix("write_file", base.TOOLS, base.run_tool, base.SYSTEM)
    tools, run_tool = sol.make_tools()
    targeted, used, ok_t = fix("replace_in_file", tools, run_tool, sol.SYSTEM)
    print("| edit tool | tokens | tests pass |")
    print(f"| write_file | {whole:,} | {ok_w} |")
    print(f"| replace_in_file | {targeted:,} | {ok_t} |")
    print(f"replace_in_file used: {'replace_in_file' in used}; token difference: "
          f"{targeted - whole:+,} ({(targeted - whole) / whole:+.0%})")
