# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] — 2026-09-08

First release.

### Added
- Git history mining: per-file commits, churn, authors, first/last touch, rename tracking.
- Static scan for 50+ languages: LOC, comments (including Python docstrings), blank lines,
  branch-keyword complexity, nesting depth, TODO/FIXME markers.
- Hotspot score combining relative and absolute size/change signals, damped for non-code
  files and for insignificantly small files.
- Explainable risk score with per-file reason strings.
- Repository health score across five independently explained dimensions.
- Temporal coupling, knowledge-risk (bus factor) analysis, stale-code detection and
  "quick wins" ranking.
- Outputs: ANSI terminal report, versioned JSON (`repolens/1`), Markdown summary for pull
  requests, and a self-contained offline HTML dashboard with SVG charts.
- Commands: `analyze` (default), `serve`, `compare`.
- CI-friendly exit codes: `--fail-under` and `--fail-on-regression`.
- 51 tests running against real, throw-away git repositories.
