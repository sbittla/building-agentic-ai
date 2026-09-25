"""Capstone 2: turn a query result into a PNG chart."""
import logging, sqlite3, sys
from pathlib import Path
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
mcp = MCPServer("charts")

@mcp.tool()
def make_chart(sql: str, chart_type: str = "bar", title: str = "") -> str:
    """Run a read-only query returning (label, value) rows and save a chart.
    chart_type: bar or line. Returns the PNG path."""
    if chart_type not in ("bar", "line"):
        raise ToolError("chart_type must be bar or line")
    try:
        with sqlite3.connect("file:shop.db?mode=ro", uri=True) as con:
            rows = con.execute(sql).fetchmany(50)
    except sqlite3.Error as e:
        raise ToolError(str(e))
    if not rows or len(rows[0]) != 2:
        raise ToolError("The query must return exactly two columns: label, value.")
    labels, values = [str(r[0]) for r in rows], [float(r[1]) for r in rows]
    Path("charts").mkdir(exist_ok=True)
    path = Path("charts") / (("".join(c if c.isalnum() else "_" for c in title)[:40] or "chart") + ".png")
    plt.figure(figsize=(7, 4))
    (plt.bar if chart_type == "bar" else plt.plot)(labels, values)
    plt.title(title); plt.xticks(rotation=30, ha="right"); plt.tight_layout(); plt.savefig(path); plt.close()
    return str(path)

if __name__ == "__main__":
    mcp.run(transport="stdio")
