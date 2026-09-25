"""Exercise 12.7 (Complex) reference solution: the weather server over stdio AND
Streamable HTTP, same results, no real network (httpx is faked in the server)."""
import asyncio
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
import pytest
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

FAKE = str(Path(__file__).parent / "fake_http")

def _env():
    return {**os.environ, "WEATHER_FAKE": "1",
            "PYTHONPATH": FAKE + os.pathsep + os.environ.get("PYTHONPATH", "")}

def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]

@pytest.fixture(scope="module")
def http_url(tmp_path_factory):
    port = _free_port()
    # a tiny launcher so the test can choose the port
    launcher = tmp_path_factory.mktemp("srv") / "run_http.py"
    launcher.write_text("import sys, ch12_weather_server as s\n"
                        f"s.mcp.run(transport='streamable-http', host='127.0.0.1', port={port})\n")
    proc = subprocess.Popen([sys.executable, str(launcher)], env=_env(), cwd=os.getcwd(),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.5).close(); break
        except OSError:
            time.sleep(0.2)
    yield f"http://127.0.0.1:{port}/mcp"
    proc.terminate(); proc.wait(timeout=10)

async def _exercise(transport):
    async with Client(transport) as c:
        names = sorted(t.name for t in (await c.list_tools()).tools)
        ok = await c.call_tool("geocode", {"city": "Pune"})
        bad = await c.call_tool("geocode", {"city": "Xyzzyqq"})
        fc = await c.call_tool("get_forecast", {"latitude": 18.5, "longitude": 73.9, "days": 1})
        return names, ok.is_error, ok.content[0].text, bad.is_error, bad.content[0].text, fc.content[0].text

def _stdio():
    return stdio_client(StdioServerParameters(command=sys.executable,
                                              args=["ch12_weather_server.py"], env=_env()))

def test_stdio_and_http_agree(http_url):
    s = asyncio.run(_exercise(_stdio()))
    h = asyncio.run(_exercise(streamable_http_client(http_url)))
    assert s == h
    names, ok_err, ok_text, bad_err, bad_text, forecast = h
    assert names == ["geocode", "get_forecast"]
    assert not ok_err and "Pune" in ok_text
    assert bad_err and "no place called" in bad_text
    assert "rain chance 70%" in forecast
