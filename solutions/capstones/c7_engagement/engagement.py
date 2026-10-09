"""Capstone 7 reference: one forward-deployed engagement, end to end, as data and checks.

Bayview Health asked for "AI to fix handovers". This file holds what discovery, design
review and the pilot established, runs every Chapter 31 check on it, and writes the
engagement record (ENGAGEMENT.md) a customer and your own team can audit:

    python engagement.py                 run every check, write ENGAGEMENT.md
    python engagement.py --week 3        the record as it stood at week 3 of the pilot

It doesn't build the agent itself: that's the summarizer you build with Chapters 16-18
and evaluate with Chapter 27. It's the part an FDE adds around any agent: the scope,
the constraints, the signed criteria, the gate and the handoff, decided by code."""
import sys
from pathlib import Path

from ch31_field import (Component, Criteria, Environment, FieldFix, Metric, PilotResults,
                        ProblemBrief, Slice, check_brief, check_design, handoff_gaps,
                        next_stage, pilot_gate, productize, rank_slices, score)

BRIEF = ProblemBrief(
    customer="Bayview Health",
    users="nurses on wards 4B and 5A at the 07:00 and 19:00 shift changes",
    job="hand each patient over to the next shift without missing anything that matters",
    output="a structured handover draft per patient (SBAR) with each fact linked to the chart",
    metric=Metric("minutes of handover per patient", "minutes", baseline=6.5, target=4.0,
                  measured_how="observed 120 handovers on both wards, 2-15 September"),
    customer_owner="Marcus Hale, VP Nursing",
    constraints=["data stays in the us-west tenant", "SAML sign-in",
                 "no writes to the health record", "14-day retention",
                 "no names, MRNs or diagnoses in logs"],
    non_goals=["clinical decisions", "medication changes", "writing to the record"],
    risks=["a missed allergy or code status", "two patients mixed in one note"])

ENV = Environment(
    data_region="us-west", allowed_model_hosts={"customer-vpc", "provider-us-hipaa"},
    egress_allowlist={"llm.hipaa.provider.example"}, sso="saml",
    pii_fields={"name", "mrn", "diagnosis", "date_of_birth"}, max_retention_days=14,
    write_access=False, not_yet={"page_doctors"})

SLICES = [
    Slice("Draft the SBAR handover from the shift's notes", 210, 4, "low", {"pii"}),
    Slice("Flag what changed since the last shift", 90, 3, "medium", {"pii"}),
    Slice("Page the doctor when vitals worsen", 300, 8, "high", {"pii", "page_doctors"}),
    Slice("Write the handover into the record", 120, 3, "medium", {"pii", "core_system_write"}),
]

DESIGN = [
    Component("ward tablet app", "us-west", user_facing=True, auth="saml"),
    Component("handover agent", "us-west", holds_customer_data=True,
              model_host="provider-us-hipaa", egress={"llm.hipaa.provider.example"},
              logs_fields={"handover_id", "latency_ms", "tokens"}, retention_days=14,
              audit_log=True),
    Component("chart reader (read-only FHIR)", "us-west", holds_customer_data=True,
              audit_log=True),
]

CRITERIA = Criteria(min_success=0.90, max_p95_s=10.0, max_cost_per_task=0.04,
                    max_critical=0, min_runs=100, min_gain=0.25)

PILOT = {   # week -> what the pilot measured (an allergy omitted counts as critical)
    1: PilotResults(30, 25, 9.1, 0.031, 1, 6.0, 6.5),
    3: PilotResults(90, 84, 8.2, 0.029, 0, 4.9, 6.5),
    6: PilotResults(240, 230, 7.4, 0.027, 0, 4.4, 6.5),
}

HANDOFF = {"runbook": "runbooks/handover-agent.md", "owner": "Clinical Apps team",
           "eval_suite": "evals/handovers.jsonl (30 cases, 3 trials)",
           "dashboard": "handover-agent SLOs", "kill_switch": "tested 3 November",
           "escalation": "Clinical Apps on-call, then the FDE team, 30 minutes",
           "training": "both wards, 3 sessions", "known_limits": "docs/limits.md"}

FIELD_FIXES = [FieldFix("Bayview Health", "medical abbreviation expansion", 14),
               FieldFix("Riverside Hospital", "medical abbreviation expansion", 9),
               FieldFix("Bayview Health", "saml sign-in", 12)]

def record(week: int) -> tuple[str, str]:
    """The engagement record at a given pilot week, and the gate's decision."""
    lines = [f"# Engagement record: {BRIEF.customer}", "", "## Brief", "",
             f"- **Users:** {BRIEF.users}", f"- **Output:** {BRIEF.output}",
             f"- **Metric:** {BRIEF.metric.name}: {BRIEF.metric.baseline} -> "
             f"{BRIEF.metric.target} ({BRIEF.metric.measured_how})",
             f"- **Owner:** {BRIEF.customer_owner}",
             f"- **Brief check:** {'; '.join(check_brief(BRIEF)) or 'ready to build'}", "",
             "## Scope", ""]
    ok, rejected = rank_slices(SLICES, ENV.blocked())
    lines += [f"- **First slice:** {ok[0].name} (score {score(ok[0]):.1f})"]
    lines += [f"- Later: {s.name}" for s in ok[1:]]
    lines += [f"- Not now: {s.name} ({'; '.join(why)})" for s, why in rejected]
    violations = check_design(DESIGN, ENV)
    lines += ["", "## Design review", "",
              *([f"- [{v.rule}] {v.component}: {v.detail} -> {v.fix}" for v in violations]
                or ["- No violations of the customer's rules."])]
    results = PILOT[max(w for w in PILOT if w <= week)]
    gate = pilot_gate(results, CRITERIA)
    lo, hi = gate["interval"]
    lines += ["", f"## Pilot gate (week {week})", "",
              f"- **Decision:** {gate['decision']} (success {lo:.0%}-{hi:.0%}, "
              f"gain {gate['gain']:.0%})",
              *[f"- {r}" for r in gate["reasons"]],
              f"- **Stage:** {next_stage('pilot', gate['decision'])}"]
    if gate["decision"] == "promote":
        gaps = handoff_gaps(HANDOFF)
        lines += ["", "## Handoff", "", *([f"- Missing: {g}" for g in gaps]
                                         or ["- Everything the customer needs is in place."])]
    lines += ["", "## For the product team", "",
              *[f"- {r['capability']}: {r['customers']} customer(s) -> {r['verdict']}"
                for r in productize(FIELD_FIXES, min_customers=2)]]
    return "\n".join(lines) + "\n", gate["decision"]

if __name__ == "__main__":
    week = int(sys.argv[sys.argv.index("--week") + 1]) if "--week" in sys.argv else max(PILOT)
    text, decision = record(week)
    Path("ENGAGEMENT.md").write_text(text)
    print(text)
    print(f"Wrote ENGAGEMENT.md (decision at week {week}: {decision}).")
