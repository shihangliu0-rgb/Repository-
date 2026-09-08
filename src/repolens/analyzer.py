"""Top level analysis pipeline."""

from __future__ import annotations

import os
import time
from typing import Dict, List, Optional, Tuple

from . import gitlog, metrics, scan as scanner
from .model import FileReport


class AnalysisError(RuntimeError):
    pass


def analyze(
    path: str,
    since: Optional[str] = None,
    until: Optional[str] = None,
    max_commits: Optional[int] = None,
    excludes: Tuple[str, ...] = scanner.DEFAULT_EXCLUDES,
    include_generated: bool = False,
    top: int = 20,
    now: Optional[float] = None,
) -> dict:
    """Analyse a git repository and return a plain-dict result document."""
    path = os.path.abspath(path)
    if not gitlog.is_git_repo(path):
        raise AnalysisError(f"{path} is not a git repository (or git history is unavailable)")
    root = gitlog.repo_root(path)
    now = now if now is not None else time.time()

    commits = gitlog.read_commits(root, since=since, until=until, max_commits=max_commits)
    tracked = gitlog.list_tracked_files(root)
    scans = scanner.scan_paths(root, tracked, excludes=excludes,
                               skip_generated=not include_generated)

    history_all = gitlog.aggregate_history(commits)
    history = {p: h for p, h in history_all.items()}

    reports: List[FileReport] = metrics.build_file_reports(scans, history, now=now)
    authors = gitlog.author_stats(commits)
    timeline = metrics.commit_timeline(commits)

    summary = {
        "repository": os.path.basename(root.rstrip(os.sep)) or root,
        "root": root,
        "branch": gitlog.current_branch(root),
        "generated_at": int(now),
        "window": {"since": since, "until": until, "max_commits": max_commits},
        "commits": len(commits),
        "authors": len(authors),
        "tracked_files": len(tracked),
        "analysed_files": len(scans),
        "loc": sum(s.loc for s in scans.values()),
        "comment_lines": sum(s.comment for s in scans.values()),
        "blank_lines": sum(s.blank for s in scans.values()),
        "total_added": sum(c["added"] for c in authors),
        "total_deleted": sum(c["deleted"] for c in authors),
        "first_commit": min((c.timestamp for c in commits), default=None),
        "last_commit": max((c.timestamp for c in commits), default=None),
        "bus_factor": metrics.bus_factor(authors),
    }

    score, dimensions = metrics.health_score(reports, summary)
    summary["health_score"] = score
    summary["health_dimensions"] = dimensions

    result = {
        "schema": "repolens/1",
        "summary": summary,
        "hotspots": [r.to_dict() for r in reports[:top]],
        "files": [r.to_dict() for r in reports],
        "languages": metrics.language_summary(scans),
        "authors": authors,
        "timeline": timeline,
        "directories": metrics.directory_summary(reports),
        "coupling": gitlog.coupling(commits),
        "knowledge_risk": metrics.knowledge_risk(reports),
        "stale": metrics.stale_files(reports, now and 365.0 or 365.0),
        "todos": metrics.collect_todos(scans),
        "quick_wins": metrics.quick_wins(reports),
    }
    return result


def compare(baseline: dict, current: dict, limit: int = 15) -> dict:
    """Diff two RepoLens result documents (for trend tracking in CI)."""
    base_files = {f["path"]: f for f in baseline.get("files", [])}
    cur_files = {f["path"]: f for f in current.get("files", [])}

    changes = []
    for path, cur in cur_files.items():
        base = base_files.get(path)
        if base is None:
            if cur["risk"] >= 50:
                changes.append({"path": path, "status": "new", "risk": cur["risk"],
                                "delta": cur["risk"]})
            continue
        delta = round(cur["risk"] - base["risk"], 1)
        if abs(delta) >= 1.0:
            changes.append({"path": path, "status": "changed", "risk": cur["risk"],
                            "delta": delta})
    for path, base in base_files.items():
        if path not in cur_files:
            changes.append({"path": path, "status": "removed", "risk": 0.0,
                            "delta": -base["risk"]})

    changes.sort(key=lambda c: -abs(c["delta"]))
    return {
        "health_before": baseline.get("summary", {}).get("health_score"),
        "health_after": current.get("summary", {}).get("health_score"),
        "changes": changes[:limit],
        "worsened": sum(1 for c in changes if c["delta"] > 0),
        "improved": sum(1 for c in changes if c["delta"] < 0),
    }
