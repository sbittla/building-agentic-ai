# Interlude: SQL in One Sitting

An agent hands you a tidy table of revenue per customer. Is it right? A query that summed prices instead of quantity × price looks just as tidy. This interlude teaches enough SQL to tell, in one sitting: eight queries against a small shop database, a checklist for reviewing someone else's SQL, and why user text never goes into a query. `EXTRA_PRACTICE.md` in the course kit has more.

**Prerequisites:** Chapter 0. You don't need any database experience.

## Learning objectives

By the end of this interlude you can:

- Write SELECT queries with filters, sorting, aggregates, grouping and joins.
- Keep user text out of SQL with `?` parameters.
- Break a complex query into steps with a CTE.
- Review an agent's SQL in a fixed order and spot common mistakes.

## Why this interlude

**SQL** (Structured Query Language) is how you ask a database questions. Chapter 8 needs it twice: to judge the agent's queries and to write your own evaluation queries. The kit's `shop.db` has four tables:

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

Run it with `./course.sh python i_sql.py` and read each query next to its result:

1. `SELECT … FROM … WHERE …` picks columns and filters rows.
2. `ORDER BY … DESC LIMIT n` sorts and keeps the top n.
3. `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` summarize many rows into one.
4. `GROUP BY` summarizes per group: one result row per status.
5. `JOIN … ON …` combines tables using matching ids.
6. Joins and grouping together answer real questions, such as revenue per category.
7. `?` **parameters** keep user text out of the SQL itself. Paste user text into SQL and you invite *SQL injection*, where crafted input changes what the query does.
8. `WITH name AS (…)` (a **CTE**) names an intermediate result, so a complex query reads in steps.

## S.2 Reading someone else's SQL

When an agent shows you a query, check it in this order:

1. **FROM and JOIN**: are these the right tables, joined on the right ids?
2. **WHERE**: are the right rows included (for example, cancelled orders excluded)?
3. **GROUP BY**: is it grouped by what the question asks about?
4. **SELECT**: are the numbers computed correctly (quantity × price, not just price)?
5. **ORDER BY / LIMIT**: is "top 5" really sorted by the right thing?

To explore on your own, run `./course.sh shell`, then `sqlite3 shop.db`, and type queries ending with `;` (`.tables` lists tables, `.quit` exits).

## Key takeaways

- `SELECT … FROM … WHERE` picks and filters; `ORDER BY` and `LIMIT` sort and trim.
- Aggregates with `GROUP BY` summarize; `JOIN` combines tables on matching ids.
- Parameters prevent SQL injection; CTEs make long queries readable.
- Review someone else's SQL in order, from FROM and JOIN to ORDER BY.

## Learn more

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

## Up next

In Chapter 8 an agent writes SQL you've never seen against `shop.db`, and some of it will be wrong. You'll make sure it can't do damage, and teach it to fix its own mistakes.
