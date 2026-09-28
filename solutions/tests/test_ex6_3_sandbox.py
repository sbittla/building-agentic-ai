"""Exercise 6.3 (Simple) reference solution: prove the notes sandbox holds."""
import os
import pytest
import ch06_notes_tools as notes

@pytest.mark.parametrize("path", ["../shop.db", "/etc/passwd", "work/../../ch04_agent.py"])
def test_escaping_paths_are_refused(path):
    assert notes.run_tool("read_file", {"path": path}).startswith("ERROR")

def test_symlink_out_of_sandbox_is_refused(tmp_path):
    link = notes.ROOT / "sneaky_link.md"
    link.unlink(missing_ok=True)
    os.symlink("/etc/hostname", link)
    try:
        assert notes.run_tool("read_file", {"path": "sneaky_link.md"}).startswith("ERROR")
    finally:
        link.unlink()

def test_normal_read_still_works():
    assert notes.run_tool("read_file", {"path": "learning/kafka-basics.md"}).startswith("1: # Kafka")
