"""Metric computation: combine git history with static scans into scores."""

from __future__ import annotations

import math
import os
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .model import FileHistory, FileReport, FileScan

DAY = 86400.0

# Absolute reference points used to damp scores in small repositories.
# A file only approaches the top of the scale when it is genuinely big or
# genuinely churny, not merely the largest thing in a tiny project.
ABS_COMPLEXITY_REF = 250.0
ABS_LOC_REF = 900.0
ABS_COMMITS_REF = 80.0
ABS_CHURN_REF = 4000.0
HIGH_RISK = 70.0
SIGNIFICANT_LOC = 60.0
SIGNIFICANT_COMMITS = 4.0

# Non-code files churn a lot (changelogs, docs, author lists) without carrying
# the same defect risk, so their scores are damped rather than dropped.
LANGUAGE_WEIGHT = {
    "Markdown": 0.35, "reStructuredText": 0.35, "Text": 0.35,
    "JSON": 0.45, "YAML": 0.5, "TOML": 0.5, "INI": 0.5, "Config": 0.4,
    "HTML": 0.75, "CSS": 0.75, "SQL": 0.85, "Docker": 0.6, "Make": 0.6,
    "Other": 0.4,
}


def language_weight(language: str) -> float:
    return LANGUAGE_WEIGHT.get(language, 1.0)


def _norm(value: float, maximum: float) -> float:
    """Log-scaled 0..1 normalisation (code metrics are heavily long-tailed)."""
    if maximum <= 0:
        return 0.0
    return min(1.0, math.log1p(max(0.0, value)) / math.log1p(maximum))


def build_file_reports(
    scans: Dict[str, FileScan],
    history: Dict[str, FileHistory],
    now: Optional[float] = None,
) -> List[FileReport]:
    now = now if now is not None else time.time()
    if not scans:
        return []

    max_complexity = max((s.complexity for s in scans.values()), default=0)
    max_loc = max((s.loc for s in scans.values()), default=0)
    max_commits = max((h.commits for h in history.values()), default=0)
    max_churn = max((h.churn for h in history.values()), default=0)

    reports: List[FileReport] = []
    for path, scan in scans.items():
        hist = history.get(path)
        rep = FileReport(
            path=path,
            language=scan.language,
            loc=scan.loc,
            complexity=scan.complexity,
            max_indent=scan.max_indent,
            comment_ratio=round(scan.comment / scan.lines, 3) if scan.lines else 0.0,
            todos=len(scan.todos),
        )
        if hist:
            rep.commits = hist.commits
            rep.churn = hist.churn
            rep.added = hist.added
            rep.deleted = hist.deleted
            rep.authors = hist.author_count
            rep.main_author = hist.main_author
            rep.ownership = round(hist.ownership, 3)
            if hist.first_seen:
                rep.age_days = round((now - hist.first_seen) / DAY, 1)
            if hist.last_seen:
                rep.last_change_days = round((now - hist.last_seen) / DAY, 1)

        # Relative score: how this file compares to the rest of THIS repository.
        rel_size = max(_norm(scan.complexity, max_complexity), _norm(scan.loc, max_loc) * 0.8)
        rel_change = max(_norm(rep.commits, max_commits), _norm(rep.churn, max_churn) * 0.9)
        # Absolute score: damping against fixed reference points, so a two-file
        # toy repository does not report a 1-line README as its biggest hazard.
        abs_size = max(_norm(scan.complexity, ABS_COMPLEXITY_REF), _norm(scan.loc, ABS_LOC_REF) * 0.9)
        abs_change = max(_norm(rep.commits, ABS_COMMITS_REF), _norm(rep.churn, ABS_CHURN_REF) * 0.9)
        # Significance ramp: a 5-line file or a file with a single commit can
        # never be a hotspot, however extreme it looks relative to its peers.
        size_sig = math.sqrt(min(1.0, scan.loc / SIGNIFICANT_LOC))
        change_sig = math.sqrt(min(1.0, max(rep.commits, 1) / SIGNIFICANT_COMMITS))
        size_score = math.sqrt(rel_size * abs_size) * size_sig
        change_score = math.sqrt(rel_change * abs_change) * change_sig
        weight = language_weight(scan.language)
        rep.hotspot = round(100.0 * math.sqrt(size_score * change_score) * weight, 1)

        risk = rep.hotspot
        reasons: List[str] = []
        if size_score > 0.6 and change_score > 0.6:
            reasons.append("large and frequently modified")
        if rep.commits >= 5 and rep.ownership >= 0.8 and rep.authors <= 2:
            risk += 12
            reasons.append(f"knowledge concentrated in {rep.main_author} ({int(rep.ownership * 100)}% of commits)")
        if scan.max_indent >= 6:
            risk += 8
            reasons.append(f"deep nesting (indent level {scan.max_indent})")
        if scan.loc >= 400:
            risk += 6
            reasons.append(f"long file ({scan.loc} LOC)")
        if scan.language in ("Python", "JavaScript", "TypeScript", "Go", "Java", "Rust", "C", "C++", "C#", "Ruby", "PHP"):
            if scan.loc >= 120 and rep.comment_ratio < 0.03:
                risk += 5
                reasons.append("almost no comments for its size")
        if rep.commits >= 8 and rep.last_change_days and rep.last_change_days <= 30:
            risk += 5
            reasons.append("still churning in the last 30 days")
        if rep.todos >= 3:
            risk += 4
            reasons.append(f"{rep.todos} TODO/FIXME markers")
        if scan.complexity and scan.loc and (scan.complexity / max(scan.loc, 1)) > 0.35 and scan.loc > 60:
            risk += 5
            reasons.append("high branch density")

        rep.risk = round(min(100.0, rep.hotspot + (risk - rep.hotspot) * weight), 1)
        rep.reasons = reasons
        reports.append(rep)

    reports.sort(key=lambda r: (-r.risk, -r.hotspot, r.path))
    return reports


