# Interlude: SQL in One Sitting

In the next chapter an agent writes database queries for you, and you need to tell a right query from a plausible wrong one. This interlude teaches only the SQL Chapter 8 needs, in one sitting. You'll run eight queries against a small shop database, learn a checklist for reviewing someone else's SQL and see why user text must never be pasted into a query. Window functions, self-joins and more practice are in `EXTRA_PRACTICE.md` in the course kit.

**Prerequisites:** Chapter 0. You don't need any database experience.

## Learning objectives

By the end of this interlude you can:

- Read and write SELECT queries with filters, sorting, aggregates, grouping and joins.
- Keep user text out of SQL with `?` parameters.
- Break a complex query into steps with a CTE.
- Review an agent's SQL in a fixed order and spot common mistakes.

## Why this interlude

In Chapter 8 an agent writes SQL for you. To judge whether its SQL is right, and to write evaluation queries yourself, you need to read SQL comfortably. **SQL** (Structured Query Language) is the language for asking a database questions. The kit's `shop.db` has four tables:

Table: The tables in `shop.db`
| Table | Columns | One row is |
| --- | --- | --- |
| `customers` | `id, name, city, joined` | A customer |
| `products` | `id, name, category, price` | A product |
| `orders` | `id, customer_id, order_date, status` | An order |
| `order_items` | `order_id, product_id, quantity` | One product line in an order |

@@image d-ccd852657079.png

Figure: The tables of `shop.db` and how they relate
Alt: Entity-relationship diagram: a customer places zero or more orders; an order contains one or more order items; a product appears in zero or more order items.

## S.1 Eight queries, each building on the last

@@code i_sql.py

Run it with `./course.sh python i_sql.py`, and read each query alongside its result:

1. `SELECT … FROM … WHERE …` picks columns and filters rows.
2. `ORDER BY … DESC LIMIT n` sorts and keeps the top n.
3. `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` summarize many rows into one.
4. `GROUP BY` summarizes per group: one result row per status.
5. `JOIN … ON …` combines tables using matching ids.
6. Joins and grouping together answer real questions, such as revenue per category.
7. `?` **parameters** keep user text out of the SQL itself. Pasting user text into SQL causes *SQL injection*, where crafted input changes what the query does.
8. `WITH name AS (…)` (a **CTE**) names an intermediate result so a complex query reads in steps.

## S.2 Reading someone else's SQL

When an agent shows you a query, check it in this order:

1. **FROM and JOIN**: are these the right tables, joined on the right ids?
2. **WHERE**: are the right rows included (for example, cancelled orders excluded)?
3. **GROUP BY**: is it grouped by what the question asks about?
4. **SELECT**: are the numbers computed correctly (quantity × price, not just price)?
5. **ORDER BY / LIMIT**: is "top 5" really sorted by the right thing?

You can also explore interactively: run `./course.sh shell`, then `sqlite3 shop.db`, then type queries ending with `;` (`.tables` lists tables, `.quit` exits).

## Key takeaways

- `SELECT … FROM … WHERE` picks and filters; `ORDER BY` and `LIMIT` sort and trim.
- Aggregates with `GROUP BY` summarize; `JOIN` combines tables on matching ids.
- Parameters prevent SQL injection; CTEs make long queries readable.
- Check someone else's SQL from FROM and JOIN through to ORDER BY.

You can now read the queries an agent writes. Chapter 8 puts that skill to use: you'll build an agent that answers questions about `shop.db` by writing SQL, catches its own errors and checks its answers against results you know are right.

## Learn more

Start with these. `RESOURCES.md` in the course kit has all 4 links for this chapter, including the **Go deeper** reading, ready to click.

| Resource | What you'll find |
| --- | --- |
| **SQLBolt**<br>[sqlbolt.com](https://sqlbolt.com) | Free interactive SQL lessons in the browser |
| **W3Schools SQL tutorial**<br>[w3schools.com/sql](https://www.w3schools.com/sql/) | Short pages with a try-it editor for each statement |

## Exercises

Each exercise starts from a file with the queries to complete. Run `./course.sh check S.1` (S.2, ...) to compare your results with the correct ones.

:::ex Simple | S.1 | Warm-up queries
Write queries for: (a) all customers in Berlin; (b) the three cheapest products; (c) how many orders are pending.
**Done when:** Your answers match a second count you make a different way in `sqlite3`.
:::

:::ex Simple | S.2 | Spot the bug
This query is meant to give revenue per customer but is wrong in three ways. Find them: `SELECT c.name, SUM(p.price) FROM customers c JOIN orders o ON o.id = c.id JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id GROUP BY c.name`.
**Done when:** You've named all three bugs and written the fixed query.
:::

:::ex Medium | S.3 | Safe parameters
Write a Python function `orders_for_city(city)` that returns the number of orders from customers in a city, using a `?` parameter. Then show what goes wrong if you build the SQL with an f-string and pass `Pune' OR '1'='1`.
**Done when:** The parameter version returns 0 for the malicious input, and you can explain what the f-string version did.
:::
