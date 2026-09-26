"""Chapter 11 reference solution: 11.4 (sequential vs parallel), 11.5 (structured
delegation with effort levels) and 11.6 (a critic pass with one revision)."""
import asyncio
import json
import time
import ch11_research_team as base
from ch11_research_team import _call, usage


def text_of(response) -> str:
    """The reply's text blocks only (a reply can start with a thinking block)."""
    return "".join(b.text for b in response.content if b.type == "text")

PLAN_TOOL = {
    "name": "make_plan",
    "description": "Split the question into 2-4 independent subtasks for parallel research.",
    "input_schema": {"type": "object", "properties": {"subtasks": {
        "type": "array", "minItems": 2, "maxItems": 4, "items": {
            "type": "object", "properties": {
                "objective": {"type": "string", "description": "exactly what to find out"},
                "out_of_scope": {"type": "string", "description": "what sibling subtasks cover"},
                "effort": {"type": "string", "enum": ["quick", "deep"]}},
            "required": ["objective", "out_of_scope", "effort"]}}},
        "required": ["subtasks"]}}
EFFORT_STEPS = {"quick": 3, "deep": 8}

CRITIC_TOOL = {
    "name": "review", "description": "List claims in the answer that no finding supports.",
    "input_schema": {"type": "object", "properties": {
        "unsupported_claims": {"type": "array", "items": {"type": "string"}}},
        "required": ["unsupported_claims"]}}

def brief(sub: dict) -> str:
    return (f"Objective: {sub['objective']}\nOut of scope (a colleague covers it): "
            f"{sub['out_of_scope']}\nEffort: {sub['effort']}")

async def research(question: str, parallel: bool = True, critic: bool = True) -> dict:
    t0 = time.perf_counter()
    plan = await _call(tools=[PLAN_TOOL], tool_choice={"type": "tool", "name": "make_plan"},
                       messages=[{"role": "user", "content": question}])
    subtasks = next(b.input["subtasks"] for b in plan.content if b.type == "tool_use")
    jobs = [base.run_subagent(brief(s), max_iterations=EFFORT_STEPS[s["effort"]]) for s in subtasks]
    if parallel:
        findings = await asyncio.gather(*jobs)
    else:                                          # one after another, to compare
        findings = [await j for j in jobs]
    report = "\n\n".join(f"## {s['objective']}\n{f}" for s, f in zip(subtasks, findings))
    draft = text_of(await _call(messages=[{"role": "user", "content":
        f"Question: {question}\n\nFindings:\n{report}\n\nWrite a concise answer. Keep every "
        "source citation. Point out disagreements."}]))
    unsupported = []
    if critic:                                     # exercise 11.5
        review = await _call(tools=[CRITIC_TOOL], tool_choice={"type": "tool", "name": "review"},
                             messages=[{"role": "user", "content":
                                        f"Findings:\n{report}\n\nAnswer:\n{draft}"}])
        unsupported = next(b.input["unsupported_claims"] for b in review.content
                           if b.type == "tool_use")
        if unsupported:
            draft = text_of(await _call(messages=[{"role": "user", "content":
                f"Revise this answer. Remove or fix these unsupported claims: "
                f"{json.dumps(unsupported)}\n\nFindings:\n{report}\n\nAnswer:\n{draft}"}]))
    return {"answer": draft, "subtasks": subtasks, "unsupported": unsupported,
            "seconds": time.perf_counter() - t0, "usage": dict(usage)}

if __name__ == "__main__":
    q = "Compare agentic search and RAG for our internal docs: cost, freshness, exact error codes."
    for mode in (True, False):
        r = asyncio.run(research(q, parallel=mode))
        print(f"\n=== {'parallel' if mode else 'sequential'}: {r['seconds']:.1f}s ===\n{r['answer']}")
