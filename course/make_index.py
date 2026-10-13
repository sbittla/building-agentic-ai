"""Build the book's index from a rendered PDF.

  python3 make_index.py book.pdf        # writes md/92_index.md

The terms are the glossary's (Appendix C) plus a short list of names readers look up. For each
term it finds the printed pages where the term appears in the main matter (Part 0 to the end of
the appendices), groups neighbouring pages into ranges and keeps the six ranges with the most
mentions. Terms that appear on most pages ("agent", "tool") are left out: an index entry with
two hundred pages helps nobody. The index sits after the appendices, so adding it never moves
the pages it points to; build.js prints it, and a second build fills in the Contents.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRA = ["MCP Inspector", "Claude Desktop", "Streamable HTTP", "stdio", "JSON Schema", "pytest",
         "OpenTelemetry", "SQLite", "Docker", "Ollama", "qwen3.5:9b", "LangGraph", "LangChain",
         "Claude Agent SDK", "Managed Agents", "Agent Skills", "tool_choice", "stop_reason",
         "max_tokens", "tool_use_id", "prompt caching", "compaction", "embedding", "reranker",
         "hybrid search", "BM25", "Wilson interval", "pass^k", "p95", "error budget", "burn rate",
         "canary", "shadow", "kill switch", "step-up", "OAuth", "JWT", "SSRF", "canary token",
         "idempotency key", "Little's law", "goodput", "knee", "coordinated omission",
         "Lakeside Insurance", "Bayview Health", "Harbor & Pine", "support agent", "shop.db"]
MAX_SHARE = 0.25          # skip terms found on more than a quarter of the pages
MAX_RANGES = 6


def glossary_terms():
    text = open(os.path.join(HERE, "md", "91_appendix.md"), encoding="utf-8").read()
    block = text[text.index("## Appendix C"):]
    block = block[:block.index("\n## ", 5)]
    terms = []
    for line in block.splitlines():
        m = re.match(r"^\| ([^|]+?) \| [^|]+ \|$", line)
        if m and m.group(1) not in ("Term", "---"):
            terms.append(m.group(1).strip())
    return terms


def variants(term):
    """'Agent card (A2A)' -> ['Agent card (A2A)', 'Agent card'];  plus a simple plural."""
    base = re.sub(r"\s*\([^)]*\)", "", term).strip()
    out = {term, base}
    for t in list(out):
        if re.fullmatch(r"[A-Za-z][A-Za-z -]*[a-z]", t) and not t.endswith("s"):
            out.add(t + "s")
    return sorted((v for v in out if len(v) >= 3), key=len, reverse=True)


def main():
    pdf = os.path.abspath(sys.argv[1])
    text = subprocess.run(["pdftotext", "-layout", pdf, "-"], check=True, capture_output=True,
                          text=True).stdout
    pages = text.split("\f")
    low = [re.sub(r"\s+", " ", p) for p in pages]
    main_start = next(i for i, p in enumerate(pages) if re.search(r"^\s*PART 0\s*$", p, re.M)
                      and "Foundations" in p and "Contents" not in p)
    end = next((i for i, p in enumerate(pages) if re.search(r"^\s*(Index|About the Author)\s*$", p, re.M)
                and i > main_start + 50), len(pages))
    # the glossary itself would appear under every term: leave its pages out
    gl0 = next((i for i in range(main_start, end) if re.search(r"^\s*Appendix C: Glossary\s*$", pages[i], re.M)), None)
    gl1 = next((i for i in range(gl0 or main_start, end) if re.search(r"^\s*Appendix D:", pages[i], re.M)), None)
    skip = set(range(gl0, gl1)) if gl0 is not None and gl1 is not None else set()
    body = [i for i in range(main_start, end) if i not in skip]
    entries = {}
    # one entry per concept: "Compaction" and "compaction", "Agent Skill" and "Agent Skills"
    seen, terms = set(), []
    for term in glossary_terms() + EXTRA:
        key = re.sub(r"\s*\([^)]*\)", "", term).lower().rstrip("s")
        if key not in seen:
            seen.add(key); terms.append(term)
    for term in sorted(terms, key=str.lower):
        pats = [re.compile(r"(?<![\w-])" + re.escape(v) + r"(?![\w-])",
                           0 if any(c.isupper() for c in v[1:]) or len(v) <= 4 else re.I)
                for v in variants(term)]
        hits = {}
        for i in body:
            n = sum(len(p.findall(low[i])) for p in pats)
            if n:
                hits[i - main_start + 1] = n
        if not hits or len(hits) > MAX_SHARE * len(body):
            continue
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
        entries[term] = ", ".join(f"{a}" if a == b else f"{a}–{b}" for a, b, _ in keep)
    lines = ["# Index", "",
             "Page numbers for the terms defined in the glossary (Appendix C) and the names readers look up most. "
             "Where a term appears on many pages, only the pages with the most mentions are listed.", ""]
    letter = None
    for term in sorted(entries, key=lambda t: re.sub(r"[^a-z0-9]", "", t.lower())):
        first = (re.sub(r"[^A-Za-z0-9]", "", term)[:1] or "#").upper()
        first = first if first.isalpha() else "Symbols and numbers"
        if first != letter:
            lines += ["", f"**{first}**", ""]
            letter = first
        shown = term[0].upper() + term[1:] if re.fullmatch(r"[a-z][a-z '\-]*", term) and term not in ("pytest", "stdio") else term
        lines += [f"{shown}, {entries[term]}", ""]
    out = os.path.join(HERE, "md", "92_index.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"{len(entries)} index entries -> {out}")


if __name__ == "__main__":
    main()
