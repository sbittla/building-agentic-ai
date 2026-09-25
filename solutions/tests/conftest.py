"""Builds a throwaway workspace (original course code + sample data), puts the
solutions on the path, and replaces the Anthropic client with the scripted stand-in.
Runs before any course module is imported, because several modules read paths
(notes/, messy/, shop.db) at import time."""
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SOLUTIONS = HERE.parent
CODE = Path(os.environ.get("COURSE_CODE", "/opt/course/code"))
DATA = Path(os.environ.get("COURSE_DATA", "/opt/course/data"))

WS = Path(tempfile.mkdtemp(prefix="solutions-ws-"))
shutil.copytree(CODE, WS, dirs_exist_ok=True)
os.chdir(WS)
sys.path[:0] = [str(HERE), str(SOLUTIONS / "exercises"), str(WS), str(DATA)]
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-offline")
os.environ["PYTHONPATH"] = os.pathsep.join([str(SOLUTIONS / "exercises"), str(WS),
                                            os.environ.get("PYTHONPATH", "")])

import generate  # noqa: E402
generate.all_data(WS)
import subprocess  # noqa: E402
subprocess.run(["git", "init", "-q"], cwd=WS)

import anthropic  # noqa: E402
from fakemodel import MODEL, AsyncFacade  # noqa: E402

anthropic.Anthropic = lambda *a, **k: MODEL
anthropic.AsyncAnthropic = lambda *a, **k: AsyncFacade(MODEL)

@pytest.fixture
def model():
    MODEL.reset()
    return MODEL

@pytest.fixture
def ws():
    os.chdir(WS)
    return WS

def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(WS, ignore_errors=True)

@pytest.fixture(autouse=True)
def _restore_module_state():
    """Some course modules keep paths in globals (chapter 11 points the chapter 6
    tools at library/, exercise 10.7 points the fixer at other repos). Put them back."""
    import ch06_notes_tools, ch10_fixer
    saved = (ch06_notes_tools.ROOT, ch10_fixer.REPO)
    os.chdir(WS)
    yield
    ch06_notes_tools.ROOT, ch10_fixer.REPO = saved
    os.chdir(WS)
