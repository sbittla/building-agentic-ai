"""Exercise P.5 (solution): decorators."""
import functools

TOOLS = {}
calls = {}

def tool(fn):
    TOOLS[fn.__name__] = {"function": fn, "description": fn.__doc__}
    return fn

def count_calls(fn):
    @functools.wraps(fn)                      # keeps fn's name and docstring on the wrapper
    def wrapper(*args, **kwargs):
        calls[fn.__name__] = calls.get(fn.__name__, 0) + 1
        return fn(*args, **kwargs)
    return wrapper

@tool
def get_weather(city: str) -> str:
    """Weather for a city."""
    return f"sunny in {city}"

@count_calls
def ping() -> str:
    return "pong"

if __name__ == "__main__":
    print(TOOLS["get_weather"]["description"]); ping(); ping(); print(calls)
