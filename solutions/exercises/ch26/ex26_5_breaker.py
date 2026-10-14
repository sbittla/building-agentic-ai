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

def demo():
    """A support agent for Ana tries Ben's order (B-2001); an analyst for Ben reads it."""
    s = ident.Session("support-agent", "ana")
    print("support-agent (for ana) asks for B-2001:", s.run_tool("get_order", {"order_id": "B-2001"}))
    ben = ident.mint("analyst-agent", "ben", {"orders:read"}, ident.API)
    print("analyst-agent (for ben) reads B-2001:  ", ident.get_order(ben, "B-2001"))
    print("breaker:", check())
    print("support-agent's next call:             ", s.run_tool("get_order", {"order_id": "A-1001"}))
    print("analyst-agent's next call (untouched): ", ident.get_order(ben, "B-2001"))

if __name__ == "__main__":
    demo()
