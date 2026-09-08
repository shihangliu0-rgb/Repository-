"""Data structures shared across RepoLens."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple


@dataclass
class Commit:
    """A single commit with the files it touched."""

    sha: str
    timestamp: int
    author: str
    email: str
    subject: str
    files: List[Tuple[str, int, int]] = field(default_factory=list)  # (path, added, deleted)

    @property
    def churn(self) -> int:
        return sum(a + d for _, a, d in self.files)


@dataclass
class FileHistory:
    """Aggregated git history for one path."""

    path: str
    commits: int = 0
    added: int = 0
    deleted: int = 0
    first_seen: Optional[int] = None
    last_seen: Optional[int] = None
    authors: Dict[str, int] = field(default_factory=dict)  # author -> commits

    @property
    def churn(self) -> int:
        return self.added + self.deleted

    @property
    def author_count(self) -> int:
        return len(self.authors)

    @property
    def main_author(self) -> str:
        if not self.authors:
            return ""
        return max(self.authors.items(), key=lambda kv: kv[1])[0]

    @property
    def ownership(self) -> float:
        """Share of commits made by the dominant author (0..1)."""
        if not self.authors:
            return 0.0
        return max(self.authors.values()) / float(sum(self.authors.values()))


@dataclass
class FileScan:
    """Static properties of a file that currently exists on disk."""

    path: str
    language: str
    loc: int = 0            # non-blank, non-comment lines
    lines: int = 0          # physical lines
    blank: int = 0
    comment: int = 0
    complexity: int = 0     # branch-keyword based cyclomatic estimate
    max_indent: int = 0     # deepest indentation level
    long_lines: int = 0
    todos: List[Tuple[int, str, str]] = field(default_factory=list)  # (lineno, tag, text)
    bytes: int = 0


@dataclass
class FileReport:
    """History + static scan + derived scores for one file."""

    path: str
    language: str = "unknown"
    loc: int = 0
    complexity: int = 0
    max_indent: int = 0
    comment_ratio: float = 0.0
    commits: int = 0
    churn: int = 0
    added: int = 0
    deleted: int = 0
    authors: int = 0
    main_author: str = ""
    ownership: float = 0.0
    age_days: float = 0.0
    last_change_days: float = 0.0
    todos: int = 0
    hotspot: float = 0.0     # 0..100, complexity x change frequency
    risk: float = 0.0        # 0..100, hotspot + knowledge/staleness penalties
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
