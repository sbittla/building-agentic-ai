"""
course.code: Python modules for "Building Agentic AI Systems"

This package makes code modules from all chapters available for import.
Exercises can use: import ch03_tools, from ch03_tools import TOOLS, etc.
"""
import sys
from pathlib import Path

# Add all chapter directories to sys.path so modules can be found directly
_code_dir = Path(__file__).parent
for chapter_dir in sorted(_code_dir.glob("ch??")):
    if chapter_dir.is_dir() and (chapter_dir / "__init__.py").exists():
        sys.path.insert(0, str(chapter_dir))

# Also add interlude directories
for interlude_dir in sorted(_code_dir.glob("interlude_*")):
    if interlude_dir.is_dir() and (interlude_dir / "__init__.py").exists():
        sys.path.insert(0, str(interlude_dir))

__all__ = []
