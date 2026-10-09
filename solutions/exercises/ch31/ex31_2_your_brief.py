"""Exercise 31.2: a brief that's ready to build.

A regional hospital asks to "use AI to reduce clinician paperwork". Write the brief
discovery should produce for one narrow workflow, discharge summaries, and let
check_brief() say whether it's buildable. Free: no model."""
from ch31_field import Metric, ProblemBrief, check_brief

VAGUE = ProblemBrief(
    customer="Riverside Hospital", users="doctors", job="paperwork",
    output="AI help", metric=Metric("less paperwork", ""))

BRIEF = ProblemBrief(
    customer="Riverside Hospital",
    users="24 ward doctors on the two internal-medicine wards",
    job="write the discharge summary from the patient's notes, results and medications",
    output="a draft discharge summary with a citation for every fact; the doctor edits and signs",
    metric=Metric("minutes from opening the record to a signed discharge summary", "minutes",
                  baseline=22, target=12,
                  measured_how="observed 30 discharges on both wards, 3-14 June"),
    customer_owner="Dr. Lena Okafor, clinical lead for internal medicine",
    constraints=["patient data stays in the hospital's own cloud tenant",
                 "sign-in with the hospital's SAML provider",
                 "the agent never writes to the patient record"],
    non_goals=["coding and billing", "letters to patients", "clinical advice"],
    risks=["a hallucinated medication", "doctors signing drafts without reading them"])

if __name__ == "__main__":
    print("Vague request:")
    for p in check_brief(VAGUE):
        print("  -", p)
    problems = check_brief(BRIEF)
    print("\nDischarge-summary brief:", problems or "ready to build")
    assert not problems
