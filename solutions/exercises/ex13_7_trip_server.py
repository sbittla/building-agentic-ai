"""Exercise 13.7 (server side): a tool that ASKS THE USER mid-call (elicitation).

The MCP 2026-07-28 specification made the protocol stateless: instead of the server sending
a request back to the client in the middle of a call, the tool returns "input required",
and the client retries the call with the user's answers (multi round-trip requests).
The SDK hides the difference: declare what you need with a *resolver* and it asks in
whichever way the connected client understands (old clients get the classic request).

The second tool uses SAMPLING (the server borrows the host's model). The 2026-07-28
specification deprecates sampling, so it's here to recognize in older servers, not to copy.

Run it as a stdio server:  python ex13_7_trip_server.py   (ex13_7_host.py is the host)"""
import logging
import sys
import warnings
from typing import Annotated
from pydantic import BaseModel, Field
from mcp.server import MCPServer
from mcp.server.elicitation import ElicitationResult
from mcp.server.mcpserver import Elicit, Resolve, Sample
from mcp.types import CreateMessageResult, SamplingMessage, TextContent

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
mcp = MCPServer("trips", instructions="Books trips and summarizes travel notes.")

class TripDetails(BaseModel):
    """What the server asks the user for. Elicitation schemas must be flat: simple types only."""
    nights: int = Field(ge=1, le=30, description="How many nights?")
    budget_usd: int = Field(ge=50, description="Total budget in US dollars")

def ask_details(city: str):
    """Resolver: runs before the tool body. Returning Elicit(...) means 'ask the user'."""
    return Elicit(f"Booking a trip to {city}. How many nights, and what budget?", TripDetails)

@mcp.tool()
async def book_trip(city: str,
                    details: Annotated[ElicitationResult[TripDetails], Resolve(ask_details)]) -> str:
    """Book a trip to a city. The server asks the user for nights and budget itself;
    don't guess them."""
    if details.action == "accept":
        d = details.data
        return f"Booked {d.nights} night(s) in {city} within ${d.budget_usd}. (Demo: nothing was charged.)"
    if details.action == "decline":
        return f"The user declined to give details, so nothing was booked for {city}."
    return "The user cancelled the booking."

def summarize_request(notes: str):
    """Resolver: Sample(...) asks the HOST's model. Deprecated in the 2026-07-28 spec."""
    return Sample([SamplingMessage(role="user", content=TextContent(
        type="text", text=f"Summarize these travel notes in three short bullets:\n\n{notes}"))],
        max_tokens=300, system_prompt="You write short, factual travel summaries.")

@mcp.tool()
async def summarize_notes(notes: str,
                          summary: Annotated[CreateMessageResult, Resolve(summarize_request)]) -> str:
    """Summarize travel notes in three bullet points, using the host's model (sampling)."""
    content = summary.content
    return content.text if isinstance(content, TextContent) else str(content)

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message=".*deprecated as of 2026-07-28.*")
    mcp.run()                      # stdio
