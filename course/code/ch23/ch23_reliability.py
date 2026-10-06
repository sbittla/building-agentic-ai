"""Chapter 23.9: reliability engineering for computer use. A wrapper around each
browser action that checks the page before acting, verifies the page afterwards (not
the model's claim), retries only what is safe to retry, stops for a person at a
sign-in or verification-code page and records evidence for every attempt.

  * preconditions   act only when the page is the one you expect
  * postconditions  read the page again; "done" means the page shows the change
  * retries         bounded, with a fresh read each time, for "not found yet" errors
  * no repeats      an action that may have happened (money, emails) is never retried
  * hand-off        a session-expired or MFA page goes to a person; nobody guesses
  * evidence        every read is logged with a snapshot id and a UTC timestamp

It reuses ch23_browser.Browser unchanged. To run offline (no Chromium, no model), the
back office is served in-process and OfflinePage stands in for Playwright's page; it
can also inject the faults real browsers produce.

    ./course.sh python ch23_reliability.py        three runs with injected faults"""
import hashlib
import re
import tempfile
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlparse

from starlette.testclient import TestClient

import ch23_backoffice as app
from ch23_browser import Browser

# ======================================================= 1. an offline page and browser
class _Parse(HTMLParser):
    """Just enough HTML for the back office: title, visible text, forms, controls."""
    BLOCK = {"h1", "p", "li", "form", "ul"}

    def __init__(self, page_html: str):
        super().__init__()
        self.title, self.text, self.forms, self.controls = "", [], [], []
        self._tag, self._label, self._in_label, self._form = None, [], [], None
        self.feed(page_html)
        self.text = re.sub(r"\n\s*\n+", "\n", "".join(self.text)).strip()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._tag = tag
        if tag == "form":
            self.forms.append({"method": a.get("method", "get"), "action": a.get("action", "")})
            self._form = len(self.forms) - 1
        elif tag == "label":
            self._label, self._in_label = [], []
        if tag in ("a", "button", "input", "select", "textarea") and a.get("type") != "hidden":
            el = {"tag": tag, "attrs": a, "text": "", "label": "", "form": self._form,
                  "value": a.get("value", "")}
            self.controls.append(el)
            if tag == "input":
                self._in_label.append(el)

    def handle_endtag(self, tag):
        if tag == "label":
            for el in self._in_label:
                el["label"] = "".join(self._label).strip()
            self._in_label = []
        if tag == "form":
            self._form = None
        if tag in self.BLOCK:
            self.text.append("\n")
        self._tag = None

    def handle_data(self, data):
        if self._tag == "title":
            self.title += data
            return
        self.text.append(data)
        self._label.append(data)
        if self.controls and self._tag in ("a", "button"):
            self.controls[-1]["text"] += data


class OfflineLocator:
    def __init__(self, page, els):
        self.page, self.els = page, els

    def count(self):
        return len(self.els)

    def inner_text(self):
        return self.els[0]["text"].strip()

    def get_attribute(self, name):
        return self.els[0]["attrs"].get(name)

    def evaluate(self, _js):            # the only script Browser runs on an element:
        return self.page._form_data(self.els[0]["form"])   # the values in its form

    def fill(self, text):
        self.els[0]["value"] = text

    def click(self):
        self.page._click(self.els[0])


