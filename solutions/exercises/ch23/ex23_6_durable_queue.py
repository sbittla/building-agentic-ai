"""Exercise 23.6 (solution): the browser queue as a Chapter 19 durable job. Each request
is a step; address changes are run by the agent and verified in code; credits wait
for a person. A crash loses nothing: finished requests stay finished."""
import ch19_durable as d
import ch23_backoffice as app
from ch23_browser import Browser
from ex23_5_verified_queue import run_queue

STATE = {"url": None}

@d.action("change_address", effect="keyed")    # setting a value twice is harmless
def change_address(args, key):
    """One browser per step. The runner runs each step in its own thread, and
    Playwright's objects belong to the thread that created them. It also means a
    resumed job simply signs in again."""
    browser = Browser(STATE["url"])
    try:
        browser.sign_in("agent-bot", app.USERS["agent-bot"])
        result = run_queue(browser, [(args["customer"], args["address"])])[0]
    finally:
        browser.close()
    if result["status"] != "done":
        raise RuntimeError(f"not verified: address is {result['actual']!r}")
    return f"verified: {result['actual']}"

@d.action("issue_credit", effect="unkeyed")
def issue_credit(args, key):
    raise d.Permanent(f"a ${args['amount']:.2f} credit needs a person's approval")

REQUESTS = [
    {"action": "change_address", "args": {"customer": 1, "address": "9 Avenida da "
                                          "Boavista, Porto"}},
    {"action": "change_address", "args": {"customer": 3, "address": "1 Marina Way, "
                                          "Singapore"}},
    {"action": "issue_credit", "args": {"customer": 2, "amount": 50.0}},
]

def main(port: int = 8768, crash_after: int = 1):
    app.reset()
    STATE["url"] = app.serve(port)
    job = d.claim("w1", d.create_job("back-office queue", REQUESTS))
    try:
        d.run_job(job, crash_after=crash_after)
    except d.Crash:
        with d._db() as con:
            con.execute("UPDATE jobs SET lease_until=0 WHERE id=?", (job,))
        d.claim("w2", job)
    status = d.run_job(job, worker="w2")
    print(d.report(job))
    return job, status

if __name__ == "__main__":
    main()
