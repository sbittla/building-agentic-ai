"""Run an interactive course program with scripted input, for run-chapter.

    python typed.py "ch17_memory.py" "My dog is called Bruno." quit
    python typed.py "ch13_mcp_agent.py servers.json" "How many orders are pending?" quit

The program runs in this process with input() replaced: each call prints its prompt and
the scripted line, as if typed, so the log reads like a real session. When the lines run
out, input() raises EOFError, as at the end of a piped stdin."""
import builtins
import runpy
import shlex
import sys

if __name__ == "__main__":
    program, *args = shlex.split(sys.argv[1])
    lines = list(sys.argv[2:])

    def scripted_input(prompt=""):
        if not lines:
            raise EOFError
        line = lines.pop(0)
        print(f"{prompt}{line}", flush=True)
        return line

    builtins.input = scripted_input
    sys.argv = [program, *args]
    sys.path.insert(0, ".")
    runpy.run_path(program, run_name="__main__")
