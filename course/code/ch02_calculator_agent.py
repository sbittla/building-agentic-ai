"""Chapter 2: the model asks for a tool, our code runs it."""
import ast
import operator
import os
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()

# ---- 1. The tool itself: a SAFE arithmetic evaluator (never use eval()) ----
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}

def calculate(expression: str) -> str:
    """Evaluate +, -, *, /, **, % and parentheses. Returns the result as text."""
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.operand))
        raise ValueError(f"Unsupported expression element: {ast.dump(node)[:40]}")
    tree = ast.parse(expression, mode="eval")
    return str(_eval(tree))

# ---- 2. The tool's description, written for the model ----
TOOLS = [{
    "name": "calculate",
    "description": ("Evaluate an arithmetic expression exactly. Use this for ANY "
                    "arithmetic, including percentages (write 17.5% of X as 0.175*X). "
                    "Supports + - * / ** % and parentheses."),
    "input_schema": {
        "type": "object",
        "properties": {"expression": {"type": "string",
                                      "description": "e.g. '0.175 * 84213'"}},
        "required": ["expression"],
    },
}]

# ---- 3. One round-trip: ask -> tool_use -> tool_result -> final answer ----
def ask(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    response = client.messages.create(model=MODEL, max_tokens=2000,
                                      tools=TOOLS, messages=messages)
    if response.stop_reason != "tool_use":
        return "".join(b.text for b in response.content if b.type == "text")          # model answered directly

    messages.append({"role": "assistant", "content": response.content})
    results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"  -> model called {block.name}({block.input})")
            output = calculate(**block.input)
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": output})
    messages.append({"role": "user", "content": results})

    final = client.messages.create(model=MODEL, max_tokens=2000,
                                   tools=TOOLS, messages=messages)
    return "".join(b.text for b in final.content if b.type == "text")

if __name__ == "__main__":
    print(ask("What is 17.5% of 84,213?"))
