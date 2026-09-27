---
name: customer-lookup
description: Looks up one customer in the shop database and shows their profile, order history and total spend. Use when the user asks about a specific customer by name or id, or asks "who is", "what did X buy" or "how much has X spent".
---
# Customer lookup

1. Read `references/tables.md` for the joins.
2. Find the customer by id, or with `WHERE name LIKE '%<name>%'`. If more than one matches, list them
   (id, name, city) and ask which one; don't guess.
3. Show, in this order:
   - **Name, city, customer since** (the `joined` date)
   - **Orders:** count, first and last order date
   - **Total spend:** SUM(quantity * price) over shipped orders
   - **Top 3 products** by spend
4. Every number must come from a query in this conversation.
