"""Capstone 7 sample data: 30 synthetic, de-identified shift-handover notes with the
nurse's own SBAR summary as the reference. Some are deliberately messy: abbreviations,
missing vitals, and two patients mixed in one note. Writes handovers.jsonl."""
import json
import random

BEDS = [f"{w}-{n}" for w in ("4B", "5A") for n in range(1, 16)]
REASONS = ["post-op day 2, hip replacement", "community-acquired pneumonia",
           "COPD exacerbation", "cellulitis, left leg", "heart failure, fluid overload",
           "UTI with confusion"]
ALLERGIES = ["NKDA", "penicillin", "latex", "sulfa", "NKDA"]
PLANS = ["mobilize with PT this morning", "repeat bloods at 06:00", "wean O2 to keep sats 92-96%",
         "IV antibiotics until review", "daily weight, fluid restriction 1.5 L"]
ABBREV = {"patient": "pt", "oxygen": "O2", "blood pressure": "BP", "nil by mouth": "NBM",
          "as needed": "PRN"}

def note(i: int, rng: random.Random) -> dict:
    bed, reason = BEDS[i], rng.choice(REASONS)
    allergy, plan = rng.choice(ALLERGIES), rng.choice(PLANS)
    bp, sats = f"{rng.randint(100, 150)}/{rng.randint(60, 90)}", rng.randint(90, 99)
    text = (f"Bed {bed}: patient admitted with {reason}. Allergy: {allergy}. "
            f"Overnight blood pressure {bp}, oxygen sats {sats}% on room air. "
            f"Paracetamol given as needed x1. Plan: {plan}.")
    messy = []
    if i % 5 == 1:                                   # abbreviations
        for full, short in ABBREV.items():
            text = text.replace(full, short)
        messy.append("abbreviations")
    if i % 7 == 3:                                   # vitals missing
        text = text.replace(f"Overnight blood pressure {bp}, oxygen sats {sats}% on room air. ", "")
        messy.append("missing vitals")
    if i % 10 == 9:                                  # another patient mixed in
        text += f" Also bed {BEDS[(i + 1) % len(BEDS)]} needs a falls review."
        messy.append("two patients in one note")
    reference = {"situation": f"Bed {bed}, {reason}",
                 "background": f"Allergy: {allergy}",
                 "assessment": "vitals not recorded" if "missing vitals" in messy
                 else f"BP {bp}, sats {sats}% on room air",
                 "recommendation": plan}
    return {"id": f"h{i + 1:02d}", "bed": bed, "note": text, "reference": reference,
            "messy": messy}

def build(path="handovers.jsonl", seed=7):
    rng = random.Random(seed)
    rows = [note(i, rng) for i in range(30)]
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return rows

if __name__ == "__main__":
    rows = build()
    print(f"Wrote handovers.jsonl: {len(rows)} notes, "
          f"{sum(1 for r in rows if r['messy'])} messy.")
