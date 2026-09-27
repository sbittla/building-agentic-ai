"""Exercise 17.8 (solution): a to-do assistant with policy-governed memory and a budget.

Memory (ch17_memory_policy) survives restarts because it's in a database; the
conversation history does not, which is exactly what a restart is. The policy decides
what may be stored, and a newer fact on the same subject replaces the older one.
run_managed_agent keeps each session under the budget by trimming and compacting."""
import ch05_todo_tools as todo
import ch17_memory_policy as memory
from ch16_context import run_managed_agent

TOOLS = todo.TOOLS + memory.TOOLS
NAMES = {t["name"] for t in memory.TOOLS}
SYSTEM = (memory.SYSTEM + " You also manage the user's to-do list. At the start of every "
          "session, call recall with 'preferences' before your first answer. When the user "
          "states a preference (date format, reminders, priorities), remember it with a "
          "short subject such as 'date format', so a newer preference replaces the old one.")

def run_tool(name, args):
    return memory.run_tool(name, args) if name in NAMES else todo.run_tool(name, args)

SCRIPT = [  # 20 turns; the second session starts at turn 11 with an empty history
    "Hi! I prefer dates written like 3 Oct 2026.", "Add 'book dentist' due 2026-10-03.",
    "Add 'renew passport' due 2026-11-01.", "I like my most urgent task listed first.",
    "What's on my list?", "Mark the dentist task done.", "Add 'call Priya' due 2026-10-05.",
    "What's still open?", "Remember that my manager is Asha.", "Thanks, that's all for now.",
    "Hello again. What do you know about my preferences?", "What's on my list?",
    "Who is my manager?", "Add 'quarterly review with Asha' due 2026-12-15.",
    "Which task is due next?", "Please forget my date format preference.",
    "What's due in November?", "Add 'buy gift' with no date.", "List everything once more.",
    "Summarize what you remember about me.",
]

def main(budget_tokens=6_000, verbose=False):
    transcript, history, totals = [], [], {"compactions": 0, "trims": 0}
    for turn, text in enumerate(SCRIPT, 1):
        if turn == 11:
            history = []                                   # the "restart"
            transcript.append("---- restart: new session, empty history ----")
        answer, history, stats = run_managed_agent(text, TOOLS, run_tool, system=SYSTEM,
                                                   messages=history, budget_tokens=budget_tokens,
                                                   verbose=verbose)
        totals["compactions"] += stats["compactions"]
        totals["trims"] += stats["trims"]
        transcript.append(f"[{turn:>2}] You: {text}\n     Agent: {answer}")
    print("\n".join(transcript))
    print(f"\n{totals}")
    return transcript, totals

if __name__ == "__main__":
    main()
