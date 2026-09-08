"""ANSI terminal rendering. No dependencies, degrades gracefully when piped."""

from __future__ import annotations

import os
import shutil
import sys
import time
from typing import List, Optional, Sequence

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"


class Style:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def __call__(self, text: str, *codes: str) -> str:
        if not self.enabled or not codes:
            return text
        return "".join(codes) + text + RESET


def make_style(no_color: bool = False, stream=None) -> Style:
    stream = stream or sys.stdout
    if no_color or os.environ.get("NO_COLOR"):
        return Style(False)
    return Style(bool(getattr(stream, "isatty", lambda: False)()))


def term_width(default: int = 100) -> int:
    try:
        return max(60, min(shutil.get_terminal_size((default, 24)).columns, 160))
    except Exception:  # pragma: no cover
        return default


def truncate(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return "…" + text[-(width - 1):]


def table(rows: Sequence[Sequence[str]], headers: Sequence[str], style: Style,
          aligns: Optional[Sequence[str]] = None, max_width: Optional[int] = None) -> str:
    if not rows:
        return style("  (nothing to report)", DIM)
    cols = len(headers)
    aligns = aligns or ["l"] * cols
    widths = [len(h) for h in headers]
    for row in rows:
        for i in range(cols):
            widths[i] = max(widths[i], len(str(row[i])))

    max_width = max_width or term_width()
    overhead = 2 + 3 * (cols - 1)
    if sum(widths) + overhead > max_width:
        # shrink the widest column (usually a path)
        excess = sum(widths) + overhead - max_width
        widest = widths.index(max(widths))
        widths[widest] = max(12, widths[widest] - excess)

    def fmt_row(values, bold=False):
        cells = []
        for i, value in enumerate(values):
            text = truncate(str(value), widths[i])
            cells.append(text.rjust(widths[i]) if aligns[i] == "r" else text.ljust(widths[i]))
        line = "  " + "   ".join(cells)
        return style(line, BOLD) if bold else line

    out = [fmt_row(headers, bold=True),
           style("  " + "   ".join("─" * w for w in widths), DIM)]
    out.extend(fmt_row(r) for r in rows)
    return "\n".join(out)


def bar(value: float, maximum: float, width: int = 18, char: str = "█") -> str:
    if maximum <= 0:
        return ""
    filled = int(round(width * min(1.0, value / maximum)))
    return char * filled + "·" * (width - filled)


def score_color(score: float) -> str:
    if score >= 75:
        return GREEN
    if score >= 50:
        return YELLOW
    return RED


def risk_color(risk: float) -> str:
    if risk >= 70:
        return RED
    if risk >= 45:
        return YELLOW
    return GREEN


def _fmt_date(ts: Optional[int]) -> str:
    if not ts:
        return "-"
    return time.strftime("%Y-%m-%d", time.gmtime(ts))


def render(result: dict, style: Style, top: int = 12, show_todos: bool = False) -> str:
    s = style
    summary = result["summary"]
    out: List[str] = []
    width = term_width()

    title = f" RepoLens · {summary['repository']} ({summary['branch']}) "
    out.append(s("╭" + "─" * (width - 2) + "╮", CYAN))
    out.append(s("│", CYAN) + s(title.ljust(width - 2), BOLD) + s("│", CYAN))
    out.append(s("╰" + "─" * (width - 2) + "╯", CYAN))

    score = summary["health_score"]
    out.append("")
    out.append("  " + s("HEALTH SCORE ", BOLD) +
               s(f"{score}/100", score_color(score), BOLD) + "   " +
               s(bar(score, 100, 30), score_color(score)))
    for dim in summary["health_dimensions"]:
        out.append("    " + s(f"{dim['name']:<22}", DIM) +
                   s(f"{dim['score']:>3}", score_color(dim["score"])) + "  " +
                   s(bar(dim["score"], 100, 16), score_color(dim["score"])) + "  " +
                   s(dim["detail"], DIM))

    out.append("")
    bf = summary["bus_factor"]
    facts = [
        f"{summary['commits']} commits", f"{summary['authors']} authors",
        f"{summary['analysed_files']} files", f"{summary['loc']:,} LOC",
        f"bus factor {bf['bus_factor']}",
        f"{_fmt_date(summary['first_commit'])} → {_fmt_date(summary['last_commit'])}",
    ]
    out.append("  " + s(" · ".join(facts), DIM))

    out.append("")
    out.append(s("  HOTSPOTS", BOLD) + s("  (complexity × change frequency — fix these first)", DIM))
    rows = []
    for rep in result["hotspots"][:top]:
        rows.append([
            rep["path"], f"{rep['risk']:.0f}", f"{rep['hotspot']:.0f}", rep["loc"],
            rep["commits"], rep["authors"], rep["language"],
        ])
    out.append(table(rows, ["FILE", "RISK", "HOT", "LOC", "COMMITS", "AUTHORS", "LANG"], s,
                     aligns=["l", "r", "r", "r", "r", "r", "l"], max_width=width))

    if result["hotspots"]:
        out.append("")
        out.append(s("  WHY THE TOP FILES ARE RISKY", BOLD))
        for rep in result["hotspots"][:3]:
            if not rep["reasons"]:
                continue
            out.append("    " + s(rep["path"], risk_color(rep["risk"]), BOLD))
            for reason in rep["reasons"]:
                out.append("      " + s("• " + reason, DIM))

    if result["quick_wins"]:
        out.append("")
        out.append(s("  QUICK WINS", BOLD) + s("  (high risk, still small enough to refactor)", DIM))
        rows = [[q["path"], f"{q['risk']:.0f}", q["loc"], q["commits"]] for q in result["quick_wins"]]
        out.append(table(rows, ["FILE", "RISK", "LOC", "COMMITS"], s,
                         aligns=["l", "r", "r", "r"], max_width=width))

    if result["knowledge_risk"]:
        out.append("")
        out.append(s("  KNOWLEDGE RISK", BOLD) + s("  (one person owns nearly all changes)", DIM))
        rows = [[k["path"], k["author"], f"{k['ownership'] * 100:.0f}%", k["commits"]]
                for k in result["knowledge_risk"][:8]]
        out.append(table(rows, ["FILE", "OWNER", "SHARE", "COMMITS"], s,
                         aligns=["l", "l", "r", "r"], max_width=width))

    if result["coupling"]:
        out.append("")
        out.append(s("  TEMPORAL COUPLING", BOLD) + s("  (files that keep changing together)", DIM))
        rows = [[c["a"], c["b"], f"{c['ratio'] * 100:.0f}%", c["shared"]]
                for c in result["coupling"][:8]]
        out.append(table(rows, ["FILE A", "FILE B", "TOGETHER", "SHARED"], s,
                         aligns=["l", "l", "r", "r"], max_width=width))

    if result["languages"]:
        out.append("")
        out.append(s("  LANGUAGES", BOLD))
        max_loc = max(l["loc"] for l in result["languages"]) or 1
        for lang in result["languages"][:8]:
            out.append("    " + s(f"{lang['language']:<16}", "") +
                       s(bar(lang["loc"], max_loc, 24), BLUE) +
                       s(f"  {lang['loc']:>7,} LOC  {lang['files']:>4} files", DIM))

    if result["authors"]:
        out.append("")
        out.append(s("  TOP CONTRIBUTORS", BOLD))
        max_c = max(a["commits"] for a in result["authors"]) or 1
        for a in result["authors"][:6]:
            out.append("    " + s(f"{truncate(a['author'], 22):<22}", "") +
                       s(bar(a["commits"], max_c, 20), MAGENTA) +
                       s(f"  {a['commits']:>5} commits  +{a['added']:,}/-{a['deleted']:,}", DIM))

    if show_todos and result["todos"]:
        out.append("")
        out.append(s("  TODO / FIXME MARKERS", BOLD))
        rows = [[t["tag"], f"{t['path']}:{t['line']}", t["text"]] for t in result["todos"][:20]]
        out.append(table(rows, ["TAG", "LOCATION", "NOTE"], s, max_width=width))
    elif result["todos"]:
        out.append("")
        out.append("  " + s(f"{len(result['todos'])} TODO/FIXME markers found (use --todos to list them)", DIM))

    if result["stale"]:
        out.append("")
        out.append(s("  STALE CODE", BOLD) + s("  (untouched for a year or more)", DIM))
        rows = [[t["path"], t["loc"], f"{t['last_change_days'] / 365:.1f}y"] for t in result["stale"][:6]]
        out.append(table(rows, ["FILE", "LOC", "AGE"], s, aligns=["l", "r", "r"], max_width=width))

    out.append("")
    return "\n".join(out)


def render_compare(diff: dict, style: Style) -> str:
    s = style
    out = [""]
    before, after = diff.get("health_before"), diff.get("health_after")
    if before is not None and after is not None:
        delta = after - before
        colour = GREEN if delta >= 0 else RED
        out.append("  " + s("HEALTH", BOLD) + f"  {before} → " +
                   s(f"{after}", score_color(after), BOLD) +
                   s(f"  ({delta:+d})", colour))
    out.append("  " + s(f"{diff['worsened']} files worse · {diff['improved']} files better", DIM))
    out.append("")
    rows = []
    for change in diff["changes"]:
        arrow = "▲" if change["delta"] > 0 else "▼"
        rows.append([change["path"], change["status"], f"{change['risk']:.0f}",
                     f"{arrow} {abs(change['delta']):.1f}"])
    out.append(table(rows, ["FILE", "STATUS", "RISK", "CHANGE"], s,
                     aligns=["l", "l", "r", "r"]))
    out.append("")
    return "\n".join(out)
