"""Git history mining. Shells out to `git`; no third-party dependencies."""

from __future__ import annotations

import os
import subprocess
from typing import Dict, Iterable, List, Optional, Tuple

from .model import Commit, FileHistory

RECORD_SEP = "\x1e"
FIELD_SEP = "\x1f"


class GitError(RuntimeError):
    pass


def run_git(repo: str, args: List[str], check: bool = True) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", repo, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
        )
    except FileNotFoundError as exc:  # pragma: no cover - environment specific
        raise GitError("`git` executable not found on PATH") from exc
    if check and proc.returncode != 0:
        raise GitError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


def is_git_repo(path: str) -> bool:
    try:
        out = run_git(path, ["rev-parse", "--is-inside-work-tree"])
    except GitError:
        return False
    return out.strip() == "true"


def repo_root(path: str) -> str:
    return run_git(path, ["rev-parse", "--show-toplevel"]).strip() or os.path.abspath(path)


def current_branch(path: str) -> str:
    try:
        return run_git(path, ["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    except GitError:  # pragma: no cover - detached/empty repo
        return "HEAD"


def _split_rename(path: str) -> str:
    """Normalise numstat rename syntax to the destination path.

    Handles both `old => new` and `dir/{old => new}/file` forms.
    """
    if "=>" not in path:
        return path
    if "{" in path and "}" in path:
        pre, rest = path.split("{", 1)
        mid, post = rest.split("}", 1)
        new = mid.split("=>")[-1].strip()
        merged = f"{pre}{new}{post}"
        return merged.replace("//", "/")
    return path.split("=>")[-1].strip()


def read_commits(
    repo: str,
    since: Optional[str] = None,
    until: Optional[str] = None,
    max_commits: Optional[int] = None,
    include_merges: bool = False,
) -> List[Commit]:
    """Read commit history with per-file line statistics."""
    fmt = RECORD_SEP + FIELD_SEP.join(["%H", "%at", "%an", "%ae", "%s"])
    args = ["log", f"--pretty=format:{fmt}", "--numstat", "-M", "--date=raw"]
    if not include_merges:
        args.append("--no-merges")
    if since:
        args.append(f"--since={since}")
    if until:
        args.append(f"--until={until}")
    if max_commits:
        args.append(f"-n{int(max_commits)}")
    out = run_git(repo, args)

    commits: List[Commit] = []
    for chunk in out.split(RECORD_SEP):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        head, _, body = chunk.partition("\n")
        parts = head.split(FIELD_SEP)
        if len(parts) < 5:
            continue
        sha, ts, author, email, subject = parts[0], parts[1], parts[2], parts[3], parts[4]
        try:
            timestamp = int(ts)
        except ValueError:
            continue
        commit = Commit(sha=sha, timestamp=timestamp, author=author.strip(),
                        email=email.strip().lower(), subject=subject.strip())
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            cols = line.split("\t")
            if len(cols) < 3:
                continue
            added_s, deleted_s, path = cols[0], cols[1], "\t".join(cols[2:])
            if added_s == "-" or deleted_s == "-":
                continue  # binary file
            try:
                added, deleted = int(added_s), int(deleted_s)
            except ValueError:
                continue
            commit.files.append((_split_rename(path.strip()), added, deleted))
        commits.append(commit)
    return commits


def aggregate_history(commits: Iterable[Commit]) -> Dict[str, FileHistory]:
    """Fold commits into per-path history records."""
    hist: Dict[str, FileHistory] = {}
    for c in commits:
        for path, added, deleted in c.files:
            fh = hist.get(path)
            if fh is None:
                fh = FileHistory(path=path)
                hist[path] = fh
            fh.commits += 1
            fh.added += added
            fh.deleted += deleted
            fh.authors[c.author] = fh.authors.get(c.author, 0) + 1
            if fh.first_seen is None or c.timestamp < fh.first_seen:
                fh.first_seen = c.timestamp
            if fh.last_seen is None or c.timestamp > fh.last_seen:
                fh.last_seen = c.timestamp
    return hist


def coupling(
    commits: Iterable[Commit],
    min_shared: int = 3,
    min_ratio: float = 0.4,
    max_files_per_commit: int = 30,
    limit: int = 25,
) -> List[dict]:
    """Temporal coupling: pairs of files that keep changing together.

    Commits touching a huge number of files (bulk reformat, vendoring) are
    skipped because they create noise rather than signal.
    """
    pair_counts: Dict[Tuple[str, str], int] = {}
    file_counts: Dict[str, int] = {}
    for c in commits:
        paths = sorted({p for p, _, _ in c.files})
        if len(paths) > max_files_per_commit:
            continue
        for p in paths:
            file_counts[p] = file_counts.get(p, 0) + 1
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                key = (paths[i], paths[j])
                pair_counts[key] = pair_counts.get(key, 0) + 1

    results: List[dict] = []
    for (a, b), shared in pair_counts.items():
        if shared < min_shared:
            continue
        denom = min(file_counts.get(a, 1), file_counts.get(b, 1))
        ratio = shared / float(denom) if denom else 0.0
        if ratio < min_ratio:
            continue
        results.append({
            "a": a,
            "b": b,
            "shared": shared,
            "commits_a": file_counts.get(a, 0),
            "commits_b": file_counts.get(b, 0),
            "ratio": round(ratio, 3),
        })
    results.sort(key=lambda r: (-r["ratio"], -r["shared"]))
    return results[:limit]


def author_stats(commits: Iterable[Commit]) -> List[dict]:
    stats: Dict[str, dict] = {}
    for c in commits:
        s = stats.setdefault(c.author, {
            "author": c.author, "commits": 0, "added": 0, "deleted": 0,
            "files": set(), "first": c.timestamp, "last": c.timestamp,
        })
        s["commits"] += 1
        s["first"] = min(s["first"], c.timestamp)
        s["last"] = max(s["last"], c.timestamp)
        for path, added, deleted in c.files:
            s["added"] += added
            s["deleted"] += deleted
            s["files"].add(path)
    out = []
    for s in stats.values():
        s = dict(s)
        s["files"] = len(s["files"])
        out.append(s)
    out.sort(key=lambda s: -s["commits"])
    return out


def list_tracked_files(repo: str) -> List[str]:
    out = run_git(repo, ["ls-files", "-z"])
    return [p for p in out.split("\0") if p]
