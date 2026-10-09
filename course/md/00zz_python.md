# Interlude: The Python You'll Need

Agent code leans on a few Python features that beginner tours often skip: calling a function with a dictionary of arguments, storing functions in a dictionary, small classes and decorators. This interlude gathers them in one runnable file and one pattern, the tool registry, that you'll see in almost every chapter. By the end, you'll have written your own `run_tool` and a decorator that registers tools.

**Prerequisites:** Chapter 0, or some experience writing Python. Like Chapter 0, this interlude is part of the **optional beginner path**: if `fn(**args)`, a dictionary of functions, a dataclass and a decorator all look familiar, skip to Chapter 1 and come back only if a listing puzzles you.

## Learning objectives

By the end of this interlude you can:

- Build lists and dictionaries with comprehensions.
- Call a function with a dictionary of arguments (`fn(**args)`), the pattern every tool uses.
- Store functions in dictionaries and sort with `key=lambda ...`.
- Write a small class and a dataclass.
- Read and write a decorator, the pattern behind `@mcp.tool()`.

## Who this interlude is for

Chapter 0's tour covers values, lists, dictionaries, functions, loops, errors and files. The chapters also use a handful of features the tour doesn't show. If you've never programmed, take your time with Chapter 0 and this interlude: type the examples, break them and fix them. It's the best investment you'll make in this book. If you can already read the file below without surprises, do exercise P.5 to check yourself, then move on.

This book teaches only the Python that agents need, and teaches it quickly. {{t:python-fundamentals}} lists the fundamentals the chapters take for granted, where each one first matters and where to read more. The links point to the free official Python tutorial (docs.python.org/3/tutorial) unless noted. If a row feels shaky, read that section before Chapter 1; you don't need anything beyond this list.

