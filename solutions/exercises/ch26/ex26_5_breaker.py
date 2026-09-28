"""Exercise 26.5 (solution): an audit circuit breaker. A burst of denials, or any
attempt on another user's resource, disables the agent at once."""
import time

import ch26_identity as ident

WINDOW, BURST = 60, 3

def check(now: float | None = None) -> list[dict]:
    now = now or time.time()
    actions = []
    by_agent = {}
    for a in ident.AUDIT:
        if a["decision"] == "denied" and a["agent"] and now - a["at"] <= WINDOW:
            by_agent.setdefault(a["agent"].removeprefix("agent:"), []).append(a)
    for agent, denials in by_agent.items():
        if agent in ident.DISABLED:
            continue
        cross_user = [d for d in denials if "another user" in d["reason"]]
        if cross_user or len(denials) > BURST:
            ident.disable(agent)
            why = ("tried another user's resource" if cross_user
                   else f"{len(denials)} denials in {WINDOW}s")
            actions.append({"agent": agent, "action": "disabled", "why": why})
    return actions

if __name__ == "__main__":
    print(check())