def language_summary(scans: Dict[str, FileScan]) -> List[dict]:
    agg: Dict[str, dict] = {}
    for scan in scans.values():
        item = agg.setdefault(scan.language, {
            "language": scan.language, "files": 0, "loc": 0, "comment": 0, "blank": 0,
        })
        item["files"] += 1
        item["loc"] += scan.loc
        item["comment"] += scan.comment
        item["blank"] += scan.blank
    out = sorted(agg.values(), key=lambda i: -i["loc"])
    return out


def commit_timeline(commits) -> List[dict]:
    """Commits and churn grouped by calendar month."""
    buckets: Dict[str, dict] = {}
    for c in commits:
        key = time.strftime("%Y-%m", time.gmtime(c.timestamp))
        item = buckets.setdefault(key, {"month": key, "commits": 0, "added": 0, "deleted": 0, "authors": set()})
        item["commits"] += 1
        item["authors"].add(c.author)
        for _, added, deleted in c.files:
            item["added"] += added
            item["deleted"] += deleted
    out = []
    for item in sorted(buckets.values(), key=lambda i: i["month"]):
        item = dict(item)
        item["authors"] = len(item["authors"])
        out.append(item)
    return out


def directory_summary(reports: List[FileReport], depth: int = 2, limit: int = 20) -> List[dict]:
    agg: Dict[str, dict] = {}
    for rep in reports:
        parts = rep.path.split("/")
        key = "/".join(parts[:depth]) if len(parts) > depth else ("/".join(parts[:-1]) or ".")
        item = agg.setdefault(key, {
            "directory": key, "files": 0, "loc": 0, "commits": 0, "churn": 0,
            "risk_sum": 0.0, "authors": set(),
        })
        item["files"] += 1
        item["loc"] += rep.loc
        item["commits"] += rep.commits
        item["churn"] += rep.churn
        item["risk_sum"] += rep.risk
        if rep.main_author:
            item["authors"].add(rep.main_author)
    out = []
    for item in agg.values():
        item = dict(item)
        item["authors"] = len(item["authors"])
        item["avg_risk"] = round(item.pop("risk_sum") / max(item["files"], 1), 1)
        out.append(item)
    out.sort(key=lambda i: -i["churn"])
    return out[:limit]


def knowledge_risk(reports: List[FileReport], min_commits: int = 4,
                   ownership_threshold: float = 0.8, limit: int = 15) -> List[dict]:
    """Files where a single person holds nearly all the knowledge."""
    out = []
    for rep in reports:
        if rep.commits >= min_commits and rep.ownership >= ownership_threshold and rep.loc >= 30:
            out.append({
                "path": rep.path,
                "author": rep.main_author,
                "ownership": rep.ownership,
                "commits": rep.commits,
                "loc": rep.loc,
                "risk": rep.risk,
            })
    out.sort(key=lambda i: (-i["risk"], -i["ownership"]))
    return out[:limit]


def stale_files(reports: List[FileReport], days: float = 365.0, min_loc: int = 80,
                limit: int = 15) -> List[dict]:
    out = [
        {"path": r.path, "loc": r.loc, "last_change_days": r.last_change_days,
         "commits": r.commits, "language": r.language}
        for r in reports
        if r.last_change_days >= days and r.loc >= min_loc
    ]
    out.sort(key=lambda i: -i["last_change_days"])
    return out[:limit]


