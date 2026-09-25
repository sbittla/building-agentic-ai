"""Each function has ONE bug. Fix it without rewriting the function."""


def add_tag(tag, tags=[]):
    """Return a list of tags with `tag` added. Each call without `tags` starts empty."""
    tags.append(tag)
    return tags


def last_n(items, n):
    """The last n items, in order. last_n([1, 2, 3, 4], 2) == [3, 4]"""
    return [items[i] for i in range(len(items) - n - 1, len(items))]


def parse_amount(text):
    """'12.50' -> 12.5. For anything that isn't a number, return an "ERROR: ..." string."""
    try:
        return float(text)
    except Exception:
        pass


if __name__ == "__main__":
    print(add_tag("a"), add_tag("b"))          # ['a'] ['b']
    print(last_n([1, 2, 3, 4], 2))              # [3, 4]
    print(parse_amount("x"))                    # ERROR: ...
