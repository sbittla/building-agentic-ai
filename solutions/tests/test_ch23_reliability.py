"""Chapter 23.9: reliability engineering for computer use. Offline: the back office
runs in-process and OfflinePage stands in for Chromium."""
import re

import pytest


@pytest.fixture
def rel(ws):
    pytest.importorskip("playwright")                  # ch23_browser imports it
    import ch23_backoffice as app
    import ch23_reliability as r
    app.reset()
    app.SESSIONS.clear()
    yield r
    app.reset()
    app.SESSIONS.clear()


def browser(rel, approve=True):
    b = rel.OfflineBrowser(approver=lambda a: approve)
    rel.sign_in(b)
    return b


def credits():
    import ch23_backoffice as app
    return [a for a in app.AUDIT if a[3] == "credit"]


def test_the_offline_page_looks_like_the_real_one_to_browser(rel):
    b = browser(rel)
    page = b.open("/customers/2")
    assert '<page_text untrusted="true">' in page and '[e5] button "Issue credit"' in page
    assert '[e1] textbox "Address" value="18 Mill Lane, Leeds"' in page
    assert b.open("https://attacker.example/").startswith("ERROR: only")


def test_stale_controls_are_retried_after_a_fresh_read(rel):
    import ch23_backoffice as app
    b, log = browser(rel), rel.ActionLog()
    b.page.missing = 2
    out = rel.run_steps(b, rel.address_steps(1, "9 Avenida da Boavista, Porto"), log)
    assert [s for _, s in out] == ["done", "done", "done"]
    assert [e["event"] for e in log.entries].count("stale") == 2
    assert app.CUSTOMERS[1]["address"] == "9 Avenida da Boavista, Porto"


def test_retries_are_bounded(rel):
    import ch23_backoffice as app
    b, log = browser(rel), rel.ActionLog()
    b.page.missing = 99
    out = rel.run_steps(b, rel.address_steps(1, "Nowhere"), log)
    assert out[-1] == ("type address 1", "failed") and log.entries[-1]["event"] == "gave up"
    assert app.CUSTOMERS[1]["address"] == "4 Rua Nova, Porto"


def test_a_failed_precondition_never_acts(rel):
    import ch23_backoffice as app
    b, log = browser(rel), rel.ActionLog()
    b.open("/customers/1")
    step = rel.Step("save", "click", "Save address",
                    before=rel.field_is("Address", "something else"))
    assert rel.run_step(b, step, log) == "failed"
    assert not app.AUDIT and "precondition not met" in [e["event"] for e in log.entries]


def test_a_credit_that_landed_is_verified_not_repeated(rel):
    import ch23_backoffice as app
    b, log = browser(rel), rel.ActionLog()
    steps = rel.credit_steps(3, 20, "late parcel")
    rel.run_steps(b, steps[:3], rel.ActionLog())
    b.page.click_fault = "after"
    assert rel.run_step(b, steps[3], log) == "done"
    assert len(credits()) == 1 and app.CUSTOMERS[3]["credit"] == 45.0


def test_an_unclear_credit_goes_to_a_person_and_is_never_retried(rel):
    import ch23_backoffice as app
    b, log = browser(rel), rel.ActionLog()
    steps = rel.credit_steps(3, 20, "late parcel")
    rel.run_steps(b, steps[:3], rel.ActionLog())
    b.page.click_fault = "before"
    assert rel.run_step(b, steps[3], log) == "needs_human"
    assert not credits() and app.CUSTOMERS[3]["credit"] == 25.0
    assert max(e["attempt"] for e in log.entries) == 1           # one try only
    assert log.entries[-1]["event"] == "unverified; not retried"


def test_refusals_are_not_retried(rel):
    b, log = browser(rel, approve=False), rel.ActionLog()
    steps = rel.credit_steps(3, 20, "late parcel")
    out = rel.run_steps(b, steps, log)
    assert out[-1] == ("issue credit 3", "refused") and not credits()
    assert sum(1 for _, what in b.log if what.startswith("refused")) == 1


def test_session_expiry_and_mfa_hand_over_to_a_person(rel):
    import ch23_backoffice as app
    b, log = browser(rel), rel.ActionLog()
    app.SESSIONS.clear()
    out = rel.run_steps(b, rel.address_steps(2, "22 Canal Street, Leeds"), log)
    assert out == [("open 2", "needs_human")] and log.entries[-1]["event"] == "handoff"

    b2, log2 = browser(rel), rel.ActionLog()
    b2.page.interrupt = ("Verify it's you", "<p>Enter the verification code we sent "
                         "to your phone.</p><label>Code <input name=code></label>")
    out = rel.run_steps(b2, rel.address_steps(2, "22 Canal Street, Leeds"), log2)
    assert out == [("open 2", "needs_human")]
    assert rel.needs_person(rel.observe(b2)) and app.CUSTOMERS[2]["address"] == "18 Mill Lane, Leeds"


def test_every_read_is_evidence(rel):
    b, log = browser(rel), rel.ActionLog()
    rel.run_steps(b, rel.address_steps(1, "9 Avenida da Boavista, Porto"), log)
    reads = [e for e in log.entries if "snapshot" in e]
    assert reads and all(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", e["at"])
                         for e in reads)
    assert all(e["snapshot"] in log.snapshots for e in reads)
    last = [e for e in reads if e["event"] == "after"][-1]
    assert "Address saved" in log.snapshots[last["snapshot"]]


def test_ex23_7_reliable_queue(rel):
    import ex23_7_reliable_queue as ex
    out = ex.main(verbose=False)
    assert out["first_run"] == {1: "done", 2: "done", 3: "needs_human", 4: "session_lost"}
    assert out["after_resume"] == {1: "done", 2: "done", 3: "needs_human", 4: "done"}
    assert out["address_writes"] == 3 and out["credits"] == 0 and out["chen_balance"] == 25.0
    events = [e["event"] for e in out["log"]]
    assert "stale" in events and "unverified; not retried" in events and "handoff" in events
