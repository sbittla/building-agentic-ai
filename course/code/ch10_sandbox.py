"""Chapter 10 (exercise 10.7): run tests in the isolated `sandbox` container.

The sandbox service has NO network, no secrets, and sees your workspace READ-ONLY.
Each job runs in a throwaway copy of its folder, with memory, CPU, file-size and
process limits, and everything it started is killed when it ends. This module hands
it a job through files in /workspace/.sandbox (the only writable folder) and waits
for the result, so model-written code never runs in the container that holds your
API key.   Start the sandbox first:   ./course.sh sandbox up
"""
import json
import time
import uuid
from pathlib import Path

QUEUE = Path("/workspace/.sandbox")

def run_in_sandbox(cmd: list[str], cwd: str = ".", timeout: int = 60) -> str:
    """Run cmd (e.g. ["python", "-m", "pytest", "-q"]) inside the sandbox."""
    job = uuid.uuid4().hex[:12]
    (QUEUE / "requests").mkdir(parents=True, exist_ok=True)
    (QUEUE / "results").mkdir(parents=True, exist_ok=True)
    request = {"id": job, "cmd": cmd, "cwd": str(Path(cwd).resolve()),
               "timeout": timeout}
    tmp = QUEUE / "requests" / f"{job}.tmp"
    tmp.write_text(json.dumps(request))
    tmp.rename(QUEUE / "requests" / f"{job}.json")     # atomic hand-off
    result_file = QUEUE / "results" / f"{job}.json"
    deadline = time.time() + timeout + 15
    while time.time() < deadline:
        if result_file.exists():
            result = json.loads(result_file.read_text())
            result_file.unlink()
            return result["output"]
        time.sleep(0.2)
    return ("ERROR: no answer from the sandbox. Is it running? "
            "Start it on your computer with:  ./course.sh sandbox up")

def run_tests_sandboxed(repo: str = "buggy_repo") -> str:
    """Drop-in replacement for ch10_fixer.run_tests that runs in the sandbox."""
    return run_in_sandbox(["python", "-m", "pytest", "-q", "--tb=short",
                           "-p", "no:cacheprovider"], cwd=repo)

if __name__ == "__main__":
    print(run_tests_sandboxed())
