"""Exercise 15.3: talk to an MCP server by hand, one HTTP request at a time.

Start the server in one terminal:   ./course.sh serve ch15_modern.py
Then run this in another:           ./course.sh run exercises/ex15_3_wire.py
"""
import json
import logging
import sys
import httpx
from ch15_modern import ENVELOPE, post

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/mcp"

def mismatched(url: str) -> dict:
    """The header says one tool, the body another: a gateway routing on the header
    would send the call to the wrong place, so the server refuses it."""
    body = {"jsonrpc": "2.0", "id": 9, "method": "tools/call",
            "params": {"name": "get_price", "arguments": {"product_id": "P-1"},
                       "_meta": ENVELOPE}}
    headers = {"Accept": "application/json, text/event-stream",
               "MCP-Protocol-Version": "2026-07-28",
               "Mcp-Method": "tools/call", "Mcp-Name": "find_products"}
    return httpx.post(url, json=body, headers=headers, timeout=30).json()

def main(url: str = URL) -> dict:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    found = {
        "discover": post(url, "server/discover")["result"],
        "tools": post(url, "tools/list")["result"],
        "call": post(url, "tools/call", {"name": "get_price",
                                         "arguments": {"product_id": "P-2"}})["result"],
        "mismatch": mismatched(url)["error"],
    }
    d = found["discover"]
    print("versions:  ", d["supportedVersions"])
    print("capability:", sorted(d["capabilities"]))
    print("tools:     ", [t["name"] for t in found["tools"]["tools"]],
          f"(fresh for {found['tools']['ttlMs'] / 1000:.0f} s, "
          f"{found['tools']['cacheScope']})")
    print("get_price: ", found["call"]["structuredContent"])
    print("mismatch:  ", json.dumps(found["mismatch"]))
    return found

if __name__ == "__main__":
    main()