class OfflinePage:
    """Stands in for Playwright's page, talking to the back office in-process. The
    fault knobs make it misbehave the way real pages do:
      missing    the next N element lookups find nothing (not rendered yet, or stale)
      click_fault "after": the click lands, then times out; "before": it never lands
      interrupt  the next page load shows this (title, html) instead, like an MFA page"""

    def __init__(self, base="http://testserver"):
        self.client = TestClient(app.app, base_url=base)
        self.url, self.doc = base + "/", _Parse("")
        self.missing, self.click_fault, self.interrupt = 0, None, None

    def _load(self, response=None, html_text=""):
        if self.interrupt:
            title, body = self.interrupt
            self.interrupt = None
            self.url = urljoin(self.url, "/verify")
            html_text = f"<title>{title}</title><body><h1>{title}</h1>{body}</body>"
        elif response is not None:
            self.url, html_text = str(response.url), response.text
        self.doc = _Parse(html_text)

    def goto(self, url):
        self._load(self.client.get(url))

    def evaluate(self, _js):            # Browser.snapshot's SNAPSHOT_JS, done in Python
        controls = []
        for n, el in enumerate(self.doc.controls, 1):
            el["ref"] = f"e{n}"
            kind = ("link" if el["tag"] == "a" else "button"
                    if el["tag"] == "button" or el["attrs"].get("type") == "submit"
                    else "select" if el["tag"] == "select" else "textbox")
            label = (el["label"] or el["text"] or el["attrs"].get("name", "")).strip()
            line = f'[e{n}] {kind} "{label[:60]}"'
            if kind == "textbox" and el["attrs"].get("type") != "password":
                line += f' value="{el["value"][:80]}"'
            controls.append(line)
        return {"title": self.doc.title, "url": self.url,
                "text": self.doc.text[:3000], "controls": controls}

    def locator(self, selector):
        if m := re.fullmatch(r'\[data-ref="(e\d+)"\]', selector):
            if self.missing:
                self.missing -= 1
                return OfflineLocator(self, [])
            return OfflineLocator(self, [e for e in self.doc.controls
                                         if e.get("ref") == m[1]])
        tag, attr, val = re.fullmatch(r"(\w+)\[(\w+)=(\w+)\]", selector).groups()
        return OfflineLocator(self, [e for e in self.doc.controls if e["tag"] == tag
                                     and e["attrs"].get(attr) == val])

    def fill(self, selector, text):
        self.locator(selector).fill(text)

    def click(self, selector):
        self.locator(selector).click()

    def input_value(self, selector):
        return self.locator(selector).els[0]["value"]

    def wait_for_load_state(self):
        pass

    def screenshot(self, path):         # offline there are no pixels: keep the text
        with open(path, "w") as f:
            f.write(self.doc.text)

    def _form_data(self, form):
        return {e["attrs"]["name"]: e["value"] for e in self.doc.controls
                if e["form"] == form and e["form"] is not None and "name" in e["attrs"]}

    def _click(self, el):
        fault, self.click_fault = self.click_fault, None
        if fault == "before":
            raise TimeoutError("click timed out")
        if el["tag"] == "a":
            self.goto(urljoin(self.url, el["attrs"]["href"]))
        elif el["form"] is not None:
            form, data = self.doc.forms[el["form"]], self._form_data(el["form"])
            target = urljoin(self.url, form["action"] or urlparse(self.url).path)
            if form["method"].lower() == "post":
                self._load(self.client.post(target, data=data))
            else:
                self.goto(target.split("?")[0] + "?" + urlencode(data))
        if fault == "after":
            raise TimeoutError("click timed out waiting for the page")


class OfflineBrowser(Browser):
    """ch23_browser.Browser with OfflinePage in place of Chromium. Every method that
    the agent and this module call (open, click, type_text, snapshot) is Browser's."""

    def __init__(self, approver=None, max_actions: int = 60, shots: str | None = None):
        self.page = OfflinePage()
        self.base = "http://testserver"
        self.host = urlparse(self.base).netloc
        self.approver = approver or (lambda action: False)
        self.max_actions, self.actions, self.log = max_actions, 0, []
        self.shots = Path(shots or tempfile.mkdtemp(prefix="shots23-"))

    def close(self):
        self.page.client.close()

# ======================================================= 2. observations and evidence
CONTROL = re.compile(r'\[(e\d+)\] (\w+) "(.*?)"(?: value="(.*)")?$')

@dataclass
class Observation:
    url: str
    title: str
    text: str
    controls: list[dict]
    snapshot_id: str
    at: str

