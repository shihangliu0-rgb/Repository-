# RepoLens

**Find the code that is actually hurting you.**

RepoLens mines your Git history, cross-references it with a static scan of the working
tree, and tells you which files are *complex* **and** *changing constantly* — the
combination where defects concentrate. It has **zero runtime dependencies** (Python 3.9+
and `git` are all you need) and produces a terminal report, machine-readable JSON,
a Markdown summary for pull requests, and a self-contained interactive HTML dashboard
that works offline.

```
╭──────────────────────────────────────────────────────────────────────────╮
│ RepoLens · flask (main)                                                  │
╰──────────────────────────────────────────────────────────────────────────╯

  HEALTH SCORE 73/100   ██████████████████████········
    Hotspot control        43  ███████·········  28.3% of code lives in high-risk files
    Knowledge spread       99  ████████████████  3 of 858 authors produce 50% of commits
    Documentation          40  ██████··········  average comment ratio 6.0%
    File size discipline   81  █████████████···  11 files over 400 LOC
    Test coverage proxy   100  ████████████████  27.5% of LOC in test/spec files

  3824 commits · 858 authors · 231 files · 24,551 LOC · bus factor 3 · 2010-04-06 → 2026-08-16

  HOTSPOTS  (complexity × change frequency — fix these first)
  FILE                      RISK   HOT    LOC   COMMITS   AUTHORS   LANG
  ───────────────────────   ────   ───   ────   ───────   ───────   ──────
  src/flask/app.py           100    93    687       136        31   Python
  src/flask/cli.py           100    89    684        67        18   Python
  tests/test_basic.py        100    88   1438       135        49   Python
  tests/test_blueprints.py    98    82    776        59        17   Python
  src/flask/sansio/app.py     85    77    347        20         6   Python

  WHY THE TOP FILES ARE RISKY
    src/flask/app.py
      • large and frequently modified
      • deep nesting (indent level 6)
      • long file (687 LOC)
      • still churning in the last 30 days
```

## Why this exists

Static linters tell you what is wrong *in a file*. They cannot tell you **which file to
care about**. A 2,000-line module nobody has touched in three years is not your problem;
a 400-line module that eleven people rewrote last quarter is. RepoLens ranks files by the
product of size/complexity and change frequency (the "hotspot" idea from
*Your Code as a Crime Scene*), then layers on knowledge concentration, temporal coupling
and staleness so you get a prioritised, explainable list instead of a wall of warnings.

Every number comes with a plain-English reason. No score is a black box.

## Install

```bash
pip install -e .          # from a clone
# or run without installing:
python -m repolens /path/to/repo
```

Requires Python 3.9+ and `git` on PATH. Nothing else — no numpy, no pandas, no Node.

## Usage

```bash
repolens                                   # analyse the current repository
repolens ~/code/app --since "12 months ago"
repolens . --top 30 --todos                # more hotspots + list TODO/FIXME markers
repolens . --html report.html --open       # interactive offline dashboard
repolens . --format json > repolens.json   # machine readable
repolens . --format markdown               # paste into a PR
repolens . --exclude vendor/ --exclude "*.generated.ts"
repolens serve . --port 8000               # analyse and serve the dashboard
repolens compare before.json after.json    # trend between two runs
```

### The HTML dashboard

`--html report.html` writes **one single file** — no CDN, no external assets, no network
access at runtime. Open it from disk, email it, attach it to a CI build. It contains:

| Panel | What it answers |
| --- | --- |
| Health gauge + 5 dimensions | How healthy is this repo, and *why* that number? |
| Hotspot map (scatter) | Which files are both complex and churning? |
| Commit activity | Is this project accelerating or decaying? |
| Sortable file table | Give me the raw numbers, filtered by path or language. |
| Why the top files are risky | Explainable reasons per file. |
| Quick wins | High risk but still small enough to refactor this sprint. |
| Temporal coupling | Which files always change together (hidden dependencies)? |
| Knowledge risk | Which files would hurt if one person left? |
| TODO / FIXME | The debt people already admitted to in comments. |
| Stale code | Untouched for a year — deletion candidates. |

A pre-generated example (analysis of the Flask repository) lives in
[`examples/flask-report.html`](examples/flask-report.html) — download and open it in a
browser.

## How the scores work

**Hotspot (0–100)** — geometric mean of a *size* signal (branch complexity, LOC) and a
*change* signal (commits, churn). Both are log-normalised twice: once against the rest of
the repository (relative) and once against fixed reference points (absolute), so a
two-file toy project does not report its README as a catastrophe. Non-code files
(Markdown, RST, lockfiles) are damped because changelogs churn without carrying defect risk.

**Risk (0–100)** — the hotspot score plus explainable penalties:

| Penalty | Trigger |
| --- | --- |
| knowledge concentration | one author owns ≥80% of commits on a file with ≥5 commits |
| deep nesting | indentation level ≥6 |
| long file | ≥400 LOC |
| undocumented | ≥120 LOC with <3% comment lines |
| active churn | ≥8 commits, last touched within 30 days |
| admitted debt | ≥3 TODO/FIXME markers |
| high branch density | branch keywords per LOC > 0.35 |

**Health score (0–100)** — the mean of five independently explainable dimensions:
hotspot control, knowledge spread, documentation, file size discipline, and a test
coverage *proxy* (share of LOC in test/spec files — it does not run your tests).

These are heuristics for **prioritisation**, not certification. They are designed to be
compared against the same repository over time, and to survive any language without a
per-language parser.

## Use it in CI

Fail the build when health regresses, and post the report on the pull request:

```yaml
- run: pip install -e .
- run: repolens . --json repolens.json --markdown report.md --fail-under 60
- run: repolens compare main.json repolens.json --fail-on-regression
```

Ready-made GitHub Actions workflows live in [`ci/github/`](ci/github/) — one runs the test
matrix, the other comments the Markdown report on every PR and uploads the HTML dashboard
as an artifact. Enable them with:

```bash
mkdir -p .github/workflows && cp ci/github/*.yml .github/workflows/
```

Exit codes: `0` success · `1` usage/analysis error · `2` threshold or regression failure.

## Python API

```python
from repolens import analyze, compare
from repolens.report import render_html, render_markdown

result = analyze("~/code/app", since="6 months ago", top=25)
print(result["summary"]["health_score"])
for f in result["hotspots"][:5]:
    print(f["path"], f["risk"], f["reasons"])

open("report.html", "w").write(render_html(result))
```

The JSON document is stable and versioned (`"schema": "repolens/1"`) so you can store runs
and diff them later with `repolens compare`.

## Performance

Single pass over `git log --numstat` plus one read of each tracked text file.
Binary blobs, lockfiles, minified bundles, `node_modules/`, `vendor/`, `dist/` and friends
are skipped by default.

| Repository | History | Time |
| --- | --- | --- |
| psf/requests | 4,882 commits | ~0.8 s |
| pallets/flask | 3,824 commits | ~1.0 s |

Use `--since` or `--max-commits` on repositories with six-figure commit counts.

## Development

```bash
python -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest        # 51 tests, no network required
```

Tests build throw-away Git repositories on the fly, so they exercise real `git` plumbing
rather than mocks. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
