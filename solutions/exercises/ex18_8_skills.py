"""Exercise 18.8: a second skill (customer-lookup) next to the example sql-report skill.
Validates both, then checks from each run's trace that the agent loaded only the skill the
question needed."""
import shutil
from pathlib import Path
import ch18_skills as sk
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
    return [b.input["name"] for m in messages if m["role"] == "assistant" and not isinstance(m["content"], str)
            for b in m["content"] if getattr(b, "type", "") == "tool_use" and b.name == "read_skill"]

def run_tool(name, args):
    return sk.read_skill(**args) if name == "read_skill" else sql.run_tool(name, args)

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
