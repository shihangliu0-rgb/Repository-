"""Shared fixtures: build throw-away git repositories on the fly."""

from __future__ import annotations

import os
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

ENV = {
    **os.environ,
    "GIT_AUTHOR_DATE": "",
    "GIT_COMMITTER_DATE": "",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
}


def git(repo, *args, author=None, when=None):
    env = dict(ENV)
    if when:
        env["GIT_AUTHOR_DATE"] = f"{when} +0000"
        env["GIT_COMMITTER_DATE"] = f"{when} +0000"
    if author:
        env["GIT_AUTHOR_NAME"] = author
        env["GIT_AUTHOR_EMAIL"] = f"{author.lower().replace(' ', '.')}@example.com"
        env["GIT_COMMITTER_NAME"] = env["GIT_AUTHOR_NAME"]
        env["GIT_COMMITTER_EMAIL"] = env["GIT_AUTHOR_EMAIL"]
    else:
        env.setdefault("GIT_AUTHOR_NAME", "Test User")
        env.setdefault("GIT_AUTHOR_EMAIL", "test@example.com")
        env.setdefault("GIT_COMMITTER_NAME", "Test User")
        env.setdefault("GIT_COMMITTER_EMAIL", "test@example.com")
    proc = subprocess.run(["git", "-C", str(repo), *args], env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert proc.returncode == 0, proc.stdout
    return proc.stdout


def write(repo, rel, content):
    path = os.path.join(str(repo), rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


def commit(repo, message, author="Test User", when=None):
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message, author=author, when=when)


def complex_module(branches: int, comment: bool = True) -> str:
    lines = ['"""Module docstring."""' if comment else "x = 1", "import os", ""]
    lines.append("def handler(value, flag, mode):")
    for i in range(branches):
        lines.append(f"    if value == {i} and flag:")
        lines.append(f"        for item in range({i + 1}):")
        lines.append(f"            while item > 0 or mode == 'x':")
        lines.append(f"                item -= 1")
    lines.append("    return value")
    return "\n".join(lines) + "\n"


@pytest.fixture
def sample_repo(tmp_path):
    """A repository with a clear hotspot, a stable file and two authors."""
    repo = tmp_path / "sample"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")

    base = int(time.time()) - 200 * 86400
    write(repo, "README.md", "# Sample\n\nA test repository.\n")
    write(repo, "src/stable.py", '"""Rarely touched."""\n\n\ndef ping():\n    return "pong"\n')
    write(repo, "src/hot.py", complex_module(6))
    write(repo, "tests/test_hot.py", "from src.hot import handler\n\n\ndef test_handler():\n    assert handler(1, True, 'x') == 1\n")
    commit(repo, "initial", author="Alice", when=base)

    # hot.py keeps changing, always by Alice -> hotspot + knowledge risk
    for i in range(1, 9):
        write(repo, "src/hot.py", complex_module(6 + i))
        write(repo, "src/config.py", f"SETTING = {i}\n# TODO: move this into the environment\n")
        commit(repo, f"tweak hot path {i}", author="Alice", when=base + i * 3 * 86400)

    write(repo, "src/other.py", "def helper():\n    # FIXME: handle the empty case\n    return []\n")
    commit(repo, "add helper", author="Bob", when=base + 40 * 86400)
    return str(repo)


@pytest.fixture
def tiny_repo(tmp_path):
    repo = tmp_path / "tiny"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    write(repo, "README.md", "# tiny\n")
    commit(repo, "initial")
    return str(repo)
