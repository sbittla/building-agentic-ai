"""Exercise 23.5 (solution): a queue of address changes, each verified in code by
reading the page directly, not by trusting the agent's final answer."""
import ch23_backoffice as app
from ch23_browser import Browser, run_browser_agent

QUEUE = [(1, "9 Avenida da Boavista, Porto"), (2, "22 Canal Street, Leeds"),
         (3, "1 Marina Way, Singapore")]

def check_address(browser: Browser, cid: int, expected: str) -> tuple[bool, str]:
    """Code reads the field itself. The agent's claim doesn't count as evidence."""
    browser.page.goto(f"{browser.base}/customers/{cid}")
    actual = browser.page.input_value("input[name=address]")
    return actual == expected, actual

def run_queue(browser: Browser, queue=QUEUE, verbose=False) -> list[dict]:
    results = []
    for cid, address in queue:
        name = app.CUSTOMERS[cid]["name"]
        answer, _, _ = run_browser_agent(f"Change {name}'s address (customer {cid}) to "
                                         f"exactly: {address}", browser, verbose=verbose)
        ok, actual = check_address(browser, cid, address)
        results.append({"customer": cid, "status": "done" if ok else "failed",
                        "expected": address, "actual": actual, "agent_said": answer})
    return results

def main(port: int = 8767):
    app.reset()
    browser = Browser(app.serve(port))
    try:
        browser.sign_in("agent-bot", app.USERS["agent-bot"])
        results = run_queue(browser)
    finally:
        browser.close()
    for r in results:
        print(r["customer"], r["status"], r["actual"])
    return results

if __name__ == "__main__":
    main()
