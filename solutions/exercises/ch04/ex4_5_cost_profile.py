"""Exercise 4.5 (Complex): cost profile of the agent across questions and runs."""
import statistics
import time
from ch03_tools import TOOLS, run_tool
import ch04_agent as a4

QUESTIONS = [
    "What is 12 * 12?",
    "How many km is 26.2 miles?",
    "What day is it?",
    "How many days until July 4 next, and what weekday is it?",
    "Convert 10 mi to km, 5 kg to lb, and tell me how many days until 2027-01-01.",
]

class Recorder:
    """Wraps the client so every model call's input tokens are recorded with its step."""
    def __init__(self, client):
        self.client, self.calls = client, []
    @property
    def messages(self):
        outer = self
        class M:
            def create(self, **kw):
                r = outer.client.messages.create(**kw)
                step = sum(1 for m in kw["messages"] if m["role"] == "assistant") + 1
                outer.calls.append((step, r.usage.input_tokens))
                return r
        return M()

def profile(runs=10):
    rows = []
    recorder = Recorder(a4.get_client())
    a4._client, original = recorder, a4._client
    for q in QUESTIONS:
        samples = []
        for _ in range(runs):
            t0 = time.perf_counter()
            _, messages, s = a4.run_agent(q, TOOLS, run_tool, verbose=False)
            s["seconds"] = time.perf_counter() - t0
            samples.append(s)
        row = {"question": q}
        for k in ("steps", "tool_calls", "input_tokens", "output_tokens", "seconds"):
            vals = [x[k] for x in samples]
            row[k] = (statistics.mean(vals), max(vals))
        rows.append(row)
    print(f"{'question':<60} {'steps':>9} {'in tok':>13} {'out tok':>11} {'sec':>9}")
    for r in rows:
        f = lambda k, d=0: f"{r[k][0]:.{d}f}/{r[k][1]:.{d}f}"
        print(f"{r['question'][:58]:<60} {f('steps', 1):>9} {f('input_tokens'):>13} "
              f"{f('output_tokens'):>11} {f('seconds', 2):>9}")
    priciest = max(rows, key=lambda r: r["input_tokens"][0])
    print(f"\nMost expensive: {priciest['question']!r} (more steps -> the whole history "
          "is re-sent each step, so input tokens grow faster than steps)")
    a4._client = original
    by_step = {}
    for step, tokens in recorder.calls:
        by_step.setdefault(step, []).append(tokens)
    per_step = {k: statistics.mean(v) for k, v in sorted(by_step.items())}
    print("mean input tokens by step number:", {k: round(v) for k, v in per_step.items()})
    return rows, per_step

def chart(per_step, path="ex4_5_cost_profile.png"):
    """What the exercise asks for: input tokens of each call against its step number."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(6, 4))
    plt.plot(list(per_step), list(per_step.values()), marker="o")
    plt.xlabel("step number within a run"); plt.ylabel("mean input tokens of that call")
    plt.title("Each step resends the history, so input grows"); plt.tight_layout()
    plt.savefig(path)
    return path

if __name__ == "__main__":
    rows, per_step = profile()
    print("saved", chart(per_step))
