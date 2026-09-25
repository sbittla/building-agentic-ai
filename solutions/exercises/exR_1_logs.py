"""Exercise R.1 (solution): pull fields out of a log with regular expressions."""
import re

LOG = """2026-09-22 14:05:11 ERROR checkout-service order=A1001 timeout after 800ms
2026-09-22 14:05:12 INFO  search-service query ok
2026-09-22 14:06:40 ERROR checkout-service order=A1002 timeout after 812ms
2026-09-22 14:07:02 WARN  checkout-service retry order=A1002"""

def timestamps(log: str) -> list[str]:
    return re.findall(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", log, re.M)

def services(log: str) -> list[str]:
    # the word after the level; \s+ absorbs the padding after "INFO"
    return re.findall(r"^\S+ \S+ \w+\s+([\w-]+)", log, re.M)

def latencies(log: str) -> list[int]:
    return [int(n) for n in re.findall(r"(\d+)ms\b", log)]

def main():
    print(timestamps(LOG))
    print(services(LOG))
    print(latencies(LOG))            # [800, 812]

if __name__ == "__main__":
    main()
