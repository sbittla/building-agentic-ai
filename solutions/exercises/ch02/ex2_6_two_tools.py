"""Exercise 2.6 (Complex): why the chapter 2 `ask` breaks on multi-step questions.

The original ask() makes exactly two model calls. If the second response is ALSO a
tool_use (the model wants percent_change first, then calculate), ask() returns
only the text of a response that is really a tool_use request: an empty answer.
The fix is a loop: see sol_ch02_calculator_agent.ask (and chapter 4's run_agent).
"""
import sol_ch02_calculator_agent as sol

QUESTION = ("Revenue went from 84,213 to 97,400. What is the percent change, and "
            "what is 17.5% of the new figure?")

def two_call_ask(question: str) -> str:
    """The chapter 2 pattern, with the extra tool registered: exactly two calls."""
    messages = [{"role": "user", "content": question}]
    r = sol.client.messages.create(model=sol.MODEL, max_tokens=2000, tools=sol.TOOLS,
                                   messages=messages)
    if r.stop_reason != "tool_use":
        return "".join(b.text for b in r.content if b.type == "text")
    messages.append({"role": "assistant", "content": r.content})
    messages.append({"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": b.id, "content": sol.run_tool(b.name, b.input)[0]}
        for b in r.content if b.type == "tool_use"]})
    final = sol.client.messages.create(model=sol.MODEL, max_tokens=2000, tools=sol.TOOLS,
                                       messages=messages)
    if final.stop_reason == "tool_use":
        return "BROKEN: the second response asked for another tool, and two_call_ask stops here."
    return "".join(b.text for b in final.content if b.type == "text")

if __name__ == "__main__":
    print("two-call version:", two_call_ask(QUESTION))
    print("looping version: ", sol.ask(QUESTION))
