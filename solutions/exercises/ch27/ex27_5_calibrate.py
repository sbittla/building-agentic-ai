"""Exercise 27.5 (solution): check the judge against people before trusting it.

    python exercises/ex27_5_calibrate.py            # grade now
    python exercises/ex27_5_calibrate.py --batch    # grade with the Batches API (half price)"""
import json
import sys
import ch27_judge as j

def main(path="judge_calibration.jsonl", batch=False, rubric=j.RUBRIC):
    items = [json.loads(line) for line in open(path) if line.strip()]
    pairs = [(it["question"], it["answer"]) for it in items]
    verdicts = j.judge_batch(pairs, rubric) if batch else [j.judge(q, a, rubric) for q, a in pairs]
    result = j.agreement([v["passed"] for v in verdicts], [it["human_passed"] for it in items])
    print(f"agreement {result['agreement']:.0%}, Cohen's kappa {result['kappa']:.2f} "
          f"on {result['n']} labeled answers")
    for it, v in zip(items, verdicts):
        if v["passed"] != it["human_passed"]:
            print(f"DISAGREE  human={it['human_passed']} judge={v['passed']} (score {v['score']}): "
                  f"{it['answer'][:70]!r}\n          judge's reason: {v['reason']}")
    verdict = ("usable" if result["kappa"] >= 0.6 else
               "not yet: read the disagreements, tighten the rubric, and measure again")
    print("Judge is", verdict)
    return result, verdicts

if __name__ == "__main__":
    main(batch="--batch" in sys.argv)
