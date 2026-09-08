"""Static, language-aware scanning of files that exist in the working tree.

Deliberately heuristic: RepoLens must work on any repository without parsers
for 20 languages, so complexity is estimated from branch keywords plus
indentation depth. That is enough to rank files against each other.
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Optional, Tuple

from .model import FileScan

# extension -> (language, line-comment prefixes, (block start, block end) or None)
LANGUAGES: Dict[str, Tuple[str, Tuple[str, ...], Optional[Tuple[str, str]]]] = {
    ".py": ("Python", ("#",), None),
    ".pyi": ("Python", ("#",), None),
    ".js": ("JavaScript", ("//",), ("/*", "*/")),
    ".mjs": ("JavaScript", ("//",), ("/*", "*/")),
    ".cjs": ("JavaScript", ("//",), ("/*", "*/")),
    ".jsx": ("JavaScript", ("//",), ("/*", "*/")),
    ".ts": ("TypeScript", ("//",), ("/*", "*/")),
    ".tsx": ("TypeScript", ("//",), ("/*", "*/")),
    ".go": ("Go", ("//",), ("/*", "*/")),
    ".rs": ("Rust", ("//",), ("/*", "*/")),
    ".java": ("Java", ("//",), ("/*", "*/")),
    ".kt": ("Kotlin", ("//",), ("/*", "*/")),
    ".swift": ("Swift", ("//",), ("/*", "*/")),
    ".c": ("C", ("//",), ("/*", "*/")),
    ".h": ("C", ("//",), ("/*", "*/")),
    ".cc": ("C++", ("//",), ("/*", "*/")),
    ".cpp": ("C++", ("//",), ("/*", "*/")),
    ".hpp": ("C++", ("//",), ("/*", "*/")),
    ".cs": ("C#", ("//",), ("/*", "*/")),
    ".rb": ("Ruby", ("#",), None),
    ".php": ("PHP", ("//", "#"), ("/*", "*/")),
    ".scala": ("Scala", ("//",), ("/*", "*/")),
    ".sh": ("Shell", ("#",), None),
    ".bash": ("Shell", ("#",), None),
    ".zsh": ("Shell", ("#",), None),
    ".sql": ("SQL", ("--",), ("/*", "*/")),
    ".r": ("R", ("#",), None),
    ".lua": ("Lua", ("--",), None),
    ".dart": ("Dart", ("//",), ("/*", "*/")),
    ".vue": ("Vue", ("//",), ("<!--", "-->")),
    ".svelte": ("Svelte", ("//",), ("<!--", "-->")),
    ".html": ("HTML", (), ("<!--", "-->")),
    ".css": ("CSS", (), ("/*", "*/")),
    ".scss": ("CSS", ("//",), ("/*", "*/")),
    ".less": ("CSS", ("//",), ("/*", "*/")),
    ".yml": ("YAML", ("#",), None),
    ".yaml": ("YAML", ("#",), None),
    ".toml": ("TOML", ("#",), None),
    ".ini": ("INI", (";", "#"), None),
    ".json": ("JSON", (), None),
    ".md": ("Markdown", (), None),
    ".rst": ("reStructuredText", (), None),
    ".tf": ("Terraform", ("#",), None),
    ".proto": ("Protobuf", ("//",), ("/*", "*/")),
    ".gradle": ("Gradle", ("//",), ("/*", "*/")),
    ".ex": ("Elixir", ("#",), None),
    ".exs": ("Elixir", ("#",), None),
    ".erl": ("Erlang", ("%",), None),
    ".clj": ("Clojure", (";",), None),
    ".hs": ("Haskell", ("--",), None),
    ".pl": ("Perl", ("#",), None),
    ".m": ("Objective-C", ("//",), ("/*", "*/")),
}

FILENAME_LANGUAGES = {
    "Dockerfile": ("Docker", ("#",), None),
    "Makefile": ("Make", ("#",), None),
    "Jenkinsfile": ("Groovy", ("//",), ("/*", "*/")),
    ".gitignore": ("Config", ("#",), None),
}

# Languages we treat as "code" for hotspot ranking.
CODE_LANGUAGES = {
    "Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "Kotlin", "Swift",
    "C", "C++", "C#", "Ruby", "PHP", "Scala", "Shell", "SQL", "R", "Lua", "Dart",
    "Vue", "Svelte", "Elixir", "Erlang", "Clojure", "Haskell", "Perl",
    "Objective-C", "Groovy", "Terraform",
}

BRANCH_KEYWORDS = re.compile(
    r"\b(if|elif|else\s+if|for|while|case|when|catch|except|rescue|and|or|"
    r"&&|\|\||\?\?|=>)\b|\?[^:\n]{0,80}:"
)

DOCSTRING_START = re.compile(r"""^[rRbBuUfF]{0,2}("{3}|'{3})""")

TODO_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX|BUG|OPTIMIZE|DEPRECATED)\b[:\s-]*(.*)")

DEFAULT_EXCLUDES = (
    "node_modules/", "vendor/", "dist/", "build/", ".venv/", "venv/", "__pycache__/",
    ".git/", "target/", "coverage/", ".next/", ".idea/", ".mypy_cache/", ".pytest_cache/",
    "site-packages/", ".tox/", "out/", "bower_components/", "third_party/",
)

