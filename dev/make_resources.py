"""Dev tool: write RESOURCES.md (every link in the book, ready to click) from the book's
markdown: Appendix G's three lists first, then every Learn more table in book order.
Safe to rerun.   python dev/make_resources.py course/md"""
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
MD = Path(sys.argv[1]) if len(sys.argv) > 1 else KIT / "course/md"
ORDER = ["00_front.md", "00z_ch00.md", "00zz_python.md", "01.md", "01z_testing.md", "02.md", "03.md",
         "04.md", "05.md", "05z_regex.md", "06.md", "07.md", "07z_sql.md", "08.md", "08z_measure.md",
         "09.md", "10.md", "10z_async.md", "11.md", "12.md", "13.md", "14.md", "15.md", "16.md",
         "17.md", "18.md", "19.md", "20.md", "21.md", "22.md", "23.md", "24.md", "25.md", "26.md",
         "27.md", "28.md", "29.md", "30.md", "90_capstones.md"]
ROW = re.compile(r"^\| \*\*(.+?)\*\*<br>\[[^\]]*\]\(([^)]+)\) \| (.+?) \| (Start here|Go deeper) \|$")

def rows(text):
    return [ROW.match(l).groups() for l in text.splitlines() if ROW.match(l)]

out = ["# Where to learn more", "",
       "Every link from the book's **Learn more** sections and Appendix G, so you can click them. "
       "Checked September 2026.", ""]
appendix = (MD / "91_appendix.md").read_text(encoding="utf8")
g = appendix[appendix.index("## Appendix G"):appendix.index("### Every link in this book")]
for title, label in [("When you're stuck: where to ask", "When you're stuck: where to ask"),
                     ("Free courses that pair well with this book", "Free courses"),
                     ("Keeping up to date", "Keeping up to date")]:
    part = g[g.index(f"### {title}"):]
    part = part[:part.index("\n### ", 5)] if "\n### " in part[5:] else part
    out += [f"## {label}", ""] + [f"- **[{t}]({u})**: {w}" for t, u, w, _ in rows(part)] + [""]
for f in ORDER:
    path = MD / f
    if not path.exists():
        continue
    text = path.read_text(encoding="utf8")
    m = re.search(r"^## Learn more\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    found = rows(m.group(1)) if m else []
    if found:
        out += [f"## {re.search(r'^# (.+)$', text, re.M).group(1).strip()}", ""]
        out += [f"- [{t}]({u}) ({lvl}): {w}" for t, u, w, lvl in found] + [""]
(KIT / "RESOURCES.md").write_text("\n".join(out), encoding="utf8")
print("wrote RESOURCES.md")
