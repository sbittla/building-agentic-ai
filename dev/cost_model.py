"""The cost model behind every cost figure in the book and the repository.

    python dev/cost_model.py            # print the model, write COST_MODEL.md and the book's Appendix E table
    python dev/cost_model.py --check    # exit 1 if COST_MODEL.md or Appendix E is out of date (CI)

Every number is computed here from stated assumptions, so the README, Chapter 0, "How to Use This
Book", Appendix E and COST_MODEL.md can't disagree. The assumptions are estimates, not measurements:
replace them with your own (each agent in the book prints its input and output tokens) and rerun.

What it counts
  * Exercises that call a paid model: model need `any`, `claude-rec` or `claude` in
    course/model_needs.json (exercises marked `desktop` use the Claude Desktop app's own plan, and
    `none` exercises never call a model).
  * An *agent run* is one task given to an agent: a few model calls with a growing history.
    RUNS below says how many agent runs an exercise's reference solution makes; every other
    model exercise makes one.
  * A *first pass* runs each exercise once, as its reference solution does. A *learner* also reruns
    while debugging and tries variations: the first pass times LEARNER.
"""
import json
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
# The one price table in the kit, read from the source (importing ch20_router needs the whole workspace)
import ast  # noqa: E402
_SRC = (KIT / "course/code/ch20/ch20_router.py").read_text(encoding="utf-8")
PRICES = ast.literal_eval(re.search(r"^PRICES = (\{.*?\})", _SRC, re.M | re.S).group(1))

MODEL, SMALL = "claude-sonnet-5", "claude-haiku-4-5"

# One agent run, low and high: model calls, input tokens per call (the history grows, so this is
# an average), output tokens per call (thinking is billed as output).
RUN = {"low": {"calls": 3, "in_per_call": 2_500, "out_per_call": 500},
       "high": {"calls": 4, "in_per_call": 3_000, "out_per_call": 700}}

# Agent runs made by exercises that run many tasks, read from each exercise's text
# (for example "20 questions", "three trials each", "50 concurrent users").
RUNS = {
    "2.4": 10, "3.4": 20, "3.6": 20, "3.7": 10, "4.5": 50, "6.6": 30, "7.6": 10, "8.7": 15,
    "M.3": 72, "10.7": 30, "11.6": 20, "11.7": 4, "13.8": 3, "16.5": 15, "16.7": 2, "18.5": 8,
    "18.6": 10, "18.9": 6, "20.5": 24, "21.6": 10, "23.5": 3, "23.6": 4, "24.5": 72, "24.7": 3,
    "25.6": 18, "27.4": 24, "27.6": 6, "27.8": 18, "28.3": 5, "29.2": 50, "29.5": 48, "29.6": 18,
    "30.6": 200,
}
ASK_RUNS = 3                       # an "ask" exercise: you chat with the tools for a few turns
LEARNER = {"low": 2.0, "high": 2.0}  # reruns while debugging and trying variations: about twice the first pass
CAPSTONE_RUNS = 120                # per capstone: development runs, a 30-case suite x 3 trials, a load test
PAID = ("any", "claude-rec", "claude")

PARTS = [("0. Foundations", ["0", "P"]), ("1. Your first agent", ["1", "T", "2", "3", "4"]),
         ("2. State and environment", ["5", "R", "6"]), ("3. Real-world tools", ["7", "S", "8", "M", "9"]),
         ("4. Autonomy", ["10", "A", "11"]), ("5. MCP and interoperability", ["12", "13", "14", "15"]),
         ("6. Context, memory and knowledge", ["16", "17", "18"]),
         ("7. Advanced agent architectures", ["19", "20", "21", "22", "23", "24"]),
         ("8. Trust", ["25", "26"]), ("9. Production engineering", ["27", "28", "29", "30"])]


def run_cost(level: str, model: str = MODEL) -> float:
    r, (p_in, p_out) = RUN[level], PRICES[model]
    return r["calls"] * (r["in_per_call"] * p_in + r["out_per_call"] * p_out) / 1e6


def runs(e: dict) -> int:
    return RUNS.get(e["id"], ASK_RUNS if e["kind"] == "ask" else 1)


