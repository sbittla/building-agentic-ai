"""Chapter 10 reference solution: 10.6 (replace_in_file) and 10.7 (sandbox option)."""
import os
import ch10_fixer as base
from ch10_fixer import _safe, list_files, read_file, run_tests, history

def replace_in_file(path: str, old: str, new: str) -> str:
    """Change one exact snippet. Fails unless `old` appears exactly once."""
    if reason := base.writable(path):            # the same allow-list as write_file
        return f"ERROR: {reason}"
    p = _safe(path)
    content = p.read_text()
    count = content.count(old)
    if count != 1:
        return (f"ERROR: the snippet appears {count} times in {path}; include more "
                "surrounding text so it matches exactly once.")
    p.write_text(content.replace(old, new, 1))
    return f"Replaced 1 snippet in {path}."

def make_tools(use_sandbox: bool = False):
    registry = {"list_files": list_files, "read_file": read_file,
                "replace_in_file": replace_in_file, "run_tests": run_tests}
    if use_sandbox:
        from ch10_sandbox import run_tests_sandboxed
        def sandboxed():
            out = run_tests_sandboxed(str(base.REPO))
            import re
            m = re.search(r"(\d+) failed", out)
            if re.search(r"\d+ (passed|failed)", out):
                history.append(int(m.group(1)) if m else 0)
            return out
        registry["run_tests"] = sandboxed
    tools = [t for t in base.TOOLS if t["name"] != "write_file"] + [{
        "name": "replace_in_file", "description": "Replace ONE exact snippet in a file "
        "(must match exactly once). Test files cannot be edited.",
        "input_schema": {"type": "object", "properties": {
            "path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}},
            "required": ["path", "old", "new"]}}]
    def run_tool(name, args):
        try:
            return str(registry[name](**args))
        except Exception as exc:
            return f"ERROR: {type(exc).__name__}: {exc}"
    return tools, run_tool

SYSTEM = base.SYSTEM + " Make edits with replace_in_file, changing as few lines as possible."
should_stop = base.should_stop
