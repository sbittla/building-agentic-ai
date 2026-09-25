"""Capstone 4: performance test analyst. Writes a markdown report to perf/report.md."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from common import server, ask

CONFIG = {"servers": dict([server("perf", "c4_perf/perfresults_server.py")])}
RULES = {"allow": {"perf": ["list_runs", "load_run", "compare_runs", "release_notes"]},
         "needs_approval": ["perf__start_test"]}
SYSTEM = """You are a performance engineer. Compare the newest run with the previous one using
compare_runs. NEVER compute statistics yourself: quote the numbers the tools return.
Correlate each regression with the release notes. Write the report in markdown:
## Summary, ## Regressions (a table: endpoint, p95 before, p95 after, change, errors),
## Likely causes, ## Suggested next tests."""

def report():
    answer, _ = asyncio.run(ask(CONFIG, "Analyze the latest load test against the previous run.",
                                SYSTEM, RULES))
    Path("perf/report.md").write_text(answer)
    return answer

if __name__ == "__main__":
    print(report())
