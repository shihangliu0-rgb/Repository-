"""RepoLens command line interface."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Optional, Tuple

from . import __version__
from .analyzer import AnalysisError, analyze, compare
from .gitlog import GitError
from .report import render_markdown, write_html, write_json, write_markdown
from .scan import DEFAULT_EXCLUDES
from .terminal import make_style, render, render_compare

EPILOG = """examples:
  repolens .                                  analyse the current repository
  repolens ~/code/app --since "12 months ago" limit the history window
  repolens . --html report.html --open        write an interactive HTML report
  repolens . --format json > repolens.json    machine readable output
  repolens . --format markdown                paste into a PR comment
  repolens . --fail-under 60                  fail CI when health drops
  repolens compare old.json new.json          diff two runs
  repolens serve . --port 8000                analyse and serve the report
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repolens",
        description="Git repository health, hotspot and risk analyzer.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"repolens {__version__}")
    sub = parser.add_subparsers(dest="command")

    def add_analysis_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("path", nargs="?", default=".", help="path to a git repository (default: .)")
        p.add_argument("--since", help='history window start, e.g. "6 months ago" or 2024-01-01')
        p.add_argument("--until", help="history window end")
        p.add_argument("--max-commits", type=int, help="cap the number of commits read")
        p.add_argument("--top", type=int, default=20, help="how many hotspots to report (default: 20)")
        p.add_argument("--exclude", action="append", default=[],
                       help="extra path fragment to ignore (repeatable)")
        p.add_argument("--include-generated", action="store_true",
                       help="do not skip lockfiles, minified and generated files")
        p.add_argument("--no-color", action="store_true", help="disable ANSI colours")

    analyse = sub.add_parser("analyze", aliases=["analyse"], help="analyse a repository")
    add_analysis_args(analyse)
    analyse.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    analyse.add_argument("--html", metavar="FILE", help="also write a self-contained HTML report")
    analyse.add_argument("--json", metavar="FILE", dest="json_out", help="also write the raw JSON result")
    analyse.add_argument("--markdown", metavar="FILE", dest="md_out", help="also write a Markdown summary")
    analyse.add_argument("--todos", action="store_true", help="list TODO/FIXME markers in the terminal")
    analyse.add_argument("--fail-under", type=float, metavar="SCORE",
                         help="exit with code 2 when the health score is below SCORE")
    analyse.add_argument("--open", dest="open_browser", action="store_true",
                         help="open the HTML report in a browser")

    serve = sub.add_parser("serve", help="analyse and serve the HTML report over HTTP")
    add_analysis_args(serve)
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--host", default="0.0.0.0")

    cmp_ = sub.add_parser("compare", help="compare two JSON results produced by --json")
    cmp_.add_argument("baseline")
    cmp_.add_argument("current")
    cmp_.add_argument("--format", choices=["text", "json"], default="text")
    cmp_.add_argument("--no-color", action="store_true")
    cmp_.add_argument("--fail-on-regression", action="store_true",
                      help="exit with code 2 when the health score decreased")
    return parser


def _run_analysis(args) -> dict:
    excludes: Tuple[str, ...] = tuple(DEFAULT_EXCLUDES) + tuple(args.exclude or [])
    return analyze(
        args.path,
        since=args.since,
        until=args.until,
        max_commits=args.max_commits,
        excludes=excludes,
        include_generated=args.include_generated,
        top=args.top,
    )


def cmd_analyze(args) -> int:
    result = _run_analysis(args)
    style = make_style(args.no_color)

    if args.format == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    elif args.format == "markdown":
        sys.stdout.write(render_markdown(result, top=args.top))
    else:
        sys.stdout.write(render(result, style, top=args.top, show_todos=args.todos) + "\n")

    written: List[str] = []
    if args.html:
        written.append(write_html(result, args.html))
    if args.json_out:
        written.append(write_json(result, args.json_out))
    if args.md_out:
        written.append(write_markdown(result, args.md_out, top=args.top))
    if written and args.format == "text":
        for path in written:
            print(f"  wrote {os.path.relpath(path)}")
        print()

    if args.open_browser and args.html:
        import webbrowser
        webbrowser.open("file://" + os.path.abspath(args.html))

    if args.fail_under is not None and result["summary"]["health_score"] < args.fail_under:
        print(f"health score {result['summary']['health_score']} is below the "
              f"required {args.fail_under:g}", file=sys.stderr)
        return 2
    return 0


def cmd_serve(args) -> int:
    import http.server
    import socketserver
    import tempfile

    result = _run_analysis(args)
    style = make_style(args.no_color)
    sys.stdout.write(render(result, style, top=args.top) + "\n")

    tmpdir = tempfile.mkdtemp(prefix="repolens-")
    write_html(result, os.path.join(tmpdir, "index.html"))
    write_json(result, os.path.join(tmpdir, "repolens.json"))

    handler_cls = http.server.SimpleHTTPRequestHandler

    class Handler(handler_cls):  # type: ignore[misc, valid-type]
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=tmpdir, **kw)

        def log_message(self, fmt, *a):  # keep the console readable
            sys.stderr.write("  %s - %s\n" % (self.address_string(), fmt % a))

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((args.host, args.port), Handler) as httpd:
        print(f"  serving RepoLens report on http://{args.host}:{args.port}  (ctrl-c to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  stopped")
    return 0


def cmd_compare(args) -> int:
    with open(args.baseline, encoding="utf-8") as fh:
        baseline = json.load(fh)
    with open(args.current, encoding="utf-8") as fh:
        current = json.load(fh)
    diff = compare(baseline, current)
    if args.format == "json":
        json.dump(diff, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_compare(diff, make_style(args.no_color)) + "\n")
    if args.fail_on_regression:
        before, after = diff.get("health_before"), diff.get("health_after")
        if before is not None and after is not None and after < before:
            print(f"health regressed: {before} → {after}", file=sys.stderr)
            return 2
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    # Allow `repolens .` and `repolens --html x.html` as shorthand for `analyze`.
    known = {"analyze", "analyse", "serve", "compare"}
    if not argv or (argv[0] not in known and not argv[0] in ("-h", "--help", "--version")):
        argv = ["analyze", *argv]

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        if args.command in ("analyze", "analyse"):
            return cmd_analyze(args)
        if args.command == "serve":
            return cmd_serve(args)
        if args.command == "compare":
            return cmd_compare(args)
    except (AnalysisError, GitError) as exc:
        print(f"repolens: {exc}", file=sys.stderr)
        return 1
    except BrokenPipeError:  # pragma: no cover - piping into head
        return 0
    except KeyboardInterrupt:  # pragma: no cover
        return 130
    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
