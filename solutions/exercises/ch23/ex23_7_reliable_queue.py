"""Exercise 23.7 (solution): a queue of back-office requests run through the reliable
action wrapper (section 23.9), with faults injected, a hand-off and a resume.

Faults: a control that's missing for one read (request 1), a credit click that times
out without landing (request 3) and a session that expires before request 4. Offline:
no Chromium, no model."""
import ch23_backoffice as app
from ch23_reliability import (ActionLog, OfflineBrowser, address_steps, credit_steps,
                              run_steps, sign_in)

QUEUE = [
    {"id": 1, "kind": "address", "customer": 1, "value": "9 Avenida da Boavista, Porto"},
    {"id": 2, "kind": "address", "customer": 2, "value": "22 Canal Street, Leeds"},
    {"id": 3, "kind": "credit", "customer": 3, "value": 20.0, "reason": "late parcel"},
    {"id": 4, "kind": "address", "customer": 3, "value": "1 Marina Way, Singapore"},
]

def steps_for(req: dict):
    if req["kind"] == "address":
        return address_steps(req["customer"], req["value"])
    return credit_steps(req["customer"], req["value"], req["reason"])

def run_queue(browser, queue, status: dict, log: ActionLog, faults=None) -> dict:
    """Skip requests already done or waiting for a person. A lost session stops the
    queue (every later request would fail the same way); anything else that needs a
    person is parked and the queue moves on."""
    faults = faults or {}
    for req in queue:
        if status.get(req["id"]) in ("done", "needs_human"):
            continue
        if fault := faults.get(req["id"]):
            fault(browser)
        start = len(log.entries)
        status[req["id"]] = run_steps(browser, steps_for(req), log)[-1][1]
        if any(e["event"] == "handoff" for e in log.entries[start:]):
            status[req["id"]] = "session_lost"          # not the request's fault: rerun
            break
    return status

def main(verbose: bool = True) -> dict:
    app.reset()
    app.SESSIONS.clear()
    browser = OfflineBrowser(approver=lambda a: True)      # a person approved the credit
    sign_in(browser)
    log, status = ActionLog(), {}
    faults = {1: lambda b: setattr(b.page, "missing", 1),
              3: lambda b: setattr(b.page, "click_fault", "before"),
              4: lambda b: app.SESSIONS.clear()}
    first = dict(run_queue(browser, QUEUE, status, log, faults))
    sign_in(browser)                                       # the person signs in again
    second = dict(run_queue(browser, QUEUE, status, log))
    browser.close()
    out = {"first_run": first, "after_resume": second,
           "address_writes": sum(1 for a in app.AUDIT if a[3] == "address"),
           "credits": sum(1 for a in app.AUDIT if a[3] == "credit"),
           "chen_balance": app.CUSTOMERS[3]["credit"],
           "snapshots": len(log.snapshots), "log": log.entries}
    if verbose:
        print("first run:   ", first)
        print("after resume:", second)
        print(f"address writes: {out['address_writes']}, credits issued: "
              f"{out['credits']}, Chen's balance ${out['chen_balance']:.2f}")
        print(f"evidence: {len(log.entries)} log entries, {out['snapshots']} snapshots")
        for e in log.entries:
            if e["event"] in ("stale", "error", "unverified; not retried", "handoff"):
                print(f"  {e['step']:<16} {e['event']:<24} {e['detail'][:50]}")
    return out

if __name__ == "__main__":
    main()
