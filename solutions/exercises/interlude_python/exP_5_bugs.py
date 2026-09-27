"""Exercise P.5 (solution): three bugs fixed.
1. add_tag: a list default is created ONCE and shared by every call. Use None.
2. last_n: the range started one item too early (len - n - 1). It's len - n.
3. parse_amount: `except Exception: pass` returned None silently. Catch the
   specific error and return a message the caller (or a model) can act on."""

def add_tag(tag, tags=None):
    tags = [] if tags is None else tags
    tags.append(tag)
    return tags

def last_n(items, n):
    return [items[i] for i in range(len(items) - n, len(items))]

def parse_amount(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return f"ERROR: {text!r} is not a number"

if __name__ == "__main__":
    print(add_tag("a"), add_tag("b"), last_n([1, 2, 3, 4], 2), parse_amount("x"))
