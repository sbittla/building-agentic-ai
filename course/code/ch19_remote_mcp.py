"""Chapter 19: a REMOTE MCP server over Streamable HTTP, as an OAuth-style resource server.
Run:  ./course.sh serve-mcp   (serves http://localhost:8000/mcp)

The MCP SDK does the protocol parts for us:
- every request needs `Authorization: Bearer <token>`, else 401 with a pointer to
- /.well-known/oauth-protected-resource/mcp (RFC 9728), which tells clients which
  authorization server issues tokens for this server and which scopes exist;
- tokens must have been issued FOR this server (the resource / audience check);
- requests with an unexpected Host header are refused (DNS-rebinding protection).
Here the tokens are static values from your .env; in production, verify_token would
check a JWT signed by your identity provider (or call its introspection endpoint)."""
import hmac
import os
import time
import uvicorn
from mcp.server import MCPServer
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
import ch05_todo_tools as todo

PUBLIC_URL = os.environ.get("MCP_PUBLIC_URL", "http://localhost:8000/mcp")
ISSUER = os.environ.get("MCP_ISSUER_URL", "https://auth.example.com")   # your identity provider

class StaticTokenVerifier:
    """Maps tokens to scopes. MCP_TOKEN may read and write; MCP_READONLY_TOKEN may only read."""
    def __init__(self, tokens: dict[str, list[str]]):
        self.tokens = {t: scopes for t, scopes in tokens.items() if t}

    async def verify_token(self, token: str) -> AccessToken | None:
        for known, scopes in self.tokens.items():
            if hmac.compare_digest(token.encode(), known.encode()):
                return AccessToken(token=token, client_id="course-client", scopes=scopes,
                                   resource=PUBLIC_URL, expires_at=int(time.time()) + 3600)
        return None

def require(scope: str):
    """Least privilege per TOOL, not just per server: check the caller's scopes."""
    token = get_access_token()
    if token is None or scope not in token.scopes:
        raise ToolError(f"This token lacks the '{scope}' scope.")

def build_server(tokens: dict[str, list[str]]) -> MCPServer:
    mcp = MCPServer("remote-todo", instructions="A shared team to-do list.",
                    token_verifier=StaticTokenVerifier(tokens),
                    auth=AuthSettings(issuer_url=ISSUER, resource_server_url=PUBLIC_URL,
                                      required_scopes=["todo:read"],
                                      validate_token_resource=True))

    @mcp.tool()
    def add_task(title: str, due: str | None = None) -> str:
        """Add a team to-do. due is YYYY-MM-DD. Needs the todo:write scope."""
        require("todo:write")
        return todo.add_task(title, due)

    @mcp.tool()
    def list_tasks() -> str:
        """List the team's open tasks."""
        return todo.list_tasks()
    return mcp

def build_app(token: str | None = None, host: str = "127.0.0.1", readonly_token: str | None = None):
    token = token or os.environ.get("MCP_TOKEN", "")
    readonly_token = readonly_token or os.environ.get("MCP_READONLY_TOKEN", "")
    if not token:
        raise RuntimeError("MCP_TOKEN is not set. Add a long random token to your .env.")
    mcp = build_server({token: ["todo:read", "todo:write"], readonly_token: ["todo:read"]})
    allowed = ["127.0.0.1:*", "localhost:*", "agentic-ai-mcp:*", "testserver"]
    return mcp.streamable_http_app(host=host, transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True, allowed_hosts=allowed,
        allowed_origins=["http://localhost:*", "http://127.0.0.1:*"]))

if __name__ == "__main__":
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    uvicorn.run(build_app(host=host), host=host, port=int(os.environ.get("MCP_PORT", "8000")))
