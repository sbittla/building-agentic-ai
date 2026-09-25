"""Chapter 11: four more ways agents work together. Each is a few lines on top of the
Chapter 4 loop, and each passes STRUCTURED data between agents (structured outputs), never
free text that the next agent has to guess at.

  route()      a router picks ONE specialist agent for the request
  handoff()    an analyst finds the facts, a writer turns them into a report
  refine()     a writer and a critic take turns until the critic approves (or 3 rounds)
  vote()       several agents answer independently; the majority wins

Run:  python ch11_patterns.py"""
import json
from concurrent.futures import ThreadPoolExecutor
from ch04_agent import get_client, MODEL, run_agent
import ch06_notes_tools as notes, ch07_weather_tools as weather, ch08_sql_tools as sql

def ask_json(prompt: str, schema: dict, system: str = "") -> dict:
    """One model call whose reply is JSON matching the schema (structured outputs)."""
    r = get_client().messages.create(
        model=MODEL, max_tokens=4096, system=system,
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": prompt}])
    return json.loads("".join(b.text for b in r.content if b.type == "text"))

def obj(**props):                        # a small helper for strict JSON Schemas
    return {"type": "object", "properties": props, "required": list(props),
            "additionalProperties": False}

# ---------------------------------------------------------------- 1. router
SPECIALISTS = {"sales_data": sql, "my_notes": notes, "weather": weather}

def route(request: str, verbose: bool = False):
    choice = ask_json(f"Which specialist should handle this request?\n\n{request}",
                      obj(specialist={"type": "string", "enum": [*SPECIALISTS, "none"]},
                          reason={"type": "string"}))
    if choice["specialist"] == "none":
        return choice, "Sorry, I can only help with sales data, your notes or the weather."
    m = SPECIALISTS[choice["specialist"]]
    answer, _, _ = run_agent(request, m.TOOLS, m.run_tool, system=m.SYSTEM, verbose=verbose)
    return choice, answer

# ---------------------------------------------------------------- 2. handoff
FINDINGS = obj(question={"type": "string"},
               facts={"type": "array", "items": obj(fact={"type": "string"},
                                                     sql={"type": "string"})},
               caveats={"type": "array", "items": {"type": "string"}})

def handoff(question: str, verbose: bool = False) -> tuple[dict, str]:
    """Stage 1 gathers facts with tools; stage 2 writes, with no tools and no access to
    the database, so it can only use what it was handed."""
    raw, _, _ = run_agent(question, sql.TOOLS, sql.run_tool, system=sql.SYSTEM, verbose=verbose)
    findings = ask_json(f"Turn this analysis into the findings format. Keep the SQL that "
                        f"produced each fact.\n\n{raw}", FINDINGS)
    report = ask_json("Write a three-sentence summary for a busy manager, using ONLY these "
                      f"findings:\n{json.dumps(findings)}", obj(summary={"type": "string"}))
    return findings, report["summary"]

# ---------------------------------------------------------------- 3. evaluator-optimizer
VERDICT = obj(approved={"type": "boolean"}, problems={"type": "array", "items": {"type": "string"}})

def refine(task: str, rounds: int = 3) -> tuple[str, list]:
    draft = ask_json(task, obj(text={"type": "string"}))["text"]
    history = []
    for _ in range(rounds):
        verdict = ask_json(f"Task: {task}\n\nDraft:\n{draft}\n\nCheck the draft against the task. "
                           "Approve it only if it fully meets it.", VERDICT,
                           system="You are a strict reviewer.")
        history.append(verdict)
        if verdict["approved"]:
            break
        draft = ask_json(f"Task: {task}\n\nRevise this draft to fix these problems: "
                         f"{json.dumps(verdict['problems'])}\n\nDraft:\n{draft}",
                         obj(text={"type": "string"}))["text"]
    return draft, history

# ---------------------------------------------------------------- 4. voting
def vote(question: str, options: list[str], n: int = 3) -> tuple[str, list]:
    """n independent judgments in parallel; ties go to the first option listed."""
    schema = obj(choice={"type": "string", "enum": options}, reason={"type": "string"})
    with ThreadPoolExecutor(max_workers=n) as pool:
        ballots = list(pool.map(lambda _: ask_json(question, schema), range(n)))
    counts = {o: sum(b["choice"] == o for b in ballots) for o in options}
    return max(options, key=lambda o: counts[o]), ballots

if __name__ == "__main__":
    print("1. ROUTER:", route("How many orders shipped last month?", verbose=False))
    findings, summary = handoff("Which product category earns the most revenue?")
    print("\n2. HANDOFF findings:", json.dumps(findings, indent=1)[:600], "\n   summary:", summary)
    text, history = refine("Write a two-line product description for a standing desk. "
                           "Mention the height range 70-120 cm and no marketing superlatives.")
    print(f"\n3. REFINE after {len(history)} review(s):", text)
    winner, ballots = vote("A customer writes: 'The chair arrived broken, I want my money back "
                           "today.' How urgent is this?", ["low", "medium", "high"])
    print("\n4. VOTE:", winner, [b["choice"] for b in ballots])
