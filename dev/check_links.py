"""Check that every external link in the book and the repository docs still answers.

    python dev/check_links.py               # report; exit 1 if any link is broken
    python dev/check_links.py --list        # print the links that would be checked

Runs in CI on a schedule (links rot without anyone touching the repo) and on demand. A site
that refuses automated requests (401, 403, 429) is reported as "blocked", not broken: open
it in a browser before changing the book. Local, internal and example addresses are skipped.
"""
import concurrent.futures as cf
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
SOURCES = sorted((KIT / "course" / "md").glob("*.md")) + sorted(KIT.glob("*.md")) + \
    sorted((KIT / "solutions").glob("*.md"))
URL = re.compile(r"https?://[^\s)<>\"'`|\]]+")
SKIP = re.compile(r"(127\.0\.0\.1|localhost|0\.0\.0\.0|10\.\d+\.\d+\.\d+|169\.254|host\.docker\.internal|"
                  r"\.internal\b|example\.(com|org|net)|\.example\b|//agentic-ai-|//local-adapter|"
                  r"^http://[a-z-]+:\d+|[{<]|your-)")
UA = "Mozilla/5.0 (compatible; building-agentic-ai link check; +https://github.com/sbittla/building-agentic-ai)"


def links() -> dict[str, list[str]]:
    found = {}
    for f in SOURCES:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for u in URL.findall(line):
                u = u.rstrip(".,;:")
                if not SKIP.search(u):
                    found.setdefault(u, []).append(f"{f.relative_to(KIT)}:{n}")
    return found


def status(url: str) -> tuple[str, str]:
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return "ok", str(r.status)
        except urllib.error.HTTPError as e:
            if e.code in (405, 501) and method == "HEAD":
                continue                                   # some servers don't do HEAD
            if e.code in (401, 403, 429):
                return "blocked", str(e.code)
            return "broken", str(e.code)
        except Exception as e:                             # DNS, TLS, timeout
            if method == "HEAD":
                continue
            return "broken", type(e).__name__
    return "broken", "no answer"


def main() -> int:
    found = links()
    if "--list" in sys.argv:
        print("\n".join(sorted(found)))
        return 0
    with cf.ThreadPoolExecutor(16) as pool:
        results = dict(zip(found, pool.map(status, found)))
    broken = {u: r for u, r in results.items() if r[0] == "broken"}
    blocked = {u: r for u, r in results.items() if r[0] == "blocked"}
    for u, (_, why) in sorted(blocked.items()):
        print(f"blocked {why}  {u}")
    for u, (_, why) in sorted(broken.items()):
        print(f"BROKEN  {why}  {u}  ({', '.join(found[u][:3])})")
    print(f"{len(found)} links: {len(found) - len(broken) - len(blocked)} ok, {len(blocked)} blocked, "
          f"{len(broken)} broken")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
