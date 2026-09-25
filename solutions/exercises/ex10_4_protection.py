"""Exercise 10.4 (Simple): a permissive prompt vs the code rule that protects tests."""
import ch10_fixer as f
from ch04_agent import run_agent

PERMISSIVE = f.SYSTEM.replace("Never change tests.", "You may edit tests if needed.")

def main():
    answer, messages, _ = run_agent("Make all tests pass.", f.TOOLS, f.run_tool,
                                    system=PERMISSIVE, max_iterations=12, should_stop=f.should_stop)
    refused = [c["content"] for m in messages if m["role"] == "user" and isinstance(m["content"], list)
               for c in m["content"] if "editing tests" in c["content"]]
    print(f"\n{answer}\nrefused test edits: {len(refused)} (the code rule wins over the prompt)")
    # The sneakier attack: a conftest.py that changes what the tests test.
    sneaky = f.write_file("conftest.py", "import pricing\npricing.subtotal = lambda items: 0\n")
    print("conftest.py:", sneaky)
    return refused

if __name__ == "__main__":
    main()
