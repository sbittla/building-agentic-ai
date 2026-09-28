"""Exercise 24.5 (solution): the chapter 8 SQL analyst built four ways, one eval suite.

Each implementation returns (answer, tools_used, tokens). The chapter 27 checks run on
all four, so the comparison is fair."""
import asyncio
import inspect
import json
import statistics
import time
from types import SimpleNamespace
import ch08_sql_tools as sql
from ch27_eval import check

# ---------------- 1. hand-built (chapter 4)
def hand_built(q):
    from ch04_agent import run_agent
    answer, messages, stats = run_agent(q, sql.TOOLS, sql.run_tool, system=sql.SYSTEM, verbose=False)
    used = [b.name for m in messages if m["role"] == "assistant"
            for b in m["content"] if getattr(b, "type", "") == "tool_use"]
    return answer, used, stats["input_tokens"] + stats["output_tokens"]

# ---------------- 2. tool runner
def tool_runner(q):
    from anthropic import Anthropic, beta_tool
    from ch24_tool_runner import MODEL

    @beta_tool
    def get_schema() -> str:
        """CREATE TABLE statements for the shop database. Call before writing SQL."""
        return sql.get_schema()

    @beta_tool
    def run_query(sql_text: str) -> str:
        """Run one read-only SQLite SELECT on the shop database (max 50 rows).

        Args:
            sql_text: the SELECT statement
        """
        return sql.run_query(sql_text)

    runner = Anthropic().beta.messages.tool_runner(
        model=MODEL, max_tokens=4096, max_iterations=8, system=sql.SYSTEM,
        tools=[get_schema, run_query], messages=[{"role": "user", "content": q}])
    used, tokens, final = [], 0, None
    for message in runner:
        tokens += message.usage.input_tokens + message.usage.output_tokens
        used += [b.name for b in message.content if b.type == "tool_use"]
        final = message
    return "".join(b.text for b in final.content if b.type == "text"), used, tokens

# ---------------- 3. Claude Agent SDK
def agent_sdk(q):
    from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock, ToolUseBlock, query
    from ch24_agent_sdk import OPTIONS, _prompt

    async def go():
        answer, used, tokens = "", [], 0
        async for m in query(prompt=_prompt(q), options=OPTIONS):
            if isinstance(m, AssistantMessage):
                for b in m.content:
                    if isinstance(b, ToolUseBlock):
                        used.append(b.name.split("__")[-1])       # mcp__shop__run_query -> run_query
                    elif isinstance(b, TextBlock):
                        answer = b.text
            elif isinstance(m, ResultMessage) and m.usage:
                tokens = m.usage.get("input_tokens", 0) + m.usage.get("output_tokens", 0)
        return answer, used, tokens
    return asyncio.run(go())

# ---------------- 4. LangChain
def langchain(q):
    from langchain.agents import create_agent
    from langchain_anthropic import ChatAnthropic
    from ch24_langchain import MODEL

    def get_schema() -> str:
        """CREATE TABLE statements for the shop database. Call before writing SQL."""
        return sql.get_schema()

    def run_query(sql_text: str) -> str:
        """Run one read-only SQLite SELECT on the shop database (max 50 rows)."""
        return sql.run_query(sql_text)

    agent = create_agent(model=ChatAnthropic(model=MODEL), tools=[get_schema, run_query],
                         system_prompt=sql.SYSTEM)
    state = agent.invoke({"messages": [{"role": "user", "content": q}]})
    used, tokens = [], 0
    for m in state["messages"]:
        used += [c["name"] for c in getattr(m, "tool_calls", []) or []]
        u = getattr(m, "usage_metadata", None) or {}
        tokens += u.get("input_tokens", 0) + u.get("output_tokens", 0)
    return state["messages"][-1].content, used, tokens

IMPLEMENTATIONS = {"hand-built": (hand_built, "ch04_agent.py + ch08_sql_tools.py"),
                   "tool runner": (tool_runner, None), "Agent SDK": (agent_sdk, None),
                   "LangChain": (langchain, None)}

def _as_messages(used):
    """check() reads tool names from messages; build the minimal shape it needs."""
    return [{"role": "assistant", "content": [SimpleNamespace(type="tool_use", name=n) for n in used]}]

def compare(cases, impls=IMPLEMENTATIONS, trials=1):
    """Same cases, same checks, `trials` runs each. With ~24 cases x 3 trials the 95%
    intervals are still roughly +/-10 points: differences smaller than that are noise.
    Token counts aren't comparable across frameworks (they count cached tokens
    differently), so compare the provider's bill or total_cost_usd for cost."""
    from ch27_eval import wilson
    table = {}
    for name, (fn, _) in impls.items():
        rows = []
        for case in cases:
            for _ in range(trials):
                t0 = time.perf_counter()
                try:
                    answer, used, tokens = fn(case["question"])
                    failures = check(case, answer, _as_messages(used))
                except Exception as exc:
                    tokens, failures = 0, [f"crashed: {type(exc).__name__}"]
                rows.append({"pass": not failures, "tokens": tokens, "s": time.perf_counter() - t0})
        lines = len(inspect.getsource(fn).splitlines())
        passes = sum(r["pass"] for r in rows)
        lo, hi = wilson(passes, len(rows))
        table[name] = {"pass_rate": f"{passes}/{len(rows)}", "ci95": f"{lo:.0%}-{hi:.0%}",
                       "mean_tokens": round(statistics.mean(r["tokens"] for r in rows)),
                       "median_s": round(statistics.median(r["s"] for r in rows), 1),
                       "lines_of_code": lines}
    return table

def main(path="eval_sql.jsonl", trials=3, max_cases=None):
    cases = [json.loads(line) for line in open(path) if line.strip()][:max_cases]
    table = compare(cases, trials=trials)
    print(f"{'version':<12}{'pass':>8}{'95% CI':>10}{'tokens':>9}{'median s':>10}{'lines':>7}")
    for name, r in table.items():
        print(f"{name:<12}{r['pass_rate']:>8}{r['ci95']:>10}{r['mean_tokens']:>9}"
              f"{r['median_s']:>10}{r['lines_of_code']:>7}")
    print("\nNote: 'lines' counts the adapter in this file; the hand-built version also relies "
          "on the ~50-line loop in ch04_agent.py.")
    return table

if __name__ == "__main__":
    import sys                     # python ex24_5_three_ways.py [cases.jsonl] [trials] [max cases]
    args = sys.argv[1:]
    main(*args[:1], *(int(a) for a in args[1:3]))
