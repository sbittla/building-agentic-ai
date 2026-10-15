"""Exercise 24.6: a second skill (customer-lookup) next to the example sql-report skill.
Validates both, then checks from each run's trace that the agent loaded only the skill the
question needed."""
import shutil
from pathlib import Path
import ch24_skills as sk
import ch08_sql_tools as sql
from ch04_agent import run_agent

HERE = Path(__file__).resolve().parent

def install():
    sk.make_example_skill()
    dest = sk.SKILLS_DIR / "customer-lookup"
    if not dest.exists():
        shutil.copytree(HERE / "skills" / "customer-lookup", dest)
    return {p.name: sk.validate(p) for p in sorted(sk.SKILLS_DIR.iterdir()) if p.is_dir()}

def skills_loaded(messages):
    """Each skill once: reading SKILL.md and then one of its extra files (level 3) is
    still one skill. A name that isn't an installed skill (a model that passes a file
    path as the name) loads nothing: read_skill returns an error for it."""
    installed = {p.name for p in sk.SKILLS_DIR.iterdir() if p.is_dir()} if sk.SKILLS_DIR.exists() else set()
    names = [b.input.get("name", "") for m in messages if m["role"] == "assistant" and not isinstance(m["content"], str)
             for b in m["content"] if getattr(b, "type", "") == "tool_use" and b.name == "read_skill"]
    return list(dict.fromkeys(n for n in names if not installed or n in installed))

def run_tool(name, args):
    try:                                   # never raise: the model reads the error and retries
        return sk.read_skill(**args) if name == "read_skill" else sql.run_tool(name, args)
    except TypeError as exc:               # e.g. read_skill called without a name
        return f"ERROR: {exc}. Call read_skill with name (the skill) and, optionally, file."

TESTS = [("What has Customer 7 bought, and how much have they spent?", ["customer-lookup"]),
         ("Give me a revenue report by category.", ["sql-report"]),
         ("How many products do we sell?", [])]

def main():
    print("Validation:", install())
    for q, expected in TESTS:
        _, messages, _ = run_agent(q, sk.TOOLS + sql.TOOLS, run_tool, system=sk.system_prompt(),
                                   verbose=False)
        got = skills_loaded(messages)
        print(f"{'OK ' if got == expected else 'BAD'} {q}  -> loaded {got}, expected {expected}")

if __name__ == "__main__":
    main()
