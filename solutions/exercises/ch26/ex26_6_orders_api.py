"""Exercise 26.6 (solution): the order tools as an HTTP API that checks bearer tokens.
The harness holds the token, renews it when it expires, and the model never sees it."""
import time

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

import ch26_identity as ident

def _token(request) -> str:
    return request.headers.get("authorization", "").removeprefix("Bearer ").strip()

async def order(request):
    try:
        return JSONResponse({"result": ident.get_order(_token(request),
                                                       request.path_params["oid"])})
    except ident.Denied as exc:
        return JSONResponse({"error": str(exc)}, status_code=403)

app = Starlette(routes=[Route("/orders/{oid}", order)])

class Harness:
    """Holds and renews the token. run_tool is what the agent calls."""
    def __init__(self, agent="support-agent", user="ana", ttl=900, audience=ident.API):
        self.agent, self.user, self.ttl, self.audience = agent, user, ttl, audience
        self.client = TestClient(app)
        self.renewals = 0
        self._mint()

    def _mint(self):
        self.token = ident.mint(self.agent, self.user, {"orders:read"}, self.audience,
                                ttl=self.ttl)
        self.expires = time.time() + self.ttl

    def run_tool(self, name, args):
        if time.time() >= self.expires - 1:                  # renew before it lapses
            self._mint()
            self.renewals += 1
        r = self.client.get(f"/orders/{args['order_id']}",
                            headers={"Authorization": f"Bearer {self.token}"})
        body = r.json()
        return body.get("result") or f"ERROR: {body.get('error')}"

TOOLS = [t for t in ident.TOOLS if t["name"] == "get_order"]

if __name__ == "__main__":
    from ch04_agent import run_agent
    h = Harness()
    print(run_agent("What did I pay for A-1001?", TOOLS, h.run_tool)[0])
