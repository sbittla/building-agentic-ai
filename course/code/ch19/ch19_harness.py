"""Chapter 19: a harness for open-ended work that spans many sessions.

A durable job (ch19_durable.py) needs its steps known in advance. Open-ended work,
such as "write the weekly sales report", doesn't. This harness keeps the state of
that work OUTSIDE the model, where every new session can read it:

  * features.json   the checklist: each item has a check your code runs, and a status
  * progress.md     what each session did and learned, in plain words
  * one item at a time, and an item is "passing" only when its check passes

    ./course.sh python ch19_harness.py          run one session (two items at most)
    ./course.sh python ch19_harness.py reset    start the report again"""
import json
import re
import sys
import time
from pathlib import Path

from ch04_agent import run_agent
import ch08_sql_tools as sql

FEATURES = Path("report/features.json")
PROGRESS = Path("report/progress.md")
MAX_ATTEMPTS = 3            # then the item waits for a person

# ------------------------------------------------------------ 1. the checklist
REPORT = [   # what "done" means, written before any work starts
    {"id": "revenue", "task": "Revenue by month, not counting cancelled orders.",
     "check": {"file": "revenue.md", "needs": ["revenue"], "numbers": 3}},
    {"id": "top_products", "task": "The five best-selling products by revenue.",
     "check": {"file": "top_products.md", "needs": [], "numbers": 5}},
    {"id": "cities", "task": "The three cities with the most customers.",
     "check": {"file": "cities.md", "needs": [], "numbers": 3}},
    {"id": "cancellations", "task": "How many orders were cancelled, and what share "
     "of all orders that is.", "check": {"file": "cancellations.md", "needs": ["%"],
                                         "numbers": 2}},
]

def load() -> list[dict]:
    if not FEATURES.exists():                    # the "initializer" run
        FEATURES.parent.mkdir(exist_ok=True)
        save([{**f, "status": "failing", "attempts": 0} for f in REPORT])
        PROGRESS.write_text("# Progress\n\nCreated the checklist; nothing done yet.\n")
    return json.loads(FEATURES.read_text())

def save(features: list[dict]) -> None:
    tmp = FEATURES.with_suffix(".tmp")           # write-then-rename: never half-written
    tmp.write_text(json.dumps(features, indent=1))
    tmp.replace(FEATURES)

def note(line: str) -> None:
    with PROGRESS.open("a") as f:
        f.write(f"- {time.strftime('%Y-%m-%d %H:%M')} {line}\n")

# ------------------------------------------------------------ 2. checks in code
def check(feature: dict) -> tuple[bool, str]:
    """The model saying "done" isn't evidence. The file is."""
    rule = feature["check"]
    path = FEATURES.parent / rule["file"]
    if not path.exists():
        return False, f"{rule['file']} doesn't exist"
    text = path.read_text()
    missing = [w for w in rule["needs"] if w.lower() not in text.lower()]
    numbers = re.findall(r"\d[\d,.]*", text)
    if missing:
        return False, f"missing {missing}"
    if len(numbers) < rule["numbers"]:
        return False, f"only {len(numbers)} numbers, expected {rule['numbers']}"
    return True, "ok"

# ------------------------------------------------------------ 3. tools
def write_section(name: str, text: str) -> str:
    if not re.fullmatch(r"[a-z_]+\.md", name):
        return "ERROR: name must look like section_name.md"
    (FEATURES.parent / name).write_text(text)
    return f"Wrote {name} ({len(text)} characters)."

WRITE_TOOL = {"name": "write_section", "description":
              "Save one report section as markdown. Use the exact file name you were "
              "given. Include the numbers you found.",
              "input_schema": {"type": "object", "required": ["name", "text"],
                               "properties": {"name": {"type": "string"},
                                              "text": {"type": "string"}}}}
TOOLS = sql.TOOLS + [WRITE_TOOL]

def run_tool(name, args):
    if name == "write_section":
        return write_section(**args)
    return sql.run_tool(name, args)

# ------------------------------------------------------------ 4. one session
def session(max_items: int = 2, max_steps: int = 10, verbose: bool = False) -> dict:
    """Start fresh: read the checklist and the progress notes, work on the first
    failing items one at a time, check each in code, save after each."""
    features = load()
    todo = [f for f in features if f["status"] == "failing"][:max_items]
    recent = "\n".join(PROGRESS.read_text().splitlines()[-12:])
    for f in todo:
        brief = (f"You're writing one section of the weekly sales report.\n"
                 f"Section: {f['task']}\nSave it with write_section as "
                 f"{f['check']['file']!r}.\n\nNotes from earlier sessions:\n{recent}")
        if f["attempts"]:
            brief += f"\n\nLast attempt failed its check: {f.get('why')}. Fix that."
        answer, _, stats = run_agent(brief, TOOLS, run_tool, system=sql.SYSTEM,
                                     max_iterations=max_steps, verbose=verbose)
        ok, why = check(f)
        f["attempts"] += 1
        f["status"] = "passing" if ok else ("needs_human" if f["attempts"] >=
                                            MAX_ATTEMPTS else "failing")
        f["why"] = why
        save(features)                                     # checkpoint after each item
        note(f"{f['id']}: {f['status']} ({why}; {stats['steps']} steps)")
    left = sum(f["status"] == "failing" for f in features)
    return {"worked_on": [f["id"] for f in todo], "left": left,
            "needs_human": [f["id"] for f in features if f["status"] == "needs_human"],
            "done": all(f["status"] == "passing" for f in features)}

if __name__ == "__main__":
    if sys.argv[1:] == ["reset"]:
        for p in FEATURES.parent.glob("*"):
            p.unlink()
        print("Report reset.")
    else:
        print(session(verbose=True))
        print(PROGRESS.read_text())