Table: The Python fundamentals this book assumes {#t:python-fundamentals}
| Fundamental | You'll need it for | Read more |
| --- | --- | --- |
| Values, strings, f-strings, `print` | Every program; formatting tool results | Tutorial 3, "An Informal Introduction" |
| `if`, `for`, `while`, `break` | The agent loop and its iteration cap (Chapter 4) | Tutorial 4, "More Control Flow Tools" |
| Functions, default and keyword arguments, `**kwargs`, `lambda` | Every tool; `run_tool` (Chapter 3) | Tutorial 4.8 and 4.9 |
| Lists, dictionaries, comprehensions | Messages, tool inputs and results | Tutorial 5, "Data Structures" |
| Modules, `import`, packages | Splitting agents into files; the SDK | Tutorial 6, "Modules" |
| Files, `pathlib`, the `json` module | Saved state and notes (Chapters 5–6) | Tutorial 7, "Input and Output" |
| Exceptions: `try`, `except`, `raise` | Turning tool errors into text (Chapter 7) | Tutorial 8, "Errors and Exceptions" |
| Classes and `@dataclass` | The MCP hub and policy layer (Chapters 13–14) | Tutorial 9, "Classes" |
| Type hints (`str`, `int`, `list[str]`, `dict`) | MCP builds tool schemas from them (Chapter 12) | mypy's "Type hints cheat sheet" |
| Virtual environments and `pip` | Running your own projects outside the course kit | Tutorial 12, "Virtual Environments and Packages" |

Asynchronous code (`async` and `await`) has its own interlude before Chapter 11. For a longer, gentler start, the courses in this interlude's **Learn more** section teach the same fundamentals from scratch, and Python Tutor lets you watch your code run one line at a time.

## P.1 Six features, one file

@@code i_python.py

Run it with `./course.sh python i_python.py`. Each section prints a line starting with its number, so you can match output to code.

Table: The six features in `i_python.py`
| Section | Feature | Where this book uses it |
| --- | --- | --- |
| 1 | Comprehensions and `sum(... for ...)` | Collecting tool results (Chapter 4), totals in evals (Chapter 27) |
| 2 | `fn(**args)` and `**kwargs` | Every `run_tool`: the model sends a dictionary, your code calls the function with it |
| 3 | Functions in dictionaries, `lambda` | `REGISTRY` in Chapter 3; sorting results |
| 4 | Classes and `@dataclass` | The MCP hub (Chapter 13), the policy layer (Chapter 14) |
| 5 | Decorators | `@mcp.tool()` (Chapter 12), `@beta_tool` (Chapter 24) |
| 6 | `:=`, unpacking, f-string formats, specific `except` | Everywhere |

## P.2 The one pattern to understand deeply

Almost every chapter contains some version of this:

```
REGISTRY = {"add_task": add_task, "list_tasks": list_tasks}

def run_tool(name, args):
    try:
        return str(REGISTRY[name](**args))
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"
```

Read it slowly. `REGISTRY[name]` looks up a **function** by its name. `(**args)` calls it with the model's arguments, unpacking the dictionary into named arguments. `try/except` turns any failure into text the model can read. Understand these lines and you understand how an agent's tools are wired. Exercise P.2 has you write it.

## Common mistakes

- **Using `[]` or `{}` as a default argument.** Every call shares the same list. Use `None` and create the list inside the function, or `field(default_factory=list)` in a dataclass.
- **Forgetting `self`** as the first parameter of a method.
- **Catching every error silently** (`except: pass`). Catch the errors you expect and report them.
- **Calling `fn(args)` instead of `fn(**args)`**: the function receives one dictionary instead of named arguments.

## Key takeaways

- Comprehensions build lists and dictionaries in one line.
- `fn(**args)` calls a function with a dictionary of arguments: this is how tools are called.
- Functions are values: store them in dictionaries and pass them around.
- Classes bundle data with the functions that use it; dataclasses are classes for data.
- Decorators wrap or register functions.

With Part 0 behind you, Chapter 1 puts these pieces to work. You'll make your first call to the model from Python and build a summarizer, the first small program in this book that hands real work to a model.

## Learn more

Start with these. `RESOURCES.md` in the course kit has all 9 links for this chapter, including the **Go deeper** reading, ready to click.

| Resource | What you'll find |
| --- | --- |
| **The official Python tutorial**<br>[docs.python.org/3/tutorial](https://docs.python.org/3/tutorial/) | Free and complete; chapters 3 to 5 and 9 cover this interlude |
| **Python for Everybody**<br>[py4e.com](https://www.py4e.com) | A free beginner course with videos, for people who have never programmed |
| **CS50's Introduction to Programming with Python**<br>[cs50.harvard.edu/python](https://cs50.harvard.edu/python/) | Harvard's free Python course with lectures and problem sets |

## Exercises

Every exercise here comes with a starter file (with the function names and examples in place) and a checker: run `./course.sh check <id>` to see whether your code is right.

:::ex Simple | P.1 | Comprehensions
In the starter, write `shipped_ids(orders)` (the ids of shipped orders, in order), `totals_by_status(orders)` (a dictionary of status to total amount) and `names_over(products, min_price)` (names of products above a price), each in one or two lines.
**Hint:** Section 1 of `i_python.py`. For `totals_by_status`, a loop with `dict.get(key, 0)` is fine too.
**Done when:** `./course.sh check P.1` passes.
:::

:::ex Simple | P.2 | Call tools by name
Write `run_tool(name, args)` that looks up `name` in the starter's `REGISTRY`, calls it with `**args` and returns the result as text. An unknown name or a failing call must return a string starting with `ERROR:`, never crash.
**Hint:** Section P.2 above is almost the whole answer. Test it with a wrong argument name too.
**Done when:** `./course.sh check P.2` passes.
:::

:::ex Medium | P.3 | A class of your own
Write a `TaskList` class with `add(title, due=None)` returning the new task's id, `complete(task_id)` returning `True` (or `False` for an unknown id), and `open_tasks()` returning the open tasks' titles, oldest first. Store tasks as `Task` dataclass objects.
**Hint:** Section 4. Number tasks 1, 2, 3... with `len(self.tasks) + 1`.
**Done when:** `./course.sh check P.3` passes.
:::

:::ex Medium | P.4 | Decorators
Write a `tool` decorator that registers a function in `TOOLS` under its name, with its docstring as the description, and returns the function unchanged. Then write `count_calls`, a decorator that records in a `calls` dictionary how many times each function was called.
**Hint:** Section 5. A decorator is a function that takes a function and returns a function.
**Done when:** `./course.sh check P.4` passes.
:::

:::ex Medium | P.5 | Find the bugs
The starter file has three functions, each with one bug: a shared default list, a wrong loop range and an error that is silently swallowed. Fix all three without rewriting the functions.
**Done when:** `./course.sh check P.5` passes, and you can name each bug.
:::

## Checkpoint: ready for Chapter 1?

You're ready to move on if you can, without looking back:

- [ ] Build a filtered list from a list of dictionaries in one line.
- [ ] Explain what `REGISTRY[name](**args)` does, piece by piece.
- [ ] Write a small class with two methods, and a dataclass.
- [ ] Explain what `@tool` above a function does.
- [ ] Spot a mutable default argument.

If two or more feel shaky, redo P.2 and P.3: they're the patterns you'll use most.
