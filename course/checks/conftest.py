"""Loads YOUR exercise file (EXERCISE_FILE) as the fixture `ex`."""
import importlib.util
import os
import sys
from pathlib import Path
import pytest

@pytest.fixture(scope="module")
def ex():
    path = Path(os.environ["EXERCISE_FILE"])
    sys.path[:0] = [str(path.parent)]
    spec = importlib.util.spec_from_file_location(path.stem + "_checked", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
