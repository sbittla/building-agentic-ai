# Joins for customer questions
- orders.customer_id -> customers.id
- order_items.order_id -> orders.id
- order_items.product_id -> products.id
Spend = SUM(order_items.quantity * products.price) WHERE orders.status = 'shipped'.
