import os

from repolens import scan


def test_detect_language():
    assert scan.detect_language("a/b/c.py")[0] == "Python"
    assert scan.detect_language("Makefile")[0] == "Make"
    assert scan.detect_language("x.unknownext")[0] == "Other"
    assert scan.detect_language("app/main.TS")[0] == "TypeScript"


def test_scan_counts_python(tmp_path):
    src = tmp_path / "mod.py"
    src.write_text(
        "# a comment\n"
        "\n"
        "def f(x):\n"
        "    if x > 1 and x < 10:\n"
        "        return [i for i in range(x) if i % 2]\n"
        "    return None  # trailing\n",
        encoding="utf-8",
    )
    result = scan.scan_file(str(tmp_path), "mod.py")
    assert result.language == "Python"
    assert result.blank == 1
    assert result.comment == 1
    assert result.loc == 4
    assert result.complexity >= 2


def test_scan_block_comments(tmp_path):
    (tmp_path / "a.js").write_text(
        "/*\n * header\n */\nfunction f() {\n  return 1;\n}\n", encoding="utf-8")
    result = scan.scan_file(str(tmp_path), "a.js")
    assert result.comment == 3
    assert result.loc == 3


def test_scan_todos(tmp_path):
    (tmp_path / "b.py").write_text(
        "# TODO: rewrite this\n"
        "def g():\n"
        "    pass  # FIXME broken on windows\n",
        encoding="utf-8")
    result = scan.scan_file(str(tmp_path), "b.py")
    tags = {t[1] for t in result.todos}
    assert tags == {"TODO", "FIXME"}
    assert result.todos[0][2].startswith("rewrite")


def test_scan_indentation_depth(tmp_path):
    (tmp_path / "deep.py").write_text(
        "def f():\n    if a:\n        if b:\n            if c:\n                return 1\n",
        encoding="utf-8")
    result = scan.scan_file(str(tmp_path), "deep.py")
    assert result.max_indent >= 4


def test_scan_skips_binary_and_large(tmp_path):
    (tmp_path / "img.png").write_bytes(b"\x89PNG" + bytes(200))
    assert scan.scan_file(str(tmp_path), "img.png") is None
    (tmp_path / "big.py").write_text("x = 1\n" * 10, encoding="utf-8")
    assert scan.scan_file(str(tmp_path), "big.py", max_bytes=5) is None


def test_scan_handles_invalid_utf8(tmp_path):
    (tmp_path / "weird.py").write_bytes(b"\xff\xfe\x00bad bytes")
    assert scan.scan_file(str(tmp_path), "weird.py") is None


def test_is_excluded():
    assert scan.is_excluded("node_modules/lib/a.js", scan.DEFAULT_EXCLUDES)
    assert scan.is_excluded("frontend/node_modules/a.js", scan.DEFAULT_EXCLUDES)
    assert not scan.is_excluded("src/app.js", scan.DEFAULT_EXCLUDES)


def test_looks_generated():
    assert scan.looks_generated("package-lock.json")
    assert scan.looks_generated("static/app.min.js")
    assert not scan.looks_generated("src/app.js")


def test_scan_paths_filters(tmp_path):
    os.makedirs(tmp_path / "node_modules", exist_ok=True)
    (tmp_path / "node_modules" / "dep.js").write_text("var a = 1;\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("print(1)\n", encoding="utf-8")
    (tmp_path / "yarn.lock").write_text("stuff\n", encoding="utf-8")
    results = scan.scan_paths(str(tmp_path), ["node_modules/dep.js", "app.py", "yarn.lock"])
    assert set(results) == {"app.py"}
    with_generated = scan.scan_paths(str(tmp_path), ["yarn.lock"], skip_generated=False)
    assert "yarn.lock" in with_generated


def test_python_docstrings_count_as_comments(tmp_path):
    (tmp_path / "doc.py").write_text(
        '"""Module docstring.\n\nSpanning several lines.\n"""\n'
        "\n"
        "def f():\n"
        '    """One-line docstring."""\n'
        "    return 1\n",
        encoding="utf-8")
    result = scan.scan_file(str(tmp_path), "doc.py")
    assert result.comment == 4  # blank lines inside a docstring stay "blank"
    assert result.loc == 2


def test_multiline_string_assignment_does_not_swallow_code(tmp_path):
    """A `X = """ + '"""' + """...""" + '"""' + """` block must not hide the rest of the file."""
    (tmp_path / "cli.py").write_text(
        'HELP = """\n'
        "usage: thing\n"
        '"""\n'
        "\n"
        "def main():\n"
        "    if HELP:\n"
        "        return 1\n"
        "    return 0\n",
        encoding="utf-8")
    result = scan.scan_file(str(tmp_path), "cli.py")
    assert result.loc == 5, result.loc
    assert result.complexity >= 1