def observe(browser: Browser) -> Observation:
    """Read the page in code, the same way Browser.snapshot does for the model."""
    s = browser.page.evaluate("snapshot")
    controls = [dict(zip(("ref", "kind", "label", "value"), m.groups()))
                for line in s["controls"] if (m := CONTROL.match(line))]
    digest = hashlib.sha256(f"{s['url']}\n{s['text']}\n{s['controls']}".encode())
    return Observation(s["url"], s["title"], s["text"], controls,
                       digest.hexdigest()[:10],
                       time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

@dataclass
class ActionLog:
    entries: list[dict] = field(default_factory=list)
    snapshots: dict[str, str] = field(default_factory=dict)   # id -> page text

    def record(self, step: str, attempt: int, event: str, obs: Observation | None = None,
               detail: str = "") -> None:
        entry = {"step": step, "attempt": attempt, "event": event, "detail": detail}
        if obs:
            entry |= {"at": obs.at, "url": urlparse(obs.url).path,
                      "snapshot": obs.snapshot_id}
            self.snapshots[obs.snapshot_id] = obs.text
        self.entries.append(entry)

# ======================================================= 3. the reliable action
HANDOFF = re.compile(r"\bsign in\b|session (has )?expired|verification code|"
                     r"one-time code|two-factor|verify it'?s you", re.I)

def needs_person(obs: Observation) -> str | None:
    """A sign-in or MFA page means the session is gone. The agent never types
    credentials or codes (section 23.3), so a person takes over."""
    if "/login" in urlparse(obs.url).path or HANDOFF.search(f"{obs.title}\n{obs.text}"):
        return f"{obs.title!r}: a person must sign in or verify"
    return None

@dataclass
class Step:
    name: str
    action: str                     # "open", "type" or "click"
    target: str                     # a path for open; a control's label otherwise
    text: str = ""                  # what to type
    before: object = lambda *obs: True     # precondition on the page before acting
    after: object = lambda *obs: True      # postcondition: after(before, after_page)
    idempotent: bool = True         # safe to do twice? (setting a value: yes)
    check_path: str | None = None   # re-open this page to verify, rather than trust it

def find(obs: Observation, label: str) -> str | None:
    """Target controls by what they are, not by a ref from an older read."""
    return next((c["ref"] for c in obs.controls if c["label"] == label), None)

def act(browser: Browser, step: Step, ref: str | None) -> str:
    if step.action == "open":
        return browser.open(step.target)
    if step.action == "type":
        return browser.type_text(ref, step.text)
    return browser.click(ref)

def run_step(browser: Browser, step: Step, log: ActionLog, tries: int = 3) -> str:
    """One action with checks on both sides. Returns done, needs_human, refused or
    failed. Retries happen only when the action certainly didn't happen, or when
    doing it again is harmless."""
    for attempt in range(1, tries + 1):
        before = observe(browser)
        log.record(step.name, attempt, "before", before)
        if reason := needs_person(before):
            log.record(step.name, attempt, "handoff", detail=reason)
            return "needs_human"
        if not step.before(before):
            log.record(step.name, attempt, "precondition not met")
            continue                                   # re-read; the page may lag
        ref = None if step.action == "open" else find(before, step.target)
        if step.action != "open" and ref is None:
            log.record(step.name, attempt, "not found", detail=step.target)
            continue
        try:
            result = act(browser, step, ref)
        except Exception as exc:                       # it may or may not have landed
            log.record(step.name, attempt, "error", detail=f"{type(exc).__name__}: {exc}")
            if step.idempotent:
                continue
            result = "outcome unknown"                 # verify; never repeat
        if result.startswith("ERROR: no control"):     # stale or not rendered yet:
            log.record(step.name, attempt, "stale", detail=result)
            continue                                   # nothing happened, so retry
        if result.startswith("ERROR"):                 # approval, allowlist, limit
            log.record(step.name, attempt, "refused", detail=result)
            return "refused"
        if step.check_path:
            browser.open(step.check_path)
        after = observe(browser)
        log.record(step.name, attempt, "after", after)
        if reason := needs_person(after):
            log.record(step.name, attempt, "handoff", detail=reason)
            return "needs_human"
        if step.after(before, after):
            log.record(step.name, attempt, "verified")
            return "done"
        if not step.idempotent:
            log.record(step.name, attempt, "unverified; not retried")
            return "needs_human"
        log.record(step.name, attempt, "not verified")
    log.record(step.name, tries, "gave up")
    return "failed"

def run_steps(browser: Browser, steps: list[Step], log: ActionLog) -> list[tuple]:
    """Run steps in order; stop at the first one that isn't done."""
    results = []
    for step in steps:
        status = run_step(browser, step, log)
        results.append((step.name, status))
        if status != "done":
            break
    return results

# ======================================================= 4. conditions and step recipes
def title_has(s):
    return lambda *obs: s in obs[-1].title          # checks the latest page given

def text_has(s):
    return lambda *obs: s in obs[-1].text

def field_is(label, value):
    return lambda *obs: any(c["label"] == label and c["value"] == value
                            for c in obs[-1].controls)

def balance(obs: Observation) -> float:
    m = re.search(r"Credit balance: \$([\d.]+)", obs.text)
    return float(m[1]) if m else float("nan")

def address_steps(cid: int, address: str) -> list[Step]:
    name = app.CUSTOMERS[cid]["name"]
    return [
        Step(f"open {cid}", "open", f"/customers/{cid}", after=title_has(name)),
        Step(f"type address {cid}", "type", "Address", address,
             before=title_has(name), after=field_is("Address", address)),
        Step(f"save address {cid}", "click", "Save address",
             before=field_is("Address", address),
             after=lambda b, a: "Address saved" in a.text and
                   field_is("Address", address)(a)),
    ]

def credit_steps(cid: int, amount: float, reason: str) -> list[Step]:
    name = app.CUSTOMERS[cid]["name"]
    page = f"/customers/{cid}"
    return [
        Step(f"open {cid}", "open", page, after=title_has(name)),
        Step(f"type amount {cid}", "type", "Credit amount", f"{amount:g}",
             before=title_has(name), after=field_is("Credit amount", f"{amount:g}")),
        Step(f"type reason {cid}", "type", "Reason", reason,
             after=field_is("Reason", reason)),
        Step(f"issue credit {cid}", "click", "Issue credit", idempotent=False,
             before=field_is("Credit amount", f"{amount:g}"), check_path=page,
             after=lambda b, a: abs(balance(a) - balance(b) - amount) < 0.005),
    ]

def sign_in(browser: Browser) -> None:
    browser.sign_in("agent-bot", app.USERS["agent-bot"])

def show(log: ActionLog) -> None:
    for e in log.entries:
        where = f"{e.get('url', '')} snap {e['snapshot']}" if "snapshot" in e else ""
        print(f"  {e['step']:<18} try {e['attempt']}  {e['event']:<24} {where}"
              f"{e['detail'][:56]}")

if __name__ == "__main__":
    app.reset()
    app.SESSIONS.clear()
    browser = OfflineBrowser(approver=lambda a: True)     # a person approves credits
    sign_in(browser)

    print("1. An element that isn't there yet: re-read and retry (idempotent).")
    log = ActionLog()
    browser.page.missing = 2
    print("  ", run_steps(browser, address_steps(1, "9 Avenida da Boavista, Porto"), log))
    show(log)
    print("   Ana's address:", app.CUSTOMERS[1]["address"])

    print("\n2. A credit click that lands, then times out: verify, never click again.")
    steps = credit_steps(3, 20, "late parcel")
    print("   ", run_steps(browser, steps[:3], ActionLog()))      # open, type, type
    log = ActionLog()
    browser.page.click_fault = "after"
    print("   ", run_step(browser, steps[3], log))
    show(log)
    credits = [a for a in app.AUDIT if a[3] == "credit"]
    print(f"   Chen's balance: ${app.CUSTOMERS[3]['credit']:.2f}; credits issued: "
          f"{len(credits)}")

    print("\n3. The session expires: hand over to a person instead of guessing.")
    log = ActionLog()
    app.SESSIONS.clear()
    print("  ", run_steps(browser, address_steps(2, "22 Canal Street, Leeds"), log))
    show(log)
    print(f"   Evidence kept: {len(log.snapshots)} page snapshots; screenshots in "
          f"{browser.shots}")
    browser.close()
