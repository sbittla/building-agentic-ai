"""Exercise R.3 (solution): find (file:line) citations in an answer."""
import re

# A path: letters, digits, _ . - and /, and it must contain a dot (a file extension).
CITATION = re.compile(r"\(([\w./-]*\.[\w]+):(\d+)\)")

def citations(text: str) -> list[tuple[str, int]]:
    return [(path, int(line)) for path, line in CITATION.findall(text)]

def main():
    answer = ("The lag came from one partition (work/2026-06-02-incident-kafka-lag.md:3), "
              "fixed in the plan (work/plan.md:12) and (notes.v2/read-me.txt:1). "
              "Not these: (see page 12) or (plan.md) or (12:30).")
    print(citations(answer))

if __name__ == "__main__":
    main()
