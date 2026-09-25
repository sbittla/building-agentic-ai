"""Exercise 13.8: elicitation and sampling, in memory, with scripted answers (no API key)."""
import asyncio
import importlib
import sys
from pathlib import Path
import pytest
from mcp import Client

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "exercises"))
server = importlib.import_module("ex13_8_trip_server")
host = importlib.import_module("ex13_8_host")

def scripted(*answers):
    it = iter(answers)
    return lambda prompt="": next(it)

async def call(tool, args, answers, generate=None):
    async def fake_generate(system, messages, max_tokens):
        assert "Summarize" in messages[0]["content"] and max_tokens <= 1000
        return "- Go early\n- Eat pastries\n- Plan a day for Sintra"
    async with Client(server.mcp,
                      elicitation_callback=host.make_elicitation_callback(ask=scripted(*answers)),
                      sampling_callback=host.make_sampling_callback(generate or fake_generate,
                                                                    ask=scripted(*answers))) as c:
        r = await c.call_tool(tool, args)
        return r.content[0].text, r.is_error

def test_elicitation_accept():
    text, err = asyncio.run(call("book_trip", {"city": "Lisbon"}, ["y", "3", "900"]))
    assert not err and "3 night(s) in Lisbon" in text and "$900" in text

def test_elicitation_decline():
    text, err = asyncio.run(call("book_trip", {"city": "Lisbon"}, ["n"]))
    assert "declined" in text and "nothing was booked" in text

def test_sampling_uses_the_hosts_model():
    text, err = asyncio.run(call("summarize_notes", {"notes": "Tram 28..."}, ["y"]))
    assert not err and "Sintra" in text

def test_sampling_refused_by_user():
    with pytest.raises(Exception) as info:
        asyncio.run(call("summarize_notes", {"notes": "Tram 28..."}, ["n"]))
    def messages(exc):
        yield str(exc)
        for sub in getattr(exc, "exceptions", ()):
            yield from messages(sub)
    assert any("refused" in m for m in messages(info.value))

def test_elicitation_over_stdio():
    """The same flow through a real subprocess, as the Chapter 13 hub connects."""
    from mcp import StdioServerParameters
    from mcp.client.stdio import stdio_client
    params = StdioServerParameters(command=sys.executable, args=[server.__file__])
    async def go():
        async with Client(stdio_client(params),
                          elicitation_callback=host.make_elicitation_callback(ask=scripted("y", "2", "400"))) as c:
            r = await c.call_tool("book_trip", {"city": "Porto"})
            return r.content[0].text
    assert "2 night(s) in Porto" in asyncio.run(go())
