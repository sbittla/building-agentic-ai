"""Exercise 30.10: fewer polls, and retries that don't start the work twice.

job_status gets a wait_s parameter: the server holds the call open for up to
wait_s seconds and answers as soon as the job finishes (a "long poll"). An agent
that polls through a model pays for every poll, so this saves real money.
"""
import asyncio
import json
from mcp import Client
import ch30_jobs_server as jobs

MAX_WAIT = 20                                   # keep calls well under client timeouts
check_once = jobs.job_status                    # the original, as a plain function
jobs.mcp.remove_tool("job_status")

@jobs.mcp.tool()
async def job_status(job_id: str, wait_s: int = 0) -> str:
    """Where a job is: working, completed (with its result), input_required or
    cancelled. With wait_s, waits up to that many seconds (max 20) for the job
    to finish."""
    deadline = asyncio.get_running_loop().time() + min(max(wait_s, 0), MAX_WAIT)
    while True:
        answer = json.loads(check_once(job_id))
        if answer["status"] != "working" or \
                asyncio.get_running_loop().time() >= deadline:
            return json.dumps(answer)
        await asyncio.sleep(0.25)

async def run(wait_s: int, request_id: str) -> dict:
    polls = 0
    async with Client(jobs.mcp) as client:
        first = await client.call_tool("start_report", {"month": "2026-04",
                                                        "request_id": request_id})
        retry = await client.call_tool("start_report", {"month": "2026-04",
                                                        "request_id": request_id})
        job = json.loads(first.content[0].text)
        same = job["job_id"] == json.loads(retry.content[0].text)["job_id"]
        while job["status"] == "working":
            polls += 1
            if not wait_s:
                await asyncio.sleep(0.5)
            result = await client.call_tool("job_status", {"job_id": job["job_id"],
                                                           "wait_s": wait_s})
            job = json.loads(result.content[0].text)
    return {"polls": polls, "status": job["status"], "retry_same_job": same}

async def main() -> dict:
    results = {"short polls": await run(0, "ex15-6-a"),
               "long poll": await run(20, "ex15-6-b")}
    for label, r in results.items():
        print(f"{label:<12} {r}")
    return results

if __name__ == "__main__":
    asyncio.run(main())
