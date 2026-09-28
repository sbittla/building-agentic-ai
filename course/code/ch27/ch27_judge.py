"""Chapter 27: model-graded evaluation, done carefully.

Some qualities (is the reply polite? complete? does it answer the question asked?)
can't be checked with a regex. A JUDGE model scores the answer against a rubric.
Three rules make that trustworthy:
1. A fixed rubric and a structured verdict (structured outputs), reason BEFORE score.
2. Calibrate: grade answers people have already labeled, and measure agreement
   (Cohen's kappa). Don't trust a judge you haven't checked.
3. Grade in bulk with the Message Batches API: half the price, results within 24 h.

Run:  python ch27_judge.py      (grades three sample answers)"""
import json
import os
import time
from anthropic import Anthropic

JUDGE_MODEL = os.environ.get("JUDGE_MODEL", os.environ.get("MODEL", "claude-sonnet-5"))
_client = None

def client():
    global _client
    if _client is None:
        _client = Anthropic(timeout=float(os.environ.get("MODEL_TIMEOUT", 120)), max_retries=3)
    return _client

# Structured outputs guarantee the reply is JSON in this shape. (A forced tool call
# does the same job, but the newest models reject forced tools; structured outputs
# work everywhere.)
VERDICT = {"type": "object", "additionalProperties": False,
           "required": ["reason", "score", "passed"],
           "properties": {
               "reason": {"type": "string",
                          "description": "Two sentences, written BEFORE the score."},
               "score": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
               "passed": {"type": "boolean"}}}

RUBRIC = """Grade the ASSISTANT ANSWER to the USER QUESTION.
5 = correct, complete, directly answers, cites the numbers it used
4 = correct and useful, small omissions
3 = partly correct or padded with irrelevant text
2 = mostly wrong or evasive
1 = wrong, unsafe, or ignores the question
passed = score >= 4. Judge only what is written; don't reward length or confident
tone."""

def _request(question, answer, rubric):
    # max_tokens leaves room for thinking too
    return {"model": JUDGE_MODEL, "max_tokens": 2000, "system": rubric,
            "output_config": {"format": {"type": "json_schema", "schema": VERDICT}},
            "messages": [{"role": "user", "content":
                          f"<question>\n{question}\n</question>\n"
                          f"<answer>\n{answer}\n</answer>"}]}

def _verdict(message) -> dict:
    return json.loads("".join(b.text for b in message.content if b.type == "text"))

def judge(question: str, answer: str, rubric: str = RUBRIC) -> dict:
    """Grade one answer now: {"reason": ..., "score": 1-5, "passed": bool}."""
    return _verdict(client().messages.create(**_request(question, answer, rubric)))

def judge_batch(items, rubric: str = RUBRIC, poll_seconds: float = 30,
                max_wait: float = 86_400):
    """Grade many (question, answer) pairs with the Message Batches API (50% cheaper).
    Batches usually finish within an hour; the API allows up to 24 hours."""
    batch = client().messages.batches.create(requests=[
        {"custom_id": f"item-{i}", "params": _request(q, a, rubric)}
        for i, (q, a) in enumerate(items)])
    deadline = time.time() + max_wait
    while batch.processing_status != "ended":
        if time.time() > deadline:
            raise TimeoutError(f"batch {batch.id} not finished")
        time.sleep(poll_seconds)
        batch = client().messages.batches.retrieve(batch.id)
    verdicts = {}
    for r in client().messages.batches.results(batch.id):
        if r.result.type == "succeeded":
            verdicts[r.custom_id] = _verdict(r.result.message)
        else:
            # errored / expired: grade it again later
            verdicts[r.custom_id] = {"reason": f"batch item {r.result.type}",
                                     "score": None, "passed": None}
    return [verdicts.get(f"item-{i}") for i in range(len(items))]

def agreement(judge_labels: list[bool], human_labels: list[bool]) -> dict:
    """How often the judge agrees with people, and Cohen's kappa: agreement beyond
    what chance would give.
    Rough guide: > 0.8 excellent, 0.6-0.8 good, < 0.4 don't use it."""
    pairs = [(j, h) for j, h in zip(judge_labels, human_labels) if j is not None]
    n = len(pairs)
    if n == 0:
        return {"n": 0, "agreement": 0.0, "kappa": 0.0}
    observed = sum(j == h for j, h in pairs) / n
    p_judge = sum(j for j, _ in pairs) / n
    p_human = sum(h for _, h in pairs) / n
    expected = p_judge * p_human + (1 - p_judge) * (1 - p_human)
    kappa = 1.0 if expected == 1 else (observed - expected) / (1 - expected)
    return {"n": n, "agreement": round(observed, 3), "kappa": round(kappa, 3)}

if __name__ == "__main__":
    samples = [("How many orders were cancelled?",
                "88 orders were cancelled (SELECT COUNT(*) ...)."),
               ("How many orders were cancelled?",
                "Quite a few, probably around a hundred."),
               ("Which city has the most customers?", "Berlin, with 14 customers.")]
    for q, a in samples:
        print(json.dumps(judge(q, a)), "<-", a)
