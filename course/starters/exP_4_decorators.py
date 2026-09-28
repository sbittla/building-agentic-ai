TOOLS = {}     # name -> {"function": fn, "description": docstring}
calls = {}     # name -> how many times it was called


def tool(fn):
    """Register fn in TOOLS (under fn.__name__, with fn.__doc__) and return fn unchanged."""
    raise NotImplementedError


def count_calls(fn):
    """Return a wrapper that adds 1 to calls[fn.__name__] every time, then calls fn."""
    raise NotImplementedError


@tool
def get_weather(city: str) -> str:
    """Weather for a city."""
    return f"sunny in {city}"


@count_calls
def ping() -> str:
    return "pong"


if __name__ == "__main__":
    print(TOOLS["get_weather"]["description"]); ping(); ping(); print(calls)
