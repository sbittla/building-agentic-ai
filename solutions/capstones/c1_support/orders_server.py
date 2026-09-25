"""Capstone 1: order lookups and returns (within policy) for the SIGNED-IN customer.

Who the customer is comes from the host, out of band: the host starts this server with
CUSTOMER_EMAIL set from its login session. No tool takes an email argument, so nothing
the model (or a customer's message) writes can make it act for someone else."""
import json, logging, os, sqlite3, sys
from datetime import date
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from data import DB, TODAY

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
RETURN_DAYS = 30
mcp = MCPServer("orders")

def _customer() -> str:
    email = os.environ.get("CUSTOMER_EMAIL", "").strip().lower()
    if not email:
        raise ToolError("No customer is signed in; order tools are unavailable.")
    return email

def _order(order_id):
    email = _customer()
    with sqlite3.connect(f"file:{DB}?mode=ro", uri=True) as con:
        row = con.execute("SELECT order_id, email, status, delivered, total, items FROM orders "
                          "WHERE order_id = ?", (order_id.strip().upper(),)).fetchone()
    # Same message for "no such order" and "wrong email": never confirm someone else's order.
    if not row or row[1].lower() != email:
        raise ToolError("No order with that ID on this customer's account. Ask them to check the ID.")
    return dict(zip(["order_id", "email", "status", "delivered", "total", "items"], row))

@mcp.tool()
def get_order(order_id: str) -> str:
    """Look up one of the signed-in customer's orders by ID."""
    o = _order(order_id)
    o.pop("email")
    return json.dumps(o)

@mcp.tool()
def list_orders() -> str:
    """List the signed-in customer's orders."""
    with sqlite3.connect(f"file:{DB}?mode=ro", uri=True) as con:
        rows = con.execute("SELECT order_id, status, total, items FROM orders WHERE lower(email)=?",
                           (_customer(),)).fetchall()
    return json.dumps([dict(zip(["order_id", "status", "total", "items"], r)) for r in rows])

@mcp.tool()
def create_return(order_id: str, reason: str) -> str:
    """Start a return and refund. Only for delivered orders within 30 days. A human
    approves every return before it is created."""
    o = _order(order_id)
    if o["status"] != "delivered":
        raise ToolError(f"Order {order_id} is {o['status']}, not delivered; it can't be returned yet.")
    age = (TODAY - date.fromisoformat(o["delivered"])).days
    if age > RETURN_DAYS:
        raise ToolError(f"Order {order_id} was delivered {age} days ago; the return window is "
                        f"{RETURN_DAYS} days. Offer a handoff to a human instead.")
    with sqlite3.connect(DB) as con:
        if con.execute("SELECT 1 FROM returns WHERE order_id=?", (o["order_id"],)).fetchone():
            return f"A return for {o['order_id']} already exists."          # idempotent
        con.execute("INSERT INTO returns VALUES (?,?,?,?)",
                    (o["order_id"], o["items"], o["total"], TODAY.isoformat()))
    return f"Return created for {o['order_id']} ({o['items']}), refund ${o['total']:.2f}."

if __name__ == "__main__":
    mcp.run(transport="stdio")
