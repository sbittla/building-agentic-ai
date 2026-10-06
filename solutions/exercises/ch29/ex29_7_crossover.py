"""Exercise 29.7: when does the cheaper model stop being cheaper?

The small model costs less per call, but every wrong answer is a task you paid for and
didn't get. Raise its simulated error rate step by step and compare cost per SUCCESSFUL
task with the large model's (experiment E3, base context). Free: the simulator."""
import tempfile

import ch29_benchmark as b

rows = []
with tempfile.TemporaryDirectory() as out:
    for p_wrong in (0.10, 0.20, 0.30, 0.40, 0.50):
        b.SIM_MODELS[b.SMALL]["p_wrong"] = p_wrong
        e3 = b.main(["--experiments", "E3", "--reps", "3", "--long-context", "0", "--quiet", "--out", out])["E3"]
        small = next(r for r in e3 if r["config"].startswith(b.SMALL) and "base" in r["config"])
        large = next(r for r in e3 if r["config"].startswith(b.LARGE) and "base" in r["config"])
        rows.append((p_wrong, small, large))

print("small model's wrong-SQL rate | small: success, $/success | large: success, $/success")
for p_wrong, s, l in rows:
    print(f"{p_wrong:>28.0%} | {s['success']:>7.0%}, ${s['cost_per_success']:.4f} | "
          f"{l['success']:>7.0%}, ${l['cost_per_success']:.4f}")
cross = next((p for p, s, l in rows if s["cost_per_success"] >= l["cost_per_success"]), None)
print(f"\nThe small model stops being cheaper per success at a wrong-SQL rate of "
      f"{cross:.0%}." if cross else "\nThe small model stays cheaper per success over this range; "
      "but look at its success rate: would your users accept it?")
