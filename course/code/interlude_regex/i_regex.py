"""Interlude (regex): regular expressions, one idea at a time."""
import re

log = """2026-09-22 14:05:11 ERROR checkout-service order=A1001 timeout after 800ms
2026-09-22 14:05:12 INFO  search-service query ok
2026-09-22 14:06:40 ERROR checkout-service order=A1002 timeout after 812ms
2026-09-22 14:07:02 WARN  checkout-service retry order=A1002"""

print(re.findall(r"ERROR", log))                    # literal text
print(re.findall(r"\d+ms", log))                    # \d = digit, + = one or more
print(re.findall(r"order=([A-Z]\d+)", log))         # ( ) captures just that part
print(re.findall(r"^\S+ \S+ (ERROR|WARN)", log, re.MULTILINE))  # ^ = line start, | = or
print(bool(re.search(r"timeout", "TIMEOUT", re.IGNORECASE)))    # ignore case
print(re.sub(r"order=\w+", "order=<hidden>", log.splitlines()[0])) # replace

for order_id in ["A1001", "A1001; DROP TABLE"]:    # check a model's tool input
    print(order_id, bool(re.fullmatch(r"[A-Z]\d{4}", order_id)))  # whole text must fit
