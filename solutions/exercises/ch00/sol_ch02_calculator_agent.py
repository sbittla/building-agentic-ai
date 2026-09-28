"""Chapter 2 reference solution: exercises 2.2 (exponent cap), 2.4 (sqrt),
2.6 (graceful errors) and 2.7 (a second tool + a loop that handles multi-step)."""
import ast
import math
import operator
import os
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.USub: operator.neg, ast.UAdd: operator.pos}
MAX_EXPONENT = 1000          # exercise 2.2: 10 ** 10 ** 10 would hang the process

def calculate(expression: str) -> str:
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            left, right = _eval(node.left), _eval(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
                raise ValueError(f"exponent {right} is larger than {MAX_EXPONENT}")
            return _OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.operand))
        # exactly one allowed function name
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "sqrt" and len(node.args) == 1 and not node.keywords):
            return math.sqrt(_eval(node.args[0]))
        raise ValueError(f"Unsupported expression element: {ast.dump(node)[:40]}")
    result = _eval(ast.parse(expression, mode="eval"))
    return str(round(result, 10) if isinstance(result, float) else result)

def percent_change(old: float, new: float) -> str:
    if old == 0:
        raise ValueError("old value is 0, so percent change is undefined")
    return f"{(new - old) / old * 100:.2f}%"

REGISTRY = {"calculate": calculate, "percent_change": percent_change}
TOOLS = [
    {"name": "calculate",
     "description": ("Evaluate an arithmetic expression exactly. Use this for ANY "
                     "arithmetic, including percentages (write 17.5% of X as 0.175*X). "
                     "Supports + - * / ** % parentheses and sqrt(x)."),
     "input_schema": {"type": "object", "properties": {"expression": {
         "type": "string", "description": "e.g. '0.175 * 84213' or 'sqrt(2) * 50'"}},
         "required": ["expression"]}},
    {"name": "percent_change",
     "description": "Percent change from old to new, e.g. revenue growth.",
     "input_schema": {"type": "object", "properties": {
         "old": {"type": "number"}, "new": {"type": "number"}}, "required": ["old", "new"]}},
]

def run_tool(name: str, args: dict) -> tuple[str, bool]:
    """Exercise 2.5: errors come back as data with is_error=True."""
    try:
        return str(REGISTRY[name](**args)), False
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}", True

def ask(question: str, max_rounds: int = 5) -> str:
    """Exercise 2.6's fix: keep going while the model asks for tools (a mini chapter 4)."""
    messages = [{"role": "user", "content": question}]
    for _ in range(max_rounds):
        r = client.messages.create(model=MODEL, max_tokens=2000, tools=TOOLS,
                                   messages=messages)
        if r.stop_reason != "tool_use":
            return "".join(b.text for b in r.content if b.type == "text")
        messages.append({"role": "assistant", "content": r.content})
        results = []
        for b in r.content:
            if b.type == "tool_use":
                out, is_error = run_tool(b.name, b.input)
                print(f"  -> {b.name}({b.input}) = {out}")
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "content": out, "is_error": is_error})
        messages.append({"role": "user", "content": results})
    return "Stopped: too many tool rounds."

if __name__ == "__main__":
    for q in ["What is the square root of 2 times 50?", "What is 5 divided by zero?",
              "Revenue went from 84,213 to 97,400. What is the percent change, and what "
              "is 17.5% of the new figure?"]:
        print(q, "\n", ask(q), "\n")
