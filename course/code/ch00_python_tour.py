"""Chapter 0: the Python you need for this course, in one runnable file.
Run it, read the output next to the code, then change things and run it again."""

# ---- 1. Values and variables -------------------------------------------------
name = "Asha"                 # a string (text)
tasks_done = 3                # an integer
price = 19.99                 # a float (decimal number)
is_admin = False              # a boolean: True or False
nothing = None                # "no value yet"
print(f"{name} finished {tasks_done} tasks; price {price:.2f}; admin={is_admin}")

# ---- 2. Lists: ordered collections --------------------------------------------
cities = ["Pune", "Seattle", "Berlin"]
cities.append("Austin")                     # add to the end
print(cities[0], cities[-1], len(cities))   # first, last, how many
for city in cities:                         # loop over every item
    print(" -", city.upper())

# ---- 3. Dictionaries: named fields (the shape of almost all API data) ---------
order = {"id": "A1001", "items": ["Laptop", "Mouse"], "total": 1225.0, "paid": True}
print(order["id"], order.get("coupon", "no coupon"))   # .get gives a default if missing
order["status"] = "shipped"                            # add or change a field
for key, value in order.items():
    print(f"  {key} = {value}")

# ---- 4. Functions: reusable steps with inputs and an output --------------------
def total_with_tax(amount: float, rate: float = 0.08) -> float:
    """Return amount plus tax, rounded to cents."""
    return round(amount * (1 + rate), 2)

print(total_with_tax(100), total_with_tax(100, rate=0.18))

# ---- 5. Decisions and loops ---------------------------------------------------
def classify(temperature_c: float) -> str:
    if temperature_c < 10:
        return "cold"
    elif temperature_c < 25:
        return "mild"
    else:
        return "hot"

readings = [4.5, 18.0, 31.2]
labels = [classify(t) for t in readings]    # a "list comprehension": a loop in one line
print(dict(zip(readings, labels)))

# ---- 6. Errors: expect them, handle them ---------------------------------------
def safe_divide(a: float, b: float) -> str:
    try:
        return str(a / b)
    except ZeroDivisionError as exc:
        return f"ERROR: {exc}"                # agents return errors as text (chapter 2)

print(safe_divide(10, 4), safe_divide(1, 0))

# ---- 7. Files ------------------------------------------------------------------
from pathlib import Path

note = Path("hello_note.txt")
note.write_text("first line\nsecond line\n")
print(note.read_text().splitlines())
note.unlink()                                  # delete it again

# ---- 8. Modules: code from other files and libraries -------------------------
import math                                    # from Python's standard library
from datetime import date                      # one name from a module
print(math.sqrt(2), date.today().isoformat())
