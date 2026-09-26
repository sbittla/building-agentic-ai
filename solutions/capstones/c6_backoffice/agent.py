"""Capstone 6: the back-office workflow agent (reference architecture).

  * the application   ch23_backoffice: a web app with no API, run locally
  * the hands         ch23_browser: the model sees pages as text and clicks by ref;
                      the harness signs in, keeps to one host, logs and screenshots
  * the queue         ch19_durable: one durable step per request; crash and resume
  * hard controls     code verifies every change; credits never run without a person;
                      the application refuses credits over its own limit

Run:  ./course.sh capstone 6            (creates the queue, then works through it)
      ./course.sh capstone 6 --crash 2  (crash after two requests; run again to resume)"""
import json
import sys
from pathlib import Path

import ch19_durable as durable
import ch23_backoffice as app
from ch23_browser import Browser, run_browser_agent

QUEUE = Path("backoffice_queue.json")
STATE = {"url": None, "approver": None}

def with_browser(fn):
    """One browser per step: steps run in their own threads, and a resumed job simply
    signs in again. The agent never sees the password."""
    browser = Browser(STATE["url"], approver=STATE["approver"])
    try:
        browser.sign_in("agent-bot", app.USERS["agent-bot"])
        return fn(browser)
    finally:
        browser.close()

def read_field(browser: Browser, customer: int, name: str) -> str:
    browser.page.goto(f"{browser.base}/customers/{customer}")
    return browser.page.input_value(f"input[name={name}]")

@durable.action("c6_change_address", effect="keyed")          # setting a value is idempotent
def change_address(args, key):
    def work(browser):
        run_browser_agent(f"Change the address of customer {args['customer']} to "
                          f"exactly: {args['address']}. Open /customers/"
                          f"{args['customer']} to start.", browser, verbose=False)
        return read_field(browser, args["customer"], "address")    # verify in code
    actual = with_browser(work)
    if actual != args["address"]:
        raise RuntimeError(f"not verified: the page shows {actual!r}")
    return f"verified: {actual}"

@durable.action("c6_issue_credit", effect="unkeyed")
def issue_credit(args, key):
    """Money never moves without a person. With nobody to ask, the job escalates."""
    if STATE["approver"] is None:
        raise durable.Permanent(f"a ${args['amount']:.2f} credit needs a person")
    def work(browser):
        before = app.CUSTOMERS[args["customer"]]["credit"]
        run_browser_agent(f"Issue customer {args['customer']} a credit of "
                          f"{args['amount']:.2f} with the reason '{args['reason']}'. "
                          f"Open /customers/{args['customer']} to start.", browser,
                          verbose=False)
        return app.CUSTOMERS[args["customer"]]["credit"] - before
    added = with_browser(work)
    if abs(added - args["amount"]) > 0.001:
        raise durable.Permanent(f"credit not applied (balance changed by {added:.2f})")
    return f"credited {added:.2f}"

def to_steps(requests: list[dict]) -> list[dict]:
    steps = []
    for r in requests:
        if r["kind"] == "address":
            steps.append({"action": "c6_change_address", "args": r})
        else:
            steps.append({"action": "c6_issue_credit", "args": r})
    return steps

def main(argv=(), port: int = 8770, approver=None):
    argv = list(argv)
    crash = int(argv[argv.index("--crash") + 1]) if "--crash" in argv else None
    STATE["url"], STATE["approver"] = app.serve(port), approver
    job = durable.claim("worker-1")                      # resume if a job is unfinished
    if job is None:
        requests = json.loads(QUEUE.read_text())
        job = durable.claim("worker-1", durable.create_job("back-office queue",
                                                             to_steps(requests)))
    try:
        status = durable.run_job(job, crash_after=crash)
    except durable.Crash as exc:
        with durable._db() as con:
            con.execute("UPDATE jobs SET lease_until=0 WHERE id=?", (job,))
        print(f"{exc}. Run again to resume.")
        status = "crashed"
    print(durable.report(job))
    return job, status

if __name__ == "__main__":
    main(sys.argv[1:])
