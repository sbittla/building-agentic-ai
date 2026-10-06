"""Chapter 30: long-running work over MCP. Start a job, get a handle, poll it.

A tool call should answer in seconds. Work that takes minutes (a report, an export,
a deployment) returns a job id at once and runs in the background, on Chapter 19's
durable runner, so a restart of this server doesn't lose it.

    python ch30_jobs_server.py        # in-process demo, no API key needed
"""
import asyncio
import json
import re
import threading
import time
from mcp import Client
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
import ch19_durable as durable
import ch08_sql_tools as sql

mcp = MCPServer("reports", instructions="Monthly sales reports. They take a while: "
                "start one, then check on it with job_status.")

# ------------------------------------------------------------ the work itself
@durable.action("sales_query")
def sales_query(args, key):
    return sql.run_query(
        "SELECT p.category, ROUND(SUM(oi.quantity * p.price), 2) AS revenue "
        "FROM orders o JOIN order_items oi ON oi.order_id = o.id "
        "JOIN products p ON p.id = oi.product_id "
        f"WHERE o.status != 'cancelled' AND strftime('%Y-%m', o.order_date) = "
        f"'{args['month']}' GROUP BY p.category ORDER BY revenue DESC")

@durable.action("render")
def render(args, key):
    time.sleep(args.get("seconds", 2))          # stands in for slow work
    return f"Sales report for {args['month']}\n{args['rows']}"

def _worker(job_id: str):
    if durable.claim("reports-server", job_id):
        durable.run_job(job_id, worker="reports-server")

# ------------------------------------------------------------ the MCP tools
@mcp.tool()
def start_report(month: str, request_id: str = "") -> str:
    """Start building the sales report for a month (YYYY-MM). Returns at once with
    a job id; call job_status with it. Pass the same request_id when retrying so
    the report isn't built twice."""
    if not re.fullmatch(r"\d{4}-\d{2}", month):   # it goes into SQL: check it
        raise ToolError("month must look like 2026-03")
    goal = f"report {month} {request_id}".strip()
    with durable._db() as con:                  # same request_id -> same job
        old = con.execute("SELECT id FROM jobs WHERE goal=? AND status != "
                          "'compensated'", (goal,)).fetchone() if request_id else None
    job_id = old["id"] if old else durable.create_job(goal, [
        {"action": "sales_query", "args": {"month": month}},
        {"action": "render", "args": {"month": month, "rows": "$1"}}])
    threading.Thread(target=_worker, args=(job_id,), daemon=True).start()
    return json.dumps({"job_id": job_id, "status": "working",
                       "poll_interval_ms": 2000})

# Durable-runner states, in the vocabulary of MCP's Tasks extension
STATUS = {"queued": "working", "running": "working", "done": "completed",
          "needs_human": "input_required", "compensated": "cancelled"}

@mcp.tool()
def job_status(job_id: str) -> str:
    """Where a job is: working, completed (with its result), input_required (a
    person must decide something) or cancelled."""
    with durable._db() as con:
        job = con.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if job is None:
            raise ToolError(f"no job {job_id}")
        steps = con.execute("SELECT status, result FROM steps WHERE job_id=? "
                            "ORDER BY idx", (job_id,)).fetchall()
    done = sum(s["status"] == "done" for s in steps)
    status = STATUS[job["status"]]
    answer = {"job_id": job_id, "status": status, "progress": f"{done}/{len(steps)}"}
    if status == "completed":
        answer["result"] = steps[-1]["result"]
    elif status == "input_required":
        answer["note"] = job["note"]
    elif status == "working":
        answer["poll_interval_ms"] = 2000
    return json.dumps(answer)

def resume_unfinished():
    """On start-up, pick up jobs a crashed or restarted server left behind."""
    while job_id := durable.claim("reports-server"):
        threading.Thread(target=durable.run_job, args=(job_id, "reports-server"),
                         daemon=True).start()

# ------------------------------------------------------------ demo
async def main():
    async with Client(mcp) as client:
        started = await client.call_tool("start_report", {"month": "2026-03",
                                                          "request_id": "demo-1"})
        job = json.loads(started.content[0].text)
        print("started:", job)
        while job["status"] == "working":
            await asyncio.sleep(job["poll_interval_ms"] / 1000)
            status = await client.call_tool("job_status", {"job_id": job["job_id"]})
            job = json.loads(status.content[0].text)
            print("status: ", job["status"], job["progress"])
        print(job.get("result") or job)

if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["stdio"]:
        resume_unfinished()
        mcp.run(transport="stdio")
    else:
        asyncio.run(main())
