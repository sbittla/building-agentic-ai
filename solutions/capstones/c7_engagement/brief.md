# Capstone 7: the customer's request (as received)

From: Marcus Hale, VP Nursing, Bayview Health
Subject: AI for handovers?

Our nurses lose a lot of time at shift change. Handover takes forever and things get
missed. Can you use AI to fix this? We'd like something live on two wards next
quarter. Our IT and privacy people will need to be involved.

## Constraint sheet (from Bayview Health's security team)

- Patient data stays in Bayview Health's own cloud tenant (region: us-west).
- Models may run only inside that tenant ("customer-vpc") or on the provider's
  US healthcare endpoint covered by their agreement ("provider-us-hipaa").
- Staff sign in with SAML. Logs may not contain patient names, MRNs or diagnoses.
- Nothing may be written to the electronic health record during the pilot.
- Data kept at most 14 days outside the record. Every access is audited.

## The dataset

`handovers.jsonl`: 30 de-identified handover notes (synthetic) with the nurse's
own summary as the reference answer. Some notes are messy: abbreviations, missing
vitals, two patients mixed in one note.
