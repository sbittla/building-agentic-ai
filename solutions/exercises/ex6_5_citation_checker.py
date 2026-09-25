"""Exercise 6.5 (Medium): check that every (file:line) citation supports the answer."""
import re
from pathlib import Path

CITATION = re.compile(r"\(([\w./-]+\.\w+):(\d+)\)")
STOP = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "was", "with",
        "it", "at", "by", "from", "as", "that", "this", "be", "are", "were"}

def key_words(sentence: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9][a-z0-9-]+", sentence.lower()) if w not in STOP}

def check_citations(answer: str, root: str = "notes") -> list[dict]:
    """For each sentence with citations, the cited line must share a key word with it."""
    report = []
    for sentence in re.split(r"(?<=[.!?])\s+", answer):
        for path, line_no in CITATION.findall(sentence):
            file = Path(root) / path
            if not file.exists():
                report.append({"citation": f"{path}:{line_no}", "ok": False, "why": "no such file"})
                continue
            lines = file.read_text(errors="ignore").splitlines()
            n = int(line_no)
            if not 1 <= n <= len(lines):
                report.append({"citation": f"{path}:{n}", "ok": False, "why": "no such line"})
                continue
            overlap = key_words(CITATION.sub("", sentence)) & key_words(lines[n - 1])
            report.append({"citation": f"{path}:{n}", "ok": bool(overlap),
                           "why": f"shares {sorted(overlap)[:4]}" if overlap
                           else f"line says: {lines[n - 1][:60]!r}"})
    return report

if __name__ == "__main__":
    import sys
    text = sys.stdin.read() if not sys.stdin.isatty() else (
        "Consumer lag spiked to 2.1M messages (work/2026-06-02-incident-kafka-lag.md:2). "
        "The fix was adding partitions (work/2026-06-02-incident-kafka-lag.md:4). "
        "Kafka 4.1 removes ZooKeeper (personal/recipes.md:2).")
    for row in check_citations(text):
        print(("OK   " if row["ok"] else "BAD  ") + row["citation"], "-", row["why"])
