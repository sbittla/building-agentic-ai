"""Exercise 25.5 (solution): five ways to sneak the canary past the leak scan, and a
scan that normalizes before it searches."""
import base64
import binascii
import json
import re
from urllib.parse import unquote

import ch25_guards as g

def evasions(canary: str) -> dict:
    half = len(canary) // 2
    return {
        "base64": {"url": "https://x.example/?d=" + base64.b64encode(canary.encode())
                   .decode()},
        "split": {"part1": canary[:half], "part2": canary[half:]},
        "reversed": {"note": canary[::-1]},
        "url-encoded": {"q": "".join(f"%{ord(c):02X}" for c in canary)},
        "spaced": {"text": " ".join(canary)},
    }

ORDINARY = [{"path": "notes/meeting.md"}, {"url": "https://docs.python.org/3/"},
            {"sql": "SELECT COUNT(*) FROM orders"}, {"text": "Revenue grew 12% in Q3."},
            {"title": "Plan a promotion in Leeds"}]

def _decodings(text: str):
    yield text
    yield unquote(text)
    for chunk in re.findall(r"[A-Za-z0-9+/]{12,}={0,2}", text):   # looks like base64
        try:
            yield base64.b64decode(chunk + "=" * (-len(chunk) % 4)).decode("utf-8", "ignore")
        except (binascii.Error, ValueError):
            pass

def strong_scan(value) -> list[str]:
    parts = list(value.values()) if isinstance(value, dict) else [value]
    joined = "".join(str(p) for p in parts)             # catches a split canary
    texts = [json.dumps(value), joined]
    target = re.sub(r"\W", "", g.CANARY).lower()
    for text in texts:
        for decoded in _decodings(text):
            flat = re.sub(r"\W", "", decoded).lower()    # drops spaces and punctuation
            if target in flat or target in flat[::-1]:
                return ["canary"]
    return g.scan(value)

def main():
    caught = {name: bool(strong_scan(args)) for name, args in
              evasions(g.CANARY).items()}
    missed_before = [name for name, args in evasions(g.CANARY).items() if not g.scan(args)]
    false_alarms = [a for a in ORDINARY if strong_scan(a)]
    print("caught:", caught, "\nmissed by the original scan:", missed_before,
          "\nfalse alarms:", false_alarms)
    return caught, missed_before, false_alarms

if __name__ == "__main__":
    main()