def bus_factor(author_stats_list: List[dict]) -> dict:
    """How many authors account for 50% of all commits."""
    total = sum(a["commits"] for a in author_stats_list) or 1
    running = 0
    count = 0
    for a in author_stats_list:
        running += a["commits"]
        count += 1
        if running / total >= 0.5:
            break
    top_share = (author_stats_list[0]["commits"] / total) if author_stats_list else 0.0
    return {
        "bus_factor": count,
        "authors": len(author_stats_list),
        "top_author": author_stats_list[0]["author"] if author_stats_list else "",
        "top_author_share": round(top_share, 3),
    }


def collect_todos(scans: Dict[str, FileScan], limit: int = 100) -> List[dict]:
    items = []
    for scan in scans.values():
        for lineno, tag, text in scan.todos:
            items.append({"path": scan.path, "line": lineno, "tag": tag, "text": text})
    priority = {"FIXME": 0, "BUG": 1, "XXX": 2, "HACK": 3, "TODO": 4, "OPTIMIZE": 5, "DEPRECATED": 6}
    items.sort(key=lambda i: (priority.get(i["tag"], 9), i["path"], i["line"]))
    return items[:limit]


def health_score(reports: List[FileReport], summary: dict) -> Tuple[int, List[dict]]:
    """A 0-100 repository health score with per-dimension breakdown.

    Each dimension is scored independently so the number is explainable
    instead of being a black box.
    """
    dims: List[dict] = []
    total_loc = sum(r.loc for r in reports) or 1

    # 1. Hotspot concentration: share of LOC sitting in high-risk files.
    risky_loc = sum(r.loc for r in reports if r.risk >= HIGH_RISK)
    share = risky_loc / total_loc
    hotspot_score = 100.0 * (1.0 - min(1.0, share / 0.5))
    dims.append({
        "name": "Hotspot control",
        "score": round(hotspot_score),
        "detail": f"{share * 100:.1f}% of code lives in high-risk files",
    })

    # 2. Knowledge distribution.
    bf = summary.get("bus_factor", {})
    factor = bf.get("bus_factor", 1)
    authors = bf.get("authors", 1)
    if authors <= 1:
        knowledge = 40.0
        detail = "single contributor in the analysed window"
    else:
        knowledge = min(100.0, 45.0 + factor * 18.0)
        detail = f"{factor} of {authors} authors produce 50% of commits"
    dims.append({"name": "Knowledge spread", "score": round(knowledge), "detail": detail})

    # 3. Documentation / comments in code files.
    code_reports = [r for r in reports if r.loc >= 30 and r.language not in ("Markdown", "JSON", "YAML", "Other")]
    if code_reports:
        avg_comment = sum(r.comment_ratio for r in code_reports) / len(code_reports)
        doc_score = min(100.0, avg_comment / 0.15 * 100.0)
        doc_detail = f"average comment ratio {avg_comment * 100:.1f}%"
    else:
        doc_score, doc_detail = 70.0, "not enough code files to judge"
    dims.append({"name": "Documentation", "score": round(doc_score), "detail": doc_detail})

    # 4. File size discipline.
    big = [r for r in reports if r.loc >= 400]
    big_share = len(big) / max(len(reports), 1)
    size_score = max(0.0, 100.0 - big_share * 400.0)
    dims.append({
        "name": "File size discipline",
        "score": round(size_score),
        "detail": f"{len(big)} files over 400 LOC",
    })

    # 5. Test presence.
    test_loc = sum(
        r.loc for r in reports
        if "test" in r.path.lower() or "spec" in r.path.lower()
    )
    ratio = test_loc / total_loc
    test_score = min(100.0, ratio / 0.25 * 100.0)
    dims.append({
        "name": "Test coverage proxy",
        "score": round(test_score),
        "detail": f"{ratio * 100:.1f}% of LOC in test/spec files",
    })

    overall = round(sum(d["score"] for d in dims) / len(dims))
    return overall, dims


def quick_wins(reports: List[FileReport], limit: int = 5) -> List[dict]:
    """Highest risk-per-line files: small enough to fix, painful enough to matter."""
    candidates = []
    for rep in reports:
        if rep.risk < 40 or rep.loc < 40 or rep.loc > 400:
            continue
        candidates.append({
            "path": rep.path,
            "risk": rep.risk,
            "loc": rep.loc,
            "commits": rep.commits,
            "reasons": rep.reasons,
            "leverage": round(rep.risk / math.log1p(rep.loc), 1),
        })
    candidates.sort(key=lambda c: -c["leverage"])
    return candidates[:limit]
