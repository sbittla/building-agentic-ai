def add(a: float, b: float) -> float:
    return a + b


def greet(name: str, excited: bool = False) -> str:
    return f"Hello, {name}{'!' if excited else '.'}"


REGISTRY = {"add": add, "greet": greet}


def run_tool(name: str, args: dict) -> str:
    """Call REGISTRY[name] with **args and return the result as a string.
    Unknown names and failing calls return a string starting with "ERROR:"."""
    raise NotImplementedError


if __name__ == "__main__":
    print(run_tool("add", {"a": 2, "b": 3}))              # 5
    print(run_tool("greet", {"name": "Asha", "excited": True}))
    print(run_tool("greet", {"nme": "typo"}))             # ERROR: ...
    print(run_tool("fly", {}))                            # ERROR: ...
