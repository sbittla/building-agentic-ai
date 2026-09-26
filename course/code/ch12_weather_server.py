"""Chapter 12: the chapter 7 weather tools, packaged as an MCP server."""
import logging
import os
import sys
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
import ch07_weather_tools as weather

# stdio servers talk JSON-RPC over stdout, so logs MUST go to stderr.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("weather-server")

mcp = MCPServer("weather", instructions="Weather forecasts for packing advice.")

@mcp.tool()
def geocode(city: str) -> str:
    """Find latitude/longitude for a city. Returns up to 5 candidates as JSON.
    If more than one plausible match exists, ask the user which one they mean."""
    log.info("geocode %s", city)
    try:
        result = weather.geocode(city)
    except Exception as exc:              # network failure after retries
        raise ToolError(str(exc)) from exc
    if result.startswith("ERROR"):
        raise ToolError(result)           # the client sees is_error=True + this text
    return result

@mcp.tool()
def get_forecast(latitude: float, longitude: float, days: int = 3) -> str:
    """Daily forecast (min/max temperature in Celsius, rain chance)
    for up to 16 days."""
    log.info("forecast %s,%s days=%s", latitude, longitude, days)
    try:
        return weather.get_forecast(latitude, longitude, days)
    except Exception as exc:
        raise ToolError(str(exc)) from exc

@mcp.resource("weather://favorites")
def favorite_cities() -> str:
    """Cities the user travels to most often."""
    return "Seattle, WA\nPune, India\nBerlin, Germany"

@mcp.prompt()
def packing_advice(city: str, days: int = 3) -> str:
    """A ready-made prompt for a packing list."""
    return (f"Get the {days}-day forecast for {city} with the weather tools, then "
            "give me a short packing list grouped by clothing, rain gear and extras.")

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    if transport == "streamable-http":
        # In Docker, MCP_HOST=0.0.0.0 lets your computer reach port 8000. Listening on
        # all interfaces switches off the SDK's automatic DNS-rebinding protection, so
        # we turn it back on and list the host names this server may be called by.
        from mcp.server.transport_security import TransportSecuritySettings
        mcp.run(transport="streamable-http",
                host=os.environ.get("MCP_HOST", "127.0.0.1"),
                transport_security=TransportSecuritySettings(
                    allowed_hosts=["127.0.0.1:*", "localhost:*"],
                    allowed_origins=["http://localhost:*", "http://127.0.0.1:*"]))
    else:
        mcp.run(transport="stdio")
