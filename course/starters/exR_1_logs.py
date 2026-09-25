import re

LOG = """2026-09-22 14:05:11 ERROR checkout-service order=A1001 timeout after 800ms
2026-09-22 14:05:12 INFO  search-service query ok
2026-09-22 14:06:40 ERROR checkout-service order=A1002 timeout after 812ms
2026-09-22 14:07:02 WARN  checkout-service retry order=A1002"""


def timestamps(log: str) -> list[str]:
    """Every "YYYY-MM-DD HH:MM:SS" at the start of a line."""
    # TODO: re.findall(r"...", log, re.M)   (re.M lets ^ match at each line start)
    raise NotImplementedError


def services(log: str) -> list[str]:
    """The service name on each line, e.g. "checkout-service"."""
    raise NotImplementedError


def latencies(log: str) -> list[int]:
    """Every latency as an integer: [800, 812]."""
    raise NotImplementedError


if __name__ == "__main__":
    print(timestamps(LOG)); print(services(LOG)); print(latencies(LOG))
