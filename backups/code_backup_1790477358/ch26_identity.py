"""Chapter 26: agent identity and authorization. Every agent acts with its own identity,
on behalf of a user, holding a token that says exactly what it may do, where, for how
long and up to what limit. Tools check the token on every call; the model never sees it.

  * identities   each agent is registered with the most it may EVER be given
  * tokens       short-lived signed tokens (JWTs) with scopes, an audience and limits
  * checks       the tool verifies the token, the scope, the resource's owner and limits
  * attenuation  a token can be narrowed for a sub-agent, never widened
  * step-up      a risky action needs a fresh, narrow, single-use token after a person
                 approves it
  * audit        every decision records the agent, the user, the token and the reason
  * revocation   one token, or a whole agent, can be switched off at once

    ./course.sh python ch26_identity.py"""
import os
import time
import uuid

import jwt

ISSUER = "course-identity"
KEY = os.environ.get("TOKEN_SIGNING_KEY", "dev-only-signing-key-change-me-0123456789")
ALGORITHM = "HS256"        # production: an identity provider and asymmetric keys

AGENTS = {   # the registry: which scopes each agent may ever hold
    "support-agent": {"orders:read", "returns:create", "refunds:create"},
    "analyst-agent": {"orders:read"},
}
REVOKED: set[str] = set()          # token ids (jti)
DISABLED: set[str] = set()         # agent names: the kill switch
USED: set[str] = set()             # single-use tokens already spent
AUDIT: list[dict] = []

class Denied(Exception):
    pass

class NeedsApproval(Denied):
    """The action is allowed in principle, but only with a person's say-so."""

# ------------------------------------------------------------ 1. issuing tokens
def mint(agent: str, user: str, scopes: set[str], audience: str, ttl: int = 900,
         limits: dict | None = None, chain: tuple = ()) -> str:
    if agent not in AGENTS or agent in DISABLED:
        raise Denied(f"agent {agent!r} is not registered or is disabled")
    if extra := set(scopes) - AGENTS[agent]:
        raise Denied(f"{agent} may never hold {sorted(extra)}")
    now = int(time.time())
    claims = {"iss": ISSUER, "sub": f"agent:{agent}", "act_for": f"user:{user}",
              "aud": audience, "scope": " ".join(sorted(scopes)), "iat": now,
              "exp": now + ttl, "jti": uuid.uuid4().hex, "limits": limits or {},
              "chain": list(chain)}                  # the tokens this one came from
    return jwt.encode(claims, KEY, algorithm=ALGORITHM)

def verify(token: str, audience: str) -> dict:
    """Signature, issuer, audience and expiry, then our own revocation lists."""
    try:
        claims = jwt.decode(token, KEY, algorithms=[ALGORITHM], audience=audience,
                            issuer=ISSUER, options={"require": ["exp", "jti", "sub"]})
    except jwt.PyJWTError as exc:
        raise Denied(f"invalid token: {exc}") from None
    if REVOKED & {claims["jti"], *claims["chain"]}:
        raise Denied("token revoked")
    if claims["sub"].removeprefix("agent:") in DISABLED:
        raise Denied("agent disabled")
    return claims

def attenuate(token: str, audience: str, scopes: set[str], agent: str | None = None,
              ttl: int | None = None, limits: dict | None = None) -> str:
    """A narrower token for a sub-agent or a single task. It can only lose rights:
    fewer scopes, an earlier expiry, tighter limits."""
    parent = verify(token, audience)
    if extra := set(scopes) - set(parent["scope"].split()):
        raise Denied(f"can't widen a token: {sorted(extra)} not in the parent")
    remaining = parent["exp"] - int(time.time())
    merged = dict(parent["limits"])
    for k, v in (limits or {}).items():
        merged[k] = min(v, merged[k]) if k in merged else v
    return mint(agent or parent["sub"].removeprefix("agent:"),
                parent["act_for"].removeprefix("user:"), scopes, audience,
                min(ttl or remaining, remaining), merged,
                (*parent["chain"], parent["jti"]))

