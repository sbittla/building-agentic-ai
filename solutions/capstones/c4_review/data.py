"""Capstone 4 data: a small repo with three 'pull requests' as branches.
pr-1 adds a bug (a test fails), pr-2 is a clean change, pr-3 deletes a test."""
import subprocess
from pathlib import Path

REPO = Path("review_repo")
ENV = {"PATH": "/usr/bin:/bin", "HOME": "/tmp", "GIT_AUTHOR_NAME": "dev", "GIT_AUTHOR_EMAIL": "d@x",
       "GIT_COMMITTER_NAME": "dev", "GIT_COMMITTER_EMAIL": "d@x"}

def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, env=ENV, capture_output=True, text=True, check=True).stdout

def build():
    if (REPO / ".git").exists():
        return REPO
    REPO.mkdir(exist_ok=True)
    git("init", "-q", "-b", "main")
    (REPO / "cart.py").write_text(
        "def total(items):\n    return sum(price * qty for price, qty in items)\n\n"
        "def last_items(items, n):\n    return items[-n:]\n")
    (REPO / "test_cart.py").write_text(
        "from cart import total, last_items\n\ndef test_total():\n    assert total([(2.0, 3)]) == 6.0\n\n"
        "def test_last_items():\n    assert last_items([1, 2, 3], 2) == [2, 3]\n")
    git("add", "-A"); git("commit", "-qm", "cart: initial")
    git("checkout", "-qb", "pr-1")
    (REPO / "cart.py").write_text((REPO / "cart.py").read_text().replace("items[-n:]", "items[-n - 1:]"))
    git("commit", "-qam", "cart: include one more item in last_items"); git("checkout", "-q", "main")
    git("checkout", "-qb", "pr-2")
    (REPO / "cart.py").write_text((REPO / "cart.py").read_text() + "\n\ndef count(items):\n    return len(items)\n")
    git("commit", "-qam", "cart: add count()"); git("checkout", "-q", "main")
    git("checkout", "-qb", "pr-3")
    (REPO / "test_cart.py").write_text("from cart import total\n\ndef test_total():\n    assert total([(2.0, 3)]) == 6.0\n")
    git("commit", "-qam", "tests: remove flaky test"); git("checkout", "-q", "main")
    return REPO

if __name__ == "__main__":
    print("built", build())
