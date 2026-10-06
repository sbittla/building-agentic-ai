"""Print selected parts of a Python file, for build.js's `@@code file.py::a,b,Class.method`.

Each name is a top-level function, class or assignment, or Class.method. The parts are
printed in the order given, separated by a line with "...", exactly as the book shows them.
Decorators are included; a method is shown dedented, and a comment block just above a part is included.
"""
import ast
import re
import textwrap
import sys


def segment(lines, node, dedent=False):
    start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    # the comment just above it belongs to it; a long "# ------" section divider doesn't
    while (start > 1 and lines[start - 2].lstrip().startswith("#")
           and not re.match(r"#\s*-{10,}", lines[start - 2].lstrip())):
        start -= 1
    text = "\n".join(lines[start - 1:node.end_lineno]).rstrip()
    return textwrap.dedent(text) if dedent else text


def find(tree, lines, name):
    if "." in name:
        cls, meth = name.split(".", 1)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == cls:
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name == meth:
                        return segment(lines, sub, dedent=True)
        raise SystemExit(f"excerpt: {name} not found")
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
            return segment(lines, node)
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return segment(lines, node)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return segment(lines, node)
    raise SystemExit(f"excerpt: {name} not found")


def main():
    path, names = sys.argv[1], sys.argv[2]
    source = open(path, encoding="utf8").read()
    lines = source.splitlines()
    tree = ast.parse(source)
    parts = [find(tree, lines, n.strip()) for n in names.split(",") if n.strip()]
    print("\n\n...\n\n".join(parts))


if __name__ == "__main__":
    main()
