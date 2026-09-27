"""Exercise P.2 (solution): call tools by name, never crash."""
def add(a: float, b: float) -> float:
    return a + b

def greet(name: str, excited: bool = False) -> str:
    return f"Hello, {name}{'!' if excited else '.'}"

REGISTRY = {"add": add, "greet": greet}

def run_tool(name: str, args: dict) -> str:
    if name not in REGISTRY:
        return f"ERROR: unknown tool '{name}'. Known tools: {', '.join(REGISTRY)}"
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

if __name__ == "__main__":
    print(run_tool("add", {"a": 2, "b": 3}), run_tool("greet", {"nme": "x"}), run_tool("fly", {}))
