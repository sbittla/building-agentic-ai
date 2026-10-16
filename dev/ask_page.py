"""The "Ask Building Agentic AI Systems" reader page: docs/ask/index.html.

    python dev/ask_page.py           # write docs/ask/index.html
    python dev/ask_page.py --check   # exit 1 if it is out of date (CI runs this)

The page answers questions from the book's chapter summaries: titles, section headings and key
takeaways for every chapter and interlude, the capstones' core features, the case study's
requirements and each appendix's opening. All of it is read from the manuscript, so the page
can't drift from the book; the design and script live in dev/ask_template.html. Without Claude
(any static host, such as GitHub Pages) it shows the chapters that match a question; inside a
Claude artifact it can also write an answer from the same material.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curriculum_map import book_order   # chapter and interlude files in printed order

KIT = Path(__file__).resolve().parent.parent
MD = KIT / "course" / "md"
TEMPLATE = KIT / "dev" / "ask_template.html"
OUT = KIT / "docs" / "ask" / "index.html"
COSTS = json.loads((KIT / "course/cost.json").read_text(encoding="utf-8"))
EXERCISES = json.loads((KIT / "course/exercises.json").read_text(encoding="utf-8"))
INTERLUDE = {"00zz_python.md": "P", "01z_testing.md": "T", "05z_regex.md": "R",
             "07z_sql.md": "S", "08z_measure.md": "M", "10z_async.md": "A"}
WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()
STANDARD = re.compile(r"^(Learning objectives|Common mistakes|Before you move on|Key takeaways|Learn more|"
                      r"Exercises|Up next|Checkpoint|Summary)")


def plain(s: str) -> str:
    """Markdown inline -> text: links, bold, italics and code marks removed, {{cost}} resolved."""
    s = re.sub(r"\{\{cost:([\w-]+)\}\}", lambda m: COSTS[m.group(1)], s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"\*\*(.+?)\*\*|\*(.+?)\*|`([^`]+)`", lambda m: next(g for g in m.groups() if g), s)
    return re.sub(r"\s+", " ", s).strip()


def section(text: str, heading: str, level: str = "##") -> str:
    """The body of the first heading that starts with `heading`, up to the next heading of that level."""
    m = re.search(rf"^{level} {re.escape(heading)}.*?$(.*?)(?=^{level} |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def bullets(body: str) -> list[str]:
    return [plain(b) for b in re.findall(r"^- (.+)$", body, re.M)]


def sentences(text: str, n: int) -> list[str]:
    """The first n sentences of the first prose paragraph, skipping any that hold a placeholder."""
    para = next((p for p in re.split(r"\n\s*\n", text)
                 if p.strip() and not p.lstrip().startswith(("#", "|", "-", ":::", "```", "Table:", "@@", ">"))), "")
    out, start, text = [], 0, plain(para)
    for m in re.finditer(r"(?<=[.!?])\s+(?=[A-Z])", text):
        if text.count('"', 0, m.start()) % 2 == 0:      # don't split inside a quotation
            out.append(text[start:m.start()]); start = m.end()
    out.append(text[start:])
    return [s for s in out if s and "{{" not in s][:n]


def chapter(f: str) -> dict:
    text = (MD / f).read_text(encoding="utf-8")
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    if f in INTERLUDE:
        label = f"Interlude {INTERLUDE[f]}"
        title = title.removeprefix("Interlude: ")
        secs = [re.sub(r"^[A-Z]\.\d+ ", "", h) for h in re.findall(r"^## (.+)$", text, re.M)
                if not STANDARD.match(h)]
    else:
        num, title = re.match(r"Chapter (\d+): (.+)", title).groups()
        label = f"Chapter {num}"
        secs = re.findall(rf"^## {num}\.\d+ (.+)$", text, re.M)
    takeaways = bullets(section(text, "Key takeaways"))
    if not takeaways:
        raise SystemExit(f"{f}: no Key takeaways list")
    return {"id": label.split()[0][:3].lower().replace("cha", "ch") + label.split()[1],
            "label": label, "title": plain(title), "sections": [" · ".join(plain(s) for s in secs)],
            "takeaways": takeaways}


def case_study() -> dict:
    text = (MD / "89_case_study.md").read_text(encoding="utf-8")
    title = re.search(r"^# Case Study: (.+)$", text, re.M).group(1)
    intro = text[text.index("\n", text.index("# Case Study")):]
    return {"id": "case", "label": "Case study", "title": plain(title),
            "sections": [" · ".join(plain(h) for h in re.findall(r"^## (.+)$", text, re.M))],
            "takeaways": sentences(intro, 2) + bullets(section(text, "The requirements"))}


def capstones() -> list[dict]:
    text = (MD / "90_capstones.md").read_text(encoding="utf-8")
    out = []
    for num, title in re.findall(r"^## Capstone (\d+): (.+)$", text, re.M):
        body = section(text, f"Capstone {num}:")
        scenario = re.search(r"^\*\*Scenario\.\*\* (.+)$", body, re.M)
        features = re.search(r"^\*\*Core features\*\*\s*\n(.*?)(?=^\*\*|\Z)", body, re.M | re.S)
        parts = [p.rstrip(":") for p in re.findall(r"^\*\*([^*.]+)\.?\*\*", body, re.M)]
        out.append({"id": f"cap{num}", "label": f"Capstone {num}", "title": plain(title),
                    "sections": [" · ".join(parts)],
                    "takeaways": (sentences(scenario.group(1), 2) if scenario else [])
                                 + (bullets(features.group(1)) if features else [])})
    return out


def appendices() -> list[dict]:
    text = (MD / "91_appendix.md").read_text(encoding="utf-8")
    out = []
    for letter, title in re.findall(r"^## Appendix ([A-Z]): (.+)$", text, re.M):
        body = section(text, f"Appendix {letter}:")
        subs = [plain(h) for h in re.findall(r"^### (.+)$", body, re.M)]
        # the glossary is a table: every "term: meaning" row is something a reader may ask about
        rows = re.findall(r"^\| (?!Term \||---)([^|]+?) \| (.+?) \|$", body, re.M) if title == "Glossary" else []
        takeaways = [f"{plain(t)}: {plain(m)}" for t, m in rows] or sentences(body, 3) or bullets(body)[:6]
        out.append({"id": f"app{letter}", "label": f"Appendix {letter}", "title": plain(title),
                    "sections": [" · ".join(subs) or plain(title)], "takeaways": takeaways})
    return out


def render() -> str:
    files = book_order()
    kb = [chapter(f) for f in files] + [case_study()] + capstones() + appendices()
    n_ch = sum(f not in INTERLUDE for f in files)
    n_int = sum(f in INTERLUDE for f in files)
    n_cap = sum(k["label"].startswith("Capstone") for k in kb)
    n_ex = len(EXERCISES)
    tags = "".join(f'<span class="tag">{t}</span>' for t in
                   (f"{n_ch} chapters", f"{n_int} interludes", f"{n_ex} exercises", f"{n_cap} capstones"))
    page = TEMPLATE.read_text(encoding="utf-8")
    for key, value in {"__TAGS__": tags,
                       "__CONTENTS__": f"{n_ch} chapters, {n_int} interludes, a case study, {n_cap} capstones and appendices",
                       "__EXERCISES__": str(n_ex), "__CAPSTONES_WORD__": WORDS[n_cap],
                       "__KB__": json.dumps(kb, ensure_ascii=False).replace("</", r"<\/")}.items():   # inside <script>
        if key not in page:
            raise SystemExit(f"{TEMPLATE.name}: placeholder {key} missing")
        page = page.replace(key, value)
    return page


def main() -> None:
    page = render()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != page:
            sys.exit(f"{OUT.relative_to(KIT)} is out of date: run python dev/ask_page.py")
        print("OK: ask page current")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(KIT)}")


if __name__ == "__main__":
    main()