GENERATED_HINTS = (
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Cargo.lock",
    "composer.lock", "Gemfile.lock", ".min.js", ".min.css", ".map", ".pb.go",
    "_pb2.py", ".generated.", ".snap",
)

BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".tar",
    ".bz2", ".xz", ".7z", ".jar", ".war", ".class", ".so", ".dylib", ".dll", ".exe",
    ".bin", ".o", ".a", ".woff", ".woff2", ".ttf", ".eot", ".otf", ".mp3", ".mp4",
    ".mov", ".avi", ".wav", ".psd", ".sqlite", ".db", ".pyc", ".pack", ".idx",
}


def detect_language(path: str) -> Tuple[str, Tuple[str, ...], Optional[Tuple[str, str]]]:
    base = os.path.basename(path)
    if base in FILENAME_LANGUAGES:
        return FILENAME_LANGUAGES[base]
    _, ext = os.path.splitext(base)
    return LANGUAGES.get(ext.lower(), ("Other", ("#",), None))


def is_excluded(path: str, excludes: Tuple[str, ...]) -> bool:
    normalised = path.replace(os.sep, "/")
    for pattern in excludes:
        if not pattern:
            continue
        if pattern.endswith("/"):
            if normalised.startswith(pattern) or f"/{pattern}" in f"/{normalised}":
                return True
        elif pattern in normalised:
            return True
    return False


def looks_generated(path: str) -> bool:
    normalised = path.replace(os.sep, "/")
    return any(hint in normalised for hint in GENERATED_HINTS)


def is_binary_path(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in BINARY_EXTS


def scan_file(root: str, rel_path: str, max_bytes: int = 2_000_000,
              collect_todos: bool = True) -> Optional[FileScan]:
    """Scan one file; returns None when unreadable, binary or oversized."""
    full = os.path.join(root, rel_path)
    try:
        size = os.path.getsize(full)
    except OSError:
        return None
    if size > max_bytes or is_binary_path(rel_path):
        return None
    try:
        with open(full, "r", encoding="utf-8", errors="strict") as fh:
            text = fh.read()
    except (UnicodeDecodeError, OSError):
        return None
    if "\0" in text:
        return None

    language, line_comments, block = detect_language(rel_path)
    scan = FileScan(path=rel_path, language=language, bytes=size)
    in_block = False
    in_docstring = False
    docstring_delim = ""
    for lineno, raw in enumerate(text.splitlines(), start=1):
        scan.lines += 1
        stripped = raw.strip()
        if not stripped:
            scan.blank += 1
            continue
        if len(raw) > 120:
            scan.long_lines += 1

        is_comment = False
        if block:
            start, end = block
            if in_block:
                is_comment = True
                if end in stripped:
                    in_block = False
            elif stripped.startswith(start):
                is_comment = True
                if end not in stripped[len(start):]:
                    in_block = True
        if not is_comment and line_comments and stripped.startswith(tuple(line_comments)):
            is_comment = True
        # Python docstrings are documentation, not code.
        if language == "Python" and not is_comment:
            if in_docstring:
                is_comment = True
                if docstring_delim in stripped:
                    in_docstring = False
            else:
                opens = None
                match = DOCSTRING_START.match(stripped)
                if match:
                    is_comment = True
                    delim = match.group(1)
                    if delim not in stripped[match.end():]:
                        opens = delim
                else:
                    # A multi-line string opened mid-line (EPILOG = """...) is
                    # code, but its continuation lines must not be parsed as such.
                    for delim in ('"""', "'''"):
                        if stripped.count(delim) % 2 == 1:
                            opens = delim
                            break
                if opens:
                    in_docstring = True
                    docstring_delim = opens

        if is_comment:
            scan.comment += 1
        else:
            scan.loc += 1
            expanded = raw.replace("\t", "    ")
            indent = len(expanded) - len(expanded.lstrip(" "))
            scan.max_indent = max(scan.max_indent, indent // 4)
            if language in CODE_LANGUAGES:
                scan.complexity += len(BRANCH_KEYWORDS.findall(stripped))

        if collect_todos:
            match = TODO_PATTERN.search(stripped)
            if match and _in_comment(stripped, match.start(), is_comment,
                                     line_comments, block, language):
                note = match.group(2).strip()[:160]
                scan.todos.append((lineno, match.group(1), note))
    return scan


def _in_comment(stripped: str, index: int, whole_line_comment: bool,
                line_comments: Tuple[str, ...], block: Optional[Tuple[str, str]],
                language: str) -> bool:
    """True when position `index` sits inside a comment (incl. trailing ones)."""
    if whole_line_comment or language not in CODE_LANGUAGES:
        return True
    starts = [stripped.find(prefix) for prefix in line_comments]
    if block:
        starts.append(stripped.find(block[0]))
    positions = [pos for pos in starts if pos != -1 and pos <= index]
    return bool(positions)


def scan_paths(root: str, paths: List[str], excludes: Tuple[str, ...] = DEFAULT_EXCLUDES,
               skip_generated: bool = True) -> Dict[str, FileScan]:
    results: Dict[str, FileScan] = {}
    for rel in paths:
        if is_excluded(rel, excludes):
            continue
        if skip_generated and looks_generated(rel):
            continue
        scan = scan_file(root, rel)
        if scan is not None:
            results[rel] = scan
    return results