def model():
    ex = json.loads((KIT / "course/exercises.json").read_text(encoding="utf-8"))
    need = json.loads((KIT / "course/model_needs.json").read_text(encoding="utf-8"))
    paid = [e for e in ex if need.get(e["id"], {}).get("model") in PAID]
    unknown = sorted(set(RUNS) - {e["id"] for e in paid})
    assert not unknown, f"RUNS names exercises that don't call a paid model: {unknown}"
    part_of = {k: name for name, keys in PARTS for k in keys}
    rows = []
    for name, _ in PARTS:
        mine = [e for e in paid if part_of[e["id"].split(".")[0]] == name]
        n = sum(runs(e) for e in mine)
        biggest = sorted((e for e in mine if runs(e) > 1), key=lambda e: -runs(e))[:3]
        rows.append({"part": name, "exercises": len(mine), "runs": n,
                     "first": (n * run_cost("low"), n * run_cost("high")),
                     "biggest": ", ".join(f"{e['id']} ({runs(e)} runs)" for e in biggest)})
    total_runs = sum(r["runs"] for r in rows)
    first = (total_runs * run_cost("low"), total_runs * run_cost("high"))
    learner = (first[0] * LEARNER["low"], first[1] * LEARNER["high"])
    capstone = (CAPSTONE_RUNS * run_cost("low") * LEARNER["low"], CAPSTONE_RUNS * run_cost("high") * LEARNER["high"])
    small = (learner[0] * run_cost("low", SMALL) / run_cost("low"), learner[1] * run_cost("high", SMALL) / run_cost("high"))
    return {"paid_exercises": len(paid), "runs": total_runs, "rows": rows, "first": first,
            "learner": learner, "capstone": capstone, "small": small}


def money(lo: float, hi: float) -> str:
    if hi == 0:
        return "$0"

    def r(x):
        return f"{x:.2f}" if x < 1 else f"{x:.0f}" if x >= 10 else f"{x:.1f}".rstrip("0").rstrip(".")
    return f"${r(lo)}–{r(hi)}"


def rounded(lo: float, hi: float) -> str:
    """The figure quoted in prose: rounded outward to $5."""
    import math
    return f"${max(5, 5 * math.floor(lo / 5))}–{5 * math.ceil(hi / 5)}"


def appendix_table(m: dict) -> str:
    lines = ["Table: Estimated cost by part, for a learner (twice the first pass, for reruns)",
             "| Part | Paid exercises | Agent runs, first pass | Estimated cost | Biggest items |",
             "| --- | ---: | ---: | --- | --- |"]
    for r in m["rows"]:
        lo, hi = r["first"]
        lines.append(f"| {r['part']} | {r['exercises']} | {r['runs']} | "
                     f"{money(lo * LEARNER['low'], hi * LEARNER['high'])} | {r['biggest'] or '—'} |")
    lines.append(f"| **All chapters** | **{m['paid_exercises']}** | **{m['runs']}** | "
                 f"**About {rounded(*m['learner'])}** | First pass alone: {money(*m['first'])} |")
    lines.append(f"| Each capstone | — | about {CAPSTONE_RUNS} | {money(*m['capstone'])} | Evaluation runs and a load test |")
    lines.append("| Cloud deployment (30.7) | — | — | Usually $0 on a free tier | The host's own charges; set a budget alert and delete the service afterward |")
    return "\n".join(lines)


def cost_md(m: dict) -> str:
    r_lo, r_hi = RUN["low"], RUN["high"]
    p_in, p_out = PRICES[MODEL]
    s_in, s_out = PRICES[SMALL]
    return f"""# Cost model

Generated by `python dev/cost_model.py` from `course/exercises.json`, `course/model_needs.json` and the
`PRICES` table in `course/code/ch20/ch20_router.py`. Don't edit by hand; CI fails if it's out of date.
Every cost figure in the book (Chapter 0, "How to Use This Book", Appendix E) and in README.md comes
from here.

## The answer

| What | Claude Sonnet 5 | Claude Haiku 4.5 | Free local model |
| --- | --- | --- | --- |
| One clean pass: every paid exercise once, as its reference solution runs it | **{money(*m['first'])}** | about half | $0 |
| A learner working through the book (reruns while debugging, variations) | **About {rounded(*m['learner'])}** ({money(*m['learner'])}) | About {rounded(*m['small'])} ({money(*m['small'])}) | $0 |
| Each capstone | {money(*m['capstone'])} | about half | $0 |
| `./course.sh check-solutions`, every offline exercise, the benchmark simulator | $0 | $0 | $0 |

Earlier versions of the README said "$5–15 for one run of every exercise". That figure had no stated
assumptions and undercounted the exercises that run many tasks (evaluation suites, load tests); this
model replaces it.

## Assumptions (change them and rerun)

| Assumption | Low | High | Why |
| --- | ---: | ---: | --- |
| Model | `{MODEL}` | | The book's default `MODEL` |
| Price per million tokens, input / output | ${p_in:.2f} / ${p_out:.2f} | | `PRICES` in `ch20_router.py`, at printing |
| Model calls per agent run | {r_lo['calls']} | {r_hi['calls']} | The book's agents take 2–6 steps for a typical task |
| Input tokens per call (average over a run; the history grows) | {r_lo['in_per_call']:,} | {r_hi['in_per_call']:,} | System prompt, tools, question and history |
| Output tokens per call, including thinking | {r_lo['out_per_call']:,} | {r_hi['out_per_call']:,} | Thinking is billed as output |
| Cost of one agent run | ${run_cost('low'):.3f} | ${run_cost('high'):.3f} | calls × (input × price + output × price) |
| Learner multiplier on the first pass | {LEARNER['low']} | {LEARNER['high']} | Reruns while debugging and trying variations: about twice the first pass |
| Agent runs per capstone | {CAPSTONE_RUNS} | {CAPSTONE_RUNS} | Development, a 30-case suite × 3 trials, a load test |
| Haiku 4.5 prices | ${s_in:.2f} / ${s_out:.2f} | | Same token counts |

Exercises that call a paid model: **{m['paid_exercises']}** (model need `any`, `claude-rec` or `claude`).
Agent runs in one clean pass: **{m['runs']}**. Exercises that run many tasks and how many runs each
makes are listed in `RUNS` in `dev/cost_model.py`, taken from each exercise's text.

## By part (learner)

{appendix_table(m).split(chr(10), 1)[1]}

## Production cost formulas

For a deployed agent rather than a learner, use the formulas in section 29.9 of the book and
`course/code/ch29/ch29_economics.py`: cost per task, cost per *successful* task, cost per user per
month, and payback against the human baseline. The per-run formula above is the same one Chapter 29
uses (`ch29_costs.estimate`), without prompt caching; caching (section 16.7) cuts the input term.

## Measuring instead of estimating

Every agent in the book prints its input and output tokens, so you can replace the assumptions with
your own numbers. A measured Claude run of the benchmark (section 29.8) will be published in
`benchmarks/` when it's made; until then these figures are estimates.
"""


