"""Chapter 24: Agent Skills, the open format (agentskills.io) that Claude Code, the
Claude Agent SDK, the Claude API and a growing list of other agents read. A skill is a
folder with a SKILL.md file: YAML front matter (name, description) and instructions,
plus optional scripts/, references/ and assets/.

The idea is PROGRESSIVE DISCLOSURE: the agent sees only each skill's one-line
description until a task needs it, then reads the instructions, then (maybe) the extra
files. This file validates skills against the specification and gives the chapter 4
agent that same behavior.

Run:  python ch24_skills.py    (creates skills/sql-report if it's missing, then uses it)
"""
import re
from pathlib import Path

SKILLS_DIR = Path("skills")
# lowercase words joined by single hyphens
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

def parse_skill(folder: Path) -> tuple[dict, str]:
    """Read SKILL.md: returns (front matter as a dict, instructions)."""
    text = (folder / "SKILL.md").read_text()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        raise ValueError("SKILL.md must start with YAML front matter between --- lines")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"')
    return meta, m.group(2).strip()

def validate(folder: Path) -> list[str]:
    """Problems with a skill folder, checked against the Agent Skills specification."""
    if not (folder / "SKILL.md").exists():
        return ["missing SKILL.md"]
    try:
        meta, body = parse_skill(folder)
    except ValueError as exc:
        return [str(exc)]
    problems = []
    name, desc = meta.get("name", ""), meta.get("description", "")
    if not name:
        problems.append("name is required")
    elif len(name) > 64 or not NAME_RE.match(name):
        problems.append("name: 1-64 lowercase letters, digits and single hyphens, "
                        "no hyphen at either end")
    elif name != folder.name:
        problems.append(f"name '{name}' must match the folder name '{folder.name}'")
    if not desc:
        problems.append("description is required: "
                        "say what the skill does AND when to use it")
    elif len(desc) > 1024:
        problems.append("description must be at most 1024 characters")
    if len(body.splitlines()) > 500:
        problems.append("keep SKILL.md under 500 lines; move details to references/")
    return problems

def catalog(skills_dir: Path | None = None) -> str:
    """Level 1 of progressive disclosure: one line per skill, for the system prompt."""
    skills_dir, lines = skills_dir or SKILLS_DIR, []
    for folder in sorted(p for p in skills_dir.glob("*") if (p / "SKILL.md").exists()):
        meta, _ = parse_skill(folder)
        lines.append(f"- {meta['name']}: {meta['description']}")
    return "\n".join(lines)

def read_skill(name: str, file: str = "SKILL.md") -> str:
    """Levels 2 and 3: the instructions, or one of the skill's extra files,
    on demand."""
    folder = (SKILLS_DIR / name).resolve()
    target = (folder / file).resolve()
    if (SKILLS_DIR.resolve() not in folder.parents
            or folder not in [target, *target.parents]):
        return "ERROR: that path is outside the skill's folder"
    if not target.is_file():
        return (f"ERROR: no {file} in skill {name}. "
                "Check the catalog in your instructions.")
    return target.read_text()[:20_000]

TOOLS = [{
    "name": "read_skill",
    "description": "Load a skill's instructions (file='SKILL.md') before doing a task "
                   "it covers, or one of the files its instructions mention "
                   "(for example 'references/schema.md').",
    "input_schema": {"type": "object", "properties": {"name": {"type": "string"},
                     "file": {"type": "string", "default": "SKILL.md"}},
                     "required": ["name"]},
}]

def system_prompt(base: str = "You are a helpful analyst.") -> str:
    return (f"{base}\n\nYou have these skills. When a task matches one, "
            f"call read_skill first and follow its instructions:\n{catalog()}")

EXAMPLE = {
    "SKILL.md": """---
name: sql-report
description: Writes a short, well-formatted revenue report from the shop database. Use when the user asks for a report, summary or breakdown of sales, revenue, orders or customers.
---
# SQL revenue report

1. Read `references/schema.md` so you use the right tables and columns.
2. Get the numbers with run_query. Use SUM(quantity * price) for revenue.
3. Write the report in exactly this shape:

## <title>
**Total revenue:** $<amount>
| <group> | Revenue | Share |
(one row per group, largest first, shares adding to 100%)
**Takeaway:** <one sentence>

Never invent numbers: every figure must come from a query in this conversation.
""",
    "references/schema.md": """# Shop database
- customers(id, name, city, joined)
- products(id, name, category, price)
- orders(id, customer_id, order_date, status)
- order_items(order_id, product_id, quantity)
Revenue = SUM(order_items.quantity * products.price), usually for status = 'shipped'.
""",
}

def make_example_skill():
    folder = SKILLS_DIR / "sql-report"
    for rel, text in EXAMPLE.items():
        path = folder / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    return folder

if __name__ == "__main__":
    from ch04_agent import run_agent
    import ch08_sql_tools as sql
    folder = make_example_skill()
    print("Validating", folder, "->", validate(folder) or "OK")
    print("\nCatalog the model sees:\n" + catalog() + "\n")

    def run_tool(name, args):
        return read_skill(**args) if name == "read_skill" else sql.run_tool(name, args)
    answer, _, stats = run_agent("Give me a revenue report by product category.",
                                 TOOLS + sql.TOOLS, run_tool, system=system_prompt())
    print(answer)
