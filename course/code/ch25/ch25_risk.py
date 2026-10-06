"""Chapter 25: sizing the risk of an agent. Five factors, each scored 1 to 3, multiplied:

    risk = capability x autonomy x access x persistence x blast radius

The score picks a tier, the tier and the factors pick the controls the agent needs
before launch, and `gaps` lists the ones it doesn't have yet. The numbers are a
structured judgment aid for comparing agents and changes, NOT a probability of harm.

    ./course.sh python ch25_risk.py        three agents from the book scored, the
                                           support agent's gaps, and one change that
                                           lowers its tier"""

# ------------------------------------------------------------ 1. the factors
FACTORS = {      # each factor: the anchor for 1, 2 and 3
    "capability": ("a few narrow tools (a clock, a calculator)",
                   "a set of domain tools (orders, files, tickets)",
                   "open-ended tools: run code, browse, fetch any URL, delegate"),
    "autonomy": ("changes nothing, or a person approves every change",
                 "acts alone within a written policy, asks for the rest",
                 "acts alone, hard-to-reverse actions included"),
    "access": ("reads public data or its own",
               "reads private data: a user's, the company's",
               "writes to systems of record or spends money"),
    "persistence": ("nothing outlives the run",
                    "state for one session or job: history, checkpoints",
                    "long-term memory, or runs on a schedule"),
    "blast_radius": ("one user, who is watching",
                     "one team, or internal systems",
                     "customers, money or outside systems"),
}

def risk_score(profile: dict) -> int:
    """Multiply the five factors. Each must be 1, 2 or 3: there is no 0, because no
    agent is risk-free, and 1 means 'this factor adds nothing'."""
    score = 1
    for factor in FACTORS:
        value = profile.get(factor)
        if value not in (1, 2, 3):
            raise ValueError(f"{factor} must be 1, 2 or 3, not {value!r}")
        score *= value
    return score

# ------------------------------------------------------------ 2. tiers
TIERS = {1: ("low", 8), 2: ("moderate", 27), 3: ("high", 81), 4: ("critical", 243)}

def tier(score: int) -> int:
    """1 to 4. The bounds are 2^3, 3^3 and 3^4: three factors at 2 is the top of low,
    three at 3 the top of moderate and four at 3 the top of high."""
    for number, (_name, upper) in TIERS.items():
        if score <= upper:
            return number
    raise ValueError(f"score {score} is above the maximum of 243")

# ------------------------------------------------------------ 3. controls
CONTROLS = {     # id: what it is, and where the book builds it
    "owner":           "a named owner in the agent inventory (30.12)",
    "evals":           "an evaluation suite that gates every change (27.7)",
    "audit_log":       "every tool call and approval logged (9.4, 28.2)",
    "threat_model":    "the four questions answered in writing (25.2)",
    "scoped_tokens":   "its own identity with least-privilege tokens (26.3)",
    "budgets":         "step, time and money limits enforced in code (29.4)",
    "monitoring":      "dashboards and alerts on its actions (28.9, 28.11)",
    "approval_gate":   "a person approves hard-to-reverse actions, in code (9.3)",
    "control_plane":   "states, rules and limits in code; the model proposes (Chapter 22)",
    "regression":      "a security regression scenario per defense (25.10)",
    "kill_switch":     "one action disables it and every token it holds (26.7)",
    "memory_gate":     "scoped memory with a write gate (17.7, 17.8)",
    "sandbox":         "untrusted input and code isolated: quarantine or sandbox (25.5, 10.4)",
    "step_up":         "one-use step-up tokens for the riskiest actions (26.6)",
    "red_team":        "a red-team run before launch (25.8)",
    "security_signoff": "a security review signs off on launch (30.12)",
    "review_monthly":  "a person reviews a sample of its traces every month",
    "review_weekly":   "a person reviews a sample of its traces every week",
}

BY_TIER = {      # each tier adds to the ones below it
    1: ["owner", "evals", "audit_log"],
    2: ["threat_model", "scoped_tokens", "budgets", "monitoring"],
    3: ["approval_gate", "control_plane", "regression", "kill_switch", "review_monthly"],
    4: ["sandbox", "step_up", "red_team", "security_signoff", "review_weekly"],
}

BY_FACTOR = {    # a factor at 3 needs these whatever the total
    "capability": ["sandbox"],
    "autonomy": ["monitoring", "kill_switch"],
    "access": ["scoped_tokens", "approval_gate"],
    "persistence": ["memory_gate"],
    "blast_radius": ["red_team", "kill_switch"],
}

def required_controls(profile: dict) -> list[str]:
    """The tier's controls (and every lower tier's), plus those any factor at 3
    demands. In the order of CONTROLS, without repeats."""
    level = tier(risk_score(profile))
    needed = {c for t in range(1, level + 1) for c in BY_TIER[t]}
    for factor, controls in BY_FACTOR.items():
        if profile[factor] == 3:
            needed.update(controls)
    if level == 4:                                      # weekly replaces monthly
        needed.discard("review_monthly")
    return [c for c in CONTROLS if c in needed]

def gaps(profile: dict, controls_in_place) -> list[str]:
    """The required controls this agent doesn't have yet. Empty means it may launch."""
    have = set(controls_in_place)
    return [c for c in required_controls(profile) if c not in have]

# ------------------------------------------------------------ 4. the demo
AGENTS = {
    "date agent (Chapter 4)":
        dict(capability=1, autonomy=1, access=1, persistence=1, blast_radius=1),
    "file organizer, auto-approval on (9.6)":
        dict(capability=2, autonomy=2, access=3, persistence=1, blast_radius=1),
    "support agent with refunds (case study)":
        dict(capability=2, autonomy=2, access=3, persistence=3, blast_radius=3),
}

def show(name: str, profile: dict) -> None:
    score = risk_score(profile)
    level = tier(score)
    factors = " x ".join(str(profile[f]) for f in FACTORS)
    print(f"{name:42} {factors} = {score:>3}  tier {level} ({TIERS[level][0]}), "
          f"{len(required_controls(profile))} controls")

if __name__ == "__main__":
    print("capability x autonomy x access x persistence x blast radius\n")
    for name, profile in AGENTS.items():
        show(name, profile)

    support = AGENTS["support agent with refunds (case study)"]
    prototype = ["owner", "evals", "audit_log", "approval_gate", "scoped_tokens"]
    print(f"\nA support-agent prototype with {', '.join(prototype)} is missing:")
    for control in gaps(support, prototype):
        print(f"  - {control:16} {CONTROLS[control]}")

    print("\nCut one factor: every refund waits for a person (autonomy 2 -> 1).")
    safer = {**support, "autonomy": 1}
    show("support agent, every refund approved", safer)
    before, after = set(required_controls(support)), set(required_controls(safer))
    print(f"No longer required: {', '.join(c for c in CONTROLS if c in before - after)}")
    print(f"Newly required:     {', '.join(c for c in CONTROLS if c in after - before)}")