# ------------------------------------------------------------ 2. checking at the tool
def authorize(token: str, audience: str, scope: str, owner: str | None = None,
              amount: float | None = None) -> dict:
    """The policy enforcement point: every tool calls this before doing anything."""
    claims, decision, reason = None, "denied", ""
    try:
        claims = verify(token, audience)
        if owner and claims["act_for"] != f"user:{owner}":
            raise Denied("the resource belongs to another user")
        if scope not in claims["scope"].split():
            raise NeedsApproval(f"token lacks {scope}")
        limit = claims["limits"].get("max_amount")
        if amount is not None and limit is not None and amount > limit:
            raise Denied(f"{amount:.2f} is over the token's limit of {limit:.2f}")
        if claims["limits"].get("single_use"):
            if claims["jti"] in USED:
                raise Denied("single-use token already used")
            USED.add(claims["jti"])
        decision, reason = "allowed", scope
        return claims
    except Denied as exc:
        reason = str(exc)
        raise
    finally:
        AUDIT.append({"at": time.time(), "decision": decision, "reason": reason,
                      "scope": scope, "audience": audience,
                      "agent": claims and claims["sub"], "for": claims and
                      claims["act_for"], "jti": claims and claims["jti"]})

def revoke(token_id: str) -> None:
    REVOKED.add(token_id)

def disable(agent: str) -> None:
    DISABLED.add(agent)

# ------------------------------------------------------------ 3. a tool server
ORDERS = {"A-1001": {"owner": "ana", "amount": 49.0},
          "A-1002": {"owner": "ana", "amount": 420.0},
          "B-2001": {"owner": "ben", "amount": 25.0}}
REFUNDS: list[tuple] = []
API = "orders-api"                     # the audience: tokens for other APIs don't work

def get_order(token: str, order_id: str) -> str:
    order = ORDERS.get(order_id)
    if order is None:
        return "ERROR: no such order"
    authorize(token, API, "orders:read", owner=order["owner"])
    return f"{order_id}: ${order['amount']:.2f}"

def refund(token: str, order_id: str, amount: float) -> str:
    order = ORDERS.get(order_id)
    if order is None:
        return "ERROR: no such order"
    if amount > order["amount"]:
        return f"ERROR: the order was only ${order['amount']:.2f}"
    authorize(token, API, "refunds:create", owner=order["owner"], amount=amount)
    REFUNDS.append((order_id, amount))
    return f"Refunded ${amount:.2f} on {order_id}"

# ------------------------------------------------------------ 4. the harness
class Session:
    """Holds the tokens for one user's conversation. The model sees tool names and
    results, never a token."""
    def __init__(self, agent: str, user: str, approver=None):
        self.agent, self.user = agent, user
        self.approver = approver or (lambda request: False)
        self.token = mint(agent, user, {"orders:read", "returns:create"}, API)

    def step_up(self, order_id: str, amount: float) -> str:
        """A person approves ONE refund; the token allows that, once, briefly."""
        if not self.approver({"agent": self.agent, "user": self.user,
                              "action": "refund", "order": order_id, "amount": amount}):
            raise Denied("a person declined the refund")
        return mint(self.agent, self.user, {"refunds:create"}, API, ttl=120,
                    limits={"max_amount": amount, "single_use": True})

    def run_tool(self, name: str, args: dict) -> str:
        try:
            if name == "get_order":
                return get_order(self.token, **args)
            if name == "refund":
                try:
                    return refund(self.token, **args)
                except NeedsApproval:
                    approved = self.step_up(args["order_id"], args["amount"])
                    return refund(approved, **args)
            return f"ERROR: unknown tool {name}"
        except Denied as exc:
            return f"ERROR: not authorized: {exc}"

TOOLS = [
    {"name": "get_order", "description": "Look up one of the signed-in customer's "
     "orders.", "input_schema": {"type": "object", "required": ["order_id"],
                                 "properties": {"order_id": {"type": "string"}}}},
    {"name": "refund", "description": "Refund an amount on an order. A person may be "
     "asked to approve.", "input_schema": {
         "type": "object", "required": ["order_id", "amount"],
         "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}}}},
]

if __name__ == "__main__":
    from ch04_agent import run_agent
    session = Session("support-agent", "ana", approver=lambda r: input(
        f"  Approve {r['action']} of ${r['amount']:.2f} on {r['order']}? [y/N] ")
        .strip().lower() == "y")
    answer, _, _ = run_agent("I'm Ana. Please refund order A-1001 in full, and also "
                             "B-2001 while you're at it.", TOOLS, session.run_tool,
                             system="You are a support agent. Use the tools.")
    print("\n" + answer + "\n\nAudit:")
    for a in AUDIT:
        print(f"  {a['decision']:<8} {a['scope']:<16} {a['for']} {a['reason']}")
