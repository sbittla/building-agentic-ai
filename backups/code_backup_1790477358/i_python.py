"""Interlude (Python): the features the course uses that Chapter 0's tour doesn't show.
Run it, read each output next to its code, then change something and run it again."""
import time
from dataclasses import dataclass, field

# ---- 1. Comprehensions: build a list or dict from another, in one line -------------
orders = [{"id": "A1", "status": "shipped", "total": 120.0},
          {"id": "A2", "status": "cancelled", "total": 80.0},
          {"id": "A3", "status": "shipped", "total": 45.5}]
shipped = [o["id"] for o in orders if o["status"] == "shipped"]      # a filtered list
totals = {o["id"]: o["total"] for o in orders}                        # a dict
# no brackets: a generator
revenue = sum(o["total"] for o in orders if o["status"] != "cancelled")
print("1.", shipped, totals, revenue)

# ---- 2. Keyword arguments, and calling a function with a dict of them --------------
def add_task(title: str, due: str | None = None, priority: str = "normal") -> str:
    return f"added {title!r} due={due} priority={priority}"

# what a model sends as tool input
args = {"title": "renew passport", "due": "2026-11-01"}
print("2.", add_task(**args))            # ** unpacks the dict into arguments

def log_call(name, *args, **kwargs):     # *args / **kwargs COLLECT extras
    print("2.", name, "positional:", args, "keyword:", kwargs)
log_call("demo", 1, 2, verbose=True)

# ---- 3. Functions are values: store them, pass them, look them up ------------------
REGISTRY = {"add_task": add_task}                            # name -> function
print("3.", REGISTRY["add_task"](title="call bank"))
# lambda: a tiny unnamed function
by_total = sorted(orders, key=lambda o: o["total"], reverse=True)
print("3.", [o["id"] for o in by_total])

# ---- 4. Classes: data plus the functions that work on it ---------------------------
class TaskList:
    def __init__(self):                  # runs when you write TaskList()
        self.tasks = []                  # self = this particular task list

    def add(self, title: str) -> int:
        self.tasks.append({"title": title, "done": False})
        return len(self.tasks)           # the new task's number

    def open_titles(self) -> list[str]:
        return [t["title"] for t in self.tasks if not t["done"]]

todo = TaskList()
todo.add("buy milk"); todo.add("call bank")
todo.tasks[0]["done"] = True
print("4.", todo.open_titles())

# a class that's mostly data: __init__ is written for you
@dataclass
class Task:
    title: str
    due: str | None = None
    # never use [] as a default: it's shared!
    tags: list[str] = field(default_factory=list)
print("4.", Task("renew passport", due="2026-11-01"))

# ---- 5. Decorators: wrap a function to add behavior --------------------------------
def timed(fn):
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"5. {fn.__name__} took {(time.perf_counter() - t0) * 1000:.1f} ms")
        return result
    return wrapper

@timed                                    # same as: slow_square = timed(slow_square)
def slow_square(x):
    time.sleep(0.01)
    return x * x
print("5.", slow_square(7))

TOOLS = {}
# how @mcp.tool() works in chapter 12, in miniature
def tool(fn):
    TOOLS[fn.__name__] = {"function": fn, "description": fn.__doc__}
    return fn

@tool
def get_time() -> str:
    """Current time as HH:MM."""
    return time.strftime("%H:%M")
print("5.", list(TOOLS), TOOLS["get_time"]["description"])

# ---- 6. Small things you'll see everywhere -----------------------------------------
if (n := len(shipped)) > 1:               # := assigns AND tests in one go
    print(f"6. {n} shipped orders")
first, *rest = ["a", "b", "c"]            # unpacking
print("6.", first, rest, f"{1234.5:,.2f}", f"{'left':<8}|", repr("line\nbreak"))
try:
    int("abc")
except ValueError as exc:                 # catch the specific error you expect
    print("6. could not convert:", exc)
