"""Exercise 18.3 (solution): one more @beta_tool, and the schema it generates."""
import json
from anthropic import Anthropic, beta_tool
import ch03_tools as t3
from ch18_tool_runner import MODEL, days_between, get_current_date

@beta_tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a value between units of the same kind: km, mi, m (length) or kg, lb, g (mass).

    Args:
        value: the number to convert
        from_unit: the unit of value, one of km, mi, m, kg, lb, g
        to_unit: the unit to convert to, of the same kind
    """
    return t3.convert_units(value, from_unit, to_unit)

TOOLS = [get_current_date, days_between, convert_units]

def ask(question: str, client=None):
    client = client or Anthropic()
    runner = client.beta.messages.tool_runner(model=MODEL, max_tokens=4096, max_iterations=8,
                                              tools=TOOLS,
                                              messages=[{"role": "user", "content": question}])
    final, used = None, []
    for message in runner:
        for block in message.content:
            if block.type == "tool_use":
                used.append(block.name)
                print(f"  -> {block.name}({block.input})")
        final = message
    return "".join(b.text for b in final.content if b.type == "text"), used

if __name__ == "__main__":
    print("Generated schema:\n" + json.dumps(convert_units.to_dict(), indent=2))
    print(ask("How far is a marathon (26.2 miles) in kilometres?")[0])
