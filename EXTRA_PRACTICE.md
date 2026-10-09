# Extra Practice: More Regex, More SQL and Three Extra Exercises

The book's regular-expression and SQL interludes teach only what the chapters need: patterns for validating agent inputs, reading logs and hiding secrets, and the queries Chapter 8's agent writes. This guide is the broader material for readers who want more, plus three extra exercises that run like any other in the course kit:

```
./course.sh ex X.1          # create your starter file
./course.sh check X.1       # check it
./course.sh solution X.1    # compare with the reference
```

| Exercise | Level | Practises |
| --- | --- | --- |
| X.1 Error codes | Medium | Word boundaries; why exact matching beats embeddings for identifiers |
| X.2 Business questions | Medium | Date grouping, `NOT EXISTS` and a self-join on `shop.db` |
| X.3 The hard conversations | Concept | Telling a customer about a slip, and answering "it's wrong" (Chapter 31, `FIELD_GUIDE.md`) |

## 1. More regular expressions

Run these in `./course.sh python` (start with `import re`).

### Matching more precisely

| Pattern or flag | What it does | Example |
| --- | --- | --- |
| `\b` | A word boundary: the edge between a word character and anything else | `\bERR-\d{4}\b` matches `ERR-4471`, not `XERR-4471` |
| `{m,n}` | Between m and n times | `\d{2,4}` |
| `*?`, `+?` | Lazy: as few characters as possible | `<.+?>` matches one tag, not everything from the first `<` to the last `>` |
| `[^...]` | Any character *not* in the set | `"[^"]*"` matches a quoted string |
| `(?:...)` | A group that doesn't capture | `(?:ERROR\|WARN) (\w+)` captures only the word after the level |
| `(?P<name>...)` | A named group | `m.group("date")` instead of `m.group(1)` |
| `(?=...)`, `(?!...)` | Look ahead without consuming: must, or must not, follow | `\d+(?=ms)` matches the number in `800ms` but not `ms` |
| `re.IGNORECASE` | Case doesn't matter | `re.search(r"timeout", "TIMEOUT", re.I)` |
| `re.MULTILINE` | `^` and `$` match at every line | `re.findall(r"^ERROR.*$", log, re.M)` |
| `re.VERBOSE` | Whitespace and `#` comments allowed inside the pattern | Long patterns you'll read again |

### Parsing a fixed format with named groups

```python
import re
LINE = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>[\d:]+) (?P<level>\w+)\s+(?P<service>\S+)")
m = LINE.match("2026-09-22 14:05:11 ERROR checkout-service order=A1001 timeout after 800ms")
print(m.group("date"), m.group("level"), m.group("service"))
print(m.groupdict())
```

`re.match` anchors at the start only; `re.fullmatch` requires the whole text to fit. Use `fullmatch` to validate an input, `match` to parse the front of a line. Compile a pattern you use often with `re.compile`; it's clearer, and you can give it a name.

### Pitfalls

- **Catastrophic backtracking.** Nested repetition such as `(a+)+$` can take exponential time on a long string that almost matches. Avoid nested quantifiers on untrusted input, and put a length limit before the regex.
- **Greedy by default.** `.*` grabs as much as it can; reach for `.*?` or a negated set.
- **Not a parser.** Regex can't match nested structures (HTML, JSON, balanced brackets). Use `json`, `html.parser` or a real parser.
- **Not a security check.** Path traversal, SQL injection and HTML sanitizing need proper tools (Chapters 6, 8 and 25).

### More practice

1. Extract every `key=value` pair from a log line into a dict.
2. Write a pattern for ISO dates (`2026-09-22`) that rejects month `13`. Then decide whether a regex is the right tool, or `datetime.date.fromisoformat`.
3. Mask email addresses but keep the domain: `ana@example.com` becomes `***@example.com`.
4. **Exercise X.1: Error codes.** Write a pattern that finds error codes like `ERR-4471` but not `ERR-44` or `XERR-4471`, and explain why embedding-based search (Chapter 18) might confuse `ERR-4471` with `ERR-4417` while this pattern can't. *Done when:* your pattern passes five examples you write, and your explanation is two sentences. (`./course.sh ex X.1`)

## 2. More SQL

All on the kit's `shop.db` (`./course.sh shell`, then `sqlite3 shop.db`).

### Beyond the interlude

| Feature | What it's for | Example |
| --- | --- | --- |
| `HAVING` | Filter groups after `GROUP BY` | `SELECT customer_id, COUNT(*) n FROM orders GROUP BY customer_id HAVING n >= 10` |
| `LEFT JOIN` | Keep rows with no match (the missing side is `NULL`) | Customers with no orders: `... LEFT JOIN orders o ON o.customer_id = c.id WHERE o.id IS NULL` |
| `NOT EXISTS` | "Has no row like this" | Customers who never cancelled (exercise X.2 b) |
| Subquery | A query inside a query | `SELECT name FROM products WHERE price > (SELECT AVG(price) FROM products)` |
| Self-join | Compare rows of one table | Products bought in the same order (exercise X.2 c) |
| `strftime` | Group by month or week in SQLite | `strftime('%Y-%m', order_date)` |
| Window functions | A value per row computed over a group, without collapsing it | `RANK() OVER (PARTITION BY category ORDER BY price DESC)` |
| `CASE` | Conditional values | `SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END)` |
| `EXPLAIN QUERY PLAN` | How SQLite will run a query: is there an index? | `EXPLAIN QUERY PLAN SELECT * FROM orders WHERE customer_id = 13` |

### Pitfalls an agent's SQL often has

- **`NULL` isn't equal to anything**, including `NULL`: use `IS NULL`. `COUNT(column)` skips `NULL`s; `COUNT(*)` doesn't.
- **A join that multiplies rows.** Joining orders to order items and then summing an order-level column counts it once per item.
- **Integer division.** In SQLite `3 / 2` is `1`; write `3.0 / 2` or `CAST(x AS REAL)`.
- **Dates as text.** Comparisons work only if every date is in the same `YYYY-MM-DD` format.

### More practice

1. The top product in each category by revenue, with a window function.
2. Each customer's first order date and how many days until their second order.
3. The share of orders cancelled per city, as a percentage with one decimal.
4. **Exercise X.2: Business questions.** Write queries for: (a) revenue per month in 2025, excluding cancelled orders; (b) customers who have never cancelled an order; (c) the product most often bought together with a Laptop. *Hint:* for (c), join `order_items` to itself on `order_id`. *Done when:* each query runs and you can explain every line. (`./course.sh ex X.2`)

## 3. Exercise X.3: The hard conversations

Write what you'd say, in five sentences or fewer each: (a) to Lakeside's customer owner (Chapter 31), when the pilot will slip three weeks because scanned PDFs need OCR; (b) to an adjuster who says "the summaries are wrong half the time". *Done when:* (a) gives the cause, what's done, the new date and an option to cut scope; (b) asks for examples and says how they'll become evaluation cases. [FIELD_GUIDE.md](FIELD_GUIDE.md), section 4, has the pattern; `./course.sh solution X.3` has a sample answer.

## Further reading

- [regex101](https://regex101.com) (choose the Python flavor) and the [Python `re` documentation](https://docs.python.org/3/library/re.html).
- [SQLite: SELECT](https://www.sqlite.org/lang_select.html) and [window functions](https://www.sqlite.org/windowfunctions.html).
