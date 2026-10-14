"""Build the book's index from a rendered PDF and the curated term list.

  python3 make_index.py book.pdf        # writes md/92_index.md

The terms, their search patterns, the chapters where each sense is taught, sub-entries and
cross-references live in index_terms.json, curated by hand so that "canary release" and
"canary token", or MCP tasks and to-do tasks, are separate entries. This script only finds
pages. It reads the Contents to learn which printed pages belong to which chapter, matches
each pattern on the pages of the chapters the entry names, groups neighbouring pages into
ranges and keeps the ranges with the most mentions. The index sits after the appendices, so
adding it never moves the pages it points to; build.js prints it, and the next build fills
in the Contents.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "md")
MAX_RANGES = 6
CODES = {"00z_ch00": "0", "00zz_python": "P", "01z_testing": "T", "05z_regex": "R", "07z_sql": "S",
         "08z_measure": "M", "10z_async": "A", "89_case_study": "CS", "90_capstones": "CAP",
         "90z_afterword": "AFT", "91_appendix": "APP"}


def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"')).strip()


def chapter_titles():
    """[(code, title)] for every chapter-like file, from its '# ' heading."""
    out = []
    for f in sorted(os.listdir(MD)):
        stem = f[:-3]
        if not f.endswith(".md") or not (stem in CODES or re.fullmatch(r"\d\d", stem)):
            continue
        title = re.search(r"^# (.+)$", open(os.path.join(MD, f), encoding="utf-8").read(), re.M).group(1)
        out.append((CODES[stem] if stem in CODES else str(int(stem)), norm(title)))
    return out


def page_chapters(pages, main_start):
    """Printed page number -> chapter code, from the Contents' start pages."""
    toc = "\n".join(pages[:main_start])
    toc_lines = [norm(l) for l in toc.splitlines()]
    starts = []
    for code, title in chapter_titles():
        for l in toc_lines:
            m = re.match(re.escape(title[:45]) + r".*?\.{3,}\s*(\d+)$", l)
            if m:
                starts.append((int(m.group(1)), code))
                break
    starts.sort()
    end = next((int(m.group(1)) for l in toc_lines for m in [re.match(r"Index\.{3,}\s*(\d+)$", l)] if m), 10 ** 6)
    owner = {}
    for (p, code), nxt in zip(starts, starts[1:] + [(end, None)]):
        for q in range(p, nxt[0]):
            owner[q] = code
    return owner


def scope(spec):
    if not spec:
        return None
    out = set()
    for part in spec.split(","):
        part = part.strip()
        m = re.fullmatch(r"(\d+)-(\d+)", part)
        out |= {str(i) for i in range(int(m.group(1)), int(m.group(2)) + 1)} if m else {part}
    return out


def find(entry, texts, owner):
    pats = [re.compile(p) for p in entry.get("patterns", [])]
    allowed = scope(entry.get("chapters"))
    hits = {}
    for pg, text in texts.items():
        if allowed is not None and owner.get(pg) not in allowed:
            continue
        n = sum(len(p.findall(text)) for p in pats)
        if n:
            hits[pg] = n
    if not hits:
        return ""
    ranges, start, prev, count = [], None, None, 0
    for pg in sorted(hits):
        if prev is not None and pg == prev + 1:
            prev, count = pg, count + hits[pg]
            continue
        if start is not None:
            ranges.append((start, prev, count))
        start, prev, count = pg, pg, hits[pg]
    ranges.append((start, prev, count))
    keep = sorted(sorted(ranges, key=lambda r: -r[2])[:MAX_RANGES])
    return ", ".join(f"{a}" if a == b else f"{a}–{b}" for a, b, _ in keep)


def main():
    pdf = os.path.abspath(sys.argv[1])
    raw = subprocess.run(["pdftotext", "-layout", pdf, "-"], check=True, capture_output=True,
                         text=True).stdout.split("\f")
    main_start = next(i for i, p in enumerate(raw) if re.search(r"^\s*PART 0\s*$", p, re.M)
                      and "Foundations" in p and "Contents" not in p)
    owner = page_chapters(raw, main_start)
    last = max(owner) if owner else len(raw)
    texts = {i - main_start + 1: norm(raw[i]) for i in range(main_start, len(raw)) if i - main_start + 1 <= last}
    # the glossary would match every term: leave its pages out
    g0 = next((pg for pg, tx in texts.items() if owner.get(pg) == "APP" and "Appendix C: Glossary" in tx), None)
    g1 = next((pg for pg, tx in texts.items() if g0 and pg >= g0 and "Appendix D:" in tx), None)
    if g0 and g1:
        for pg in range(g0, g1):
            texts.pop(pg, None)
    terms = json.load(open(os.path.join(HERE, "index_terms.json"), encoding="utf-8"))
    rows = []
    for e in terms:
        if "see" in e:
            rows.append((e["term"], f"*see* {e['see']}", []))
            continue
        pages = find(e, texts, owner)
        subs = []
        for s in e.get("sub", []):
            sp = find(s, texts, owner)
            if sp:
                subs.append((s["term"], sp))
        see_also = e.get("see_also") or []
        if pages or subs:
            line = pages + (f"; *see also* {', '.join(see_also)}" if see_also else "")
            rows.append((e["term"], line, subs))
    rows.sort(key=lambda r: re.sub(r"[^a-z0-9]", "", r[0].lower()))
    lines = ["# Index", "",
             "Where a term appears on many pages, the pages with the most mentions are listed. "
             "Definitions of most terms are also in the glossary (Appendix C).", ""]
    letter = None
    for term, line, subs in rows:
        first = (re.sub(r"[^A-Za-z0-9]", "", term)[:1] or "#").upper()
        first = first if first.isalpha() else "Symbols and numbers"
        if first != letter:
            lines += [f"**{first}**", ""]
            letter = first
        lines += [f"{term}, {line}".replace(", ;", ";").rstrip(", "), ""]
        for st, sp in subs:
            lines += [f"\u2003\u2003{st}, {sp}", ""]
    open(os.path.join(MD, "92_index.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"{len(rows)} entries, {sum(len(r[2]) for r in rows)} sub-entries -> md/92_index.md")


if __name__ == "__main__":
    main()
