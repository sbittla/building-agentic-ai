"""Exercise 16.5 (solution): measure what prompt caching saves, from real usage fields.

Three runs of the same 5-question session (one conversation, so history grows):
  off     no caching
  prefix  tools + system prompt cached (with_cache)
  auto    top-level cache_control: the growing conversation is cached too
No padding tricks: if the stable prefix is below the model's minimum cacheable length
(1,024-4,096 tokens depending on the model), `prefix` simply caches nothing, and the
report says so. That is a real finding, not a failure."""
import ch08_sql_tools as sql
from ch04_agent import next_action
from ch16_context import MODEL, cache_kwargs, client, cost, count_tokens

QUESTIONS = ["How many customers are there?", "Which city has the most customers?",
             "What is the most expensive product?", "How many orders were cancelled?",
             "Which product category earns the most revenue?"]
MIN_CACHEABLE = 1024          # the smallest minimum; check your model's in the docs

def run_session(questions, mode: str, max_iterations=8):
    request = cache_kwargs(sql.SYSTEM, sql.TOOLS, mode)
    totals = {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0, "calls": 0}
    messages = []
    for q in questions:
        messages.append({"role": "user", "content": q})
        for _ in range(max_iterations):
            r = client().messages.create(model=MODEL, max_tokens=4096, messages=messages, **request)
            u = r.usage
            totals["calls"] += 1
            totals["input"] += u.input_tokens
            totals["output"] += u.output_tokens
            totals["cache_write"] += getattr(u, "cache_creation_input_tokens", 0) or 0
            totals["cache_read"] += getattr(u, "cache_read_input_tokens", 0) or 0
            messages.append({"role": "assistant", "content": r.content})
            if next_action(r)[0] != "tools":
                break
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": b.id, "content": sql.run_tool(b.name, b.input)}
                for b in r.content if b.type == "tool_use"]})
    totals["cost"] = cost(totals["input"], totals["output"], totals["cache_write"], totals["cache_read"])
    return totals

def main():
    prefix = count_tokens([{"role": "user", "content": "x"}], sql.SYSTEM, sql.TOOLS)
    print(f"Stable prefix (system + tools): about {prefix} tokens"
          + ("" if prefix >= MIN_CACHEABLE else
             f" -- below {MIN_CACHEABLE}, so 'prefix' caching will cache nothing"))
    rows = {mode: run_session(QUESTIONS, mode) for mode in ("off", "prefix", "auto")}
    print(f"{'mode':<8}{'calls':>6}{'input':>9}{'output':>8}{'c.write':>9}{'c.read':>9}{'cost $':>10}")
    for mode, t in rows.items():
        print(f"{mode:<8}{t['calls']:>6}{t['input']:>9}{t['output']:>8}{t['cache_write']:>9}"
              f"{t['cache_read']:>9}{t['cost']:>10.4f}")
    base = rows["off"]["cost"]
    for mode in ("prefix", "auto"):
        if base:
            print(f"{mode}: {100 * (base - rows[mode]['cost']) / base:.0f}% cheaper than no caching")
    return rows

if __name__ == "__main__":
    main()