def figures(m: dict) -> dict:
    """The figures the book's prose quotes as {{cost:NAME}} (build.js reads course/cost.json)."""
    return {"learner": rounded(*m["learner"]), "first": money(*m["first"]),
            "haiku": rounded(*m["small"]), "capstone": money(*m["capstone"]),
            "run": f"${run_cost('low'):.2f}–{run_cost('high'):.2f}"}


README_RE = re.compile(r"(<!-- cost -->).*?(<!-- /cost -->)", re.S)


def readme_text(m: dict) -> str:
    return (f"Working through the whole book on Claude Sonnet 5 costs about {rounded(*m['learner'])} "
            f"({money(*m['first'])} for one clean pass of every paid exercise; about half on Claude Haiku 4.5; "
            f"nothing on the free local model). See [COST_MODEL.md](COST_MODEL.md) for the assumptions.")


def update_readme(m: dict, write: bool = True) -> bool:
    p = KIT / "README.md"
    text = p.read_text(encoding="utf-8")
    assert README_RE.search(text), "README.md has no <!-- cost --> marker"
    new = README_RE.sub(lambda mm: mm.group(1) + readme_text(m) + mm.group(2), text)
    if write and new != text:
        p.write_text(new, encoding="utf-8")
    return new == text


def update_appendix(m: dict, write: bool) -> bool:
    p = KIT / "course/md/91_appendix.md"
    text = p.read_text(encoding="utf-8")
    pat = re.compile(r"^Table: Estimated cost by part.*?\n(?:\|.*\n)+", re.M)
    assert pat.search(text), "Appendix E's cost table not found"
    new = pat.sub(lambda _: appendix_table(m) + "\n", text, count=1)
    if write and new != text:
        p.write_text(new, encoding="utf-8")
    return new == text


def main():
    m = model()
    check = "--check" in sys.argv
    md = cost_md(m)
    out = KIT / "COST_MODEL.md"
    fresh = out.exists() and out.read_text(encoding="utf-8") == md
    table_ok = update_appendix(m, write=not check)
    if check:
        cj = KIT / "course/cost.json"
        fresh = fresh and cj.exists() and json.loads(cj.read_text(encoding="utf-8")) == figures(m)
        if not (fresh and table_ok and update_readme(m, write=False)):
            print("COST_MODEL.md or Appendix E's cost table is stale: run python dev/cost_model.py")
            return 1
        print(f"OK: cost model current (learner about {rounded(*m['learner'])})")
        return 0
    out.write_text(md, encoding="utf-8")
    (KIT / "course/cost.json").write_text(json.dumps(figures(m), indent=1) + "\n", encoding="utf-8")
    update_readme(m)
    print(f"paid exercises {m['paid_exercises']}, agent runs {m['runs']}, run ${run_cost('low'):.3f}–${run_cost('high'):.3f}")
    print(f"first pass {money(*m['first'])}; learner {money(*m['learner'])} -> 'about {rounded(*m['learner'])}'; "
          f"capstone {money(*m['capstone'])}; Haiku learner {money(*m['small'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
