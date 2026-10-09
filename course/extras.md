# Extra Practice (course kit)

Exercises beyond the book. The guide to them, with the extra regular-expression and SQL material, is `EXTRA_PRACTICE.md` at the top of the course kit. Run them like any other: `./course.sh ex X.1`, `./course.sh check X.1`, `./course.sh solution X.1`.

:::ex Medium | X.1 | Error codes
Write a pattern that finds error codes like `ERR-4471` but not `ERR-44` or `XERR-4471`, and explain why embedding-based search (Chapter 18) might confuse `ERR-4471` with `ERR-4417` while this pattern can't.
**Hint:** `\b` matches a word boundary.
**Done when:** Your pattern passes five examples you write, and your explanation is two sentences.
:::

:::ex Medium | X.2 | Business questions
Write queries for: (a) revenue per month in 2025, excluding cancelled orders; (b) customers who have never cancelled an order; (c) the product most often bought together with a Laptop.
**Hint:** For (c), join `order_items` to itself on `order_id`.
**Done when:** Each query runs and you can explain every line.
:::

:::ex Concept | X.3 | The hard conversations
Write what you'd say, in five sentences or fewer each: (a) to Lakeside's customer owner (Chapter 31), when the pilot will slip three weeks because scanned PDFs need OCR; (b) to an adjuster who says "the summaries are wrong half the time".
**Done when:** (a) gives the cause, what's done, the new date and an option to cut scope; (b) asks for examples and says how they'll become evaluation cases.
:::
