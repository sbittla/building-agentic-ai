"""Exercise 22.4 (solution): the refund policy as a versioned JSON file, with a new rule
added as data. The decision stays pure code; every case records the policy version."""
import json
from datetime import date
from pathlib import Path

import ch22_guarded as g

POLICY_FILE = Path("refund_policy.json")
DEFAULT = {"version": "2026-09-25.1", "window_days": 30, "auto_limit": 100.0,
           "share": {"damaged": 1.0, "late": 1.0, "wrong_item": 1.0, "changed_mind": 0.9},
           "restricted": [{"above": 300.0, "only": ["damaged", "wrong_item"]}]}

def load_policy(path: Path = POLICY_FILE) -> dict:
    if not path.exists():
        path.write_text(json.dumps(DEFAULT, indent=1))
    policy = json.loads(path.read_text())
    g.POLICY = policy                    # the workflow reads the loaded policy
    return policy

def decide(case: g.Case) -> None:
    policy = g.POLICY
    order = g.ORDERS[case.facts["order_id"]]
    reason = case.facts["reason"]
    age = (g.TODAY - date.fromisoformat(order["delivered"])).days
    amount = round(order["amount"] * policy["share"][reason], 2)
    case.facts.update(amount=amount, age_days=age, policy=policy["version"])
    tag = f" [policy {policy['version']}]"
    blocked = [r for r in policy.get("restricted", [])
               if order["amount"] > r["above"] and reason not in r["only"]]
    if age > policy["window_days"]:
        case.move("rejected", f"delivered {age} days ago{tag}")
    elif blocked:
        case.move("rejected", f"orders over ${blocked[0]['above']:.0f} are refundable "
                              f"only for {', '.join(blocked[0]['only'])}{tag}")
    elif amount > policy["auto_limit"]:
        case.move("awaiting_approval", f"${amount:.2f} over the limit{tag}")
    else:
        case.move("approved", f"${amount:.2f} within policy{tag}")

g.decide = decide                         # handle() now uses the versioned decision

if __name__ == "__main__":
    load_policy()
    case = g.handle("ana@example.com", "I changed my mind about A-1002.")
    print(case.state, case.log)
