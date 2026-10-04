"""Fill in the Contents page numbers.

build.js writes toc_headings.json (every heading in the Contents, in order) and puts "000" in the
Contents until toc_pages.json exists. This script renders the .docx to PDF with LibreOffice, finds
the page each heading lands on, and writes toc_pages.json; build again to print the numbers.

  node build.js out.docx && python3 make_toc.py out.docx && node build.js out.docx

Front matter is numbered i, ii, ... from the half-title; the main matter restarts at 1 on the
Part 0 opener, exactly as build.js numbers the pages.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def roman(n):
    out = ""
    for v, s in ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
                 (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")):
        while n >= v:
            out += s; n -= v
    return out


def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("—", "-").replace("–", "-")).strip().lower()


def matches(lines, want):
    """A heading is a line of its own; a long one may wrap onto the next line or two."""
    for k, l in enumerate(lines):
        if l == want:
            return True
        if len(l) >= 15 and want.startswith(l):
            joined = l
            for nxt in lines[k + 1:k + 3]:
                joined += " " + nxt
                if joined == want:
                    return True
                if not want.startswith(joined):
                    break
    return False


def main():
    docx = os.path.abspath(sys.argv[1])
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, docx],
                       check=True, capture_output=True)
        pdf = os.path.join(tmp, os.path.splitext(os.path.basename(docx))[0] + ".pdf")
        text = subprocess.run(["pdftotext", "-layout", pdf, "-"], check=True, capture_output=True,
                              text=True).stdout
    pages = [[norm(l) for l in p.splitlines() if l.strip()] for p in text.split("\f")]
    headings = json.load(open(os.path.join(HERE, "toc_headings.json")))

    # where the main matter starts: the Part 0 opener ("PART 0" alone on a line)
    main_start = next(i for i, p in enumerate(pages) if "part 0" in p and "foundations" in p
                      and not any("contents" == l for l in p))
    # skip the Contents pages themselves: pages full of "title ..... 123" lines
    toc_line = re.compile(r"\.{4,}\s*(\d+|[ivxlc]+)$")
    contents_end = max(i for i, p in enumerate(pages[:main_start]) if sum(bool(toc_line.search(l)) for l in p) >= 5)

    result, cursor, missing = {}, contents_end + 1, []
    for h in headings:
        if h.get("noToc"):
            continue
        want = norm(h["find"])
        found = None
        for i in range(cursor, len(pages)):
            if matches(pages[i], want):
                found = i
                break
        if found is None:
            missing.append(h["text"])
            continue
        cursor = found + 1 if h["level"] == 0 else found   # a part opener is a page of its own
        result[h["id"]] = str(found - main_start + 1) if found >= main_start else roman(found + 1)
    json.dump(result, open(os.path.join(HERE, "toc_pages.json"), "w"), indent=1)
    print(f"{len(result)} page numbers written; {len(missing)} headings not found")
    for m in missing[:20]:
        print("  not found:", m)


if __name__ == "__main__":
    main()
