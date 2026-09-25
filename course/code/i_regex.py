"""Interlude (regex): regular expressions, one idea at a time."""
import re

log = """2026-09-22 14:05:11 ERROR checkout-service order=A1001 timeout after 800ms
2026-09-22 14:05:12 INFO  search-service query ok
2026-09-22 14:06:40 ERROR checkout-service order=A1002 timeout after 812ms
2026-09-22 14:07:02 WARN  checkout-service retry order=A1002"""

print(re.findall(r"ERROR", log))                    # literal text
print(re.findall(r"\d+ms", log))                    # \d = digit, + = one or more
print(re.findall(r"order=([A-Z]\d+)", log))         # ( ) captures just that part
print(re.findall(r"^\S+ \S+ (ERROR|WARN)", log, re.MULTILINE))   # ^ = line start, | = or
print(bool(re.search(r"timeout", "TIMEOUT", re.IGNORECASE)))     # ignore case
print(re.sub(r"order=\w+", "order=<hidden>", log.splitlines()[0])) # replace

m = re.match(r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>[\d:]+) (?P<level>\w+)", log)
print(m.group("date"), m.group("level"))            # named groups
