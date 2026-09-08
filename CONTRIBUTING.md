# Contributing

Thanks for taking a look. RepoLens is deliberately small and dependency-free — please
keep it that way.

## Ground rules

1. **No runtime dependencies.** The standard library and `git` only. Test-time
   dependencies (`pytest`) are fine.
2. **Every score must be explainable.** If you add a penalty or dimension, it must produce
   a human-readable reason string that appears in the terminal, Markdown and HTML output.
3. **Heuristics must degrade gracefully.** RepoLens runs against repositories in languages
   it has never seen; unknown files should be counted, not crash the run.
4. **Tests use real git.** `tests/conftest.py` builds throw-away repositories with real
   commits, authors and dates. No mocking of `git`.

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest -q
```

Dogfood your change before opening a PR:

```bash
.venv/bin/python -m repolens . --no-color
.venv/bin/python -m repolens . --html /tmp/report.html && open /tmp/report.html
```

## Layout

| File | Responsibility |
| --- | --- |
| `src/repolens/gitlog.py` | Everything that shells out to `git`: log parsing, aggregation, coupling, author stats |
| `src/repolens/scan.py` | Language detection and static line/complexity/TODO scanning |
| `src/repolens/metrics.py` | Scoring: hotspot, risk, health dimensions, knowledge risk, stale code |
| `src/repolens/analyzer.py` | Pipeline that produces the versioned JSON document, plus `compare` |
| `src/repolens/terminal.py` | ANSI rendering (tables, bars, colours) |
| `src/repolens/report.py` | HTML / JSON / Markdown writers |
| `src/repolens/templates/report.html` | The offline dashboard (vanilla JS + inline SVG) |
| `src/repolens/cli.py` | Argument parsing and command wiring |

## Changing the JSON schema

The document carries `"schema": "repolens/1"`. Additive changes are fine; anything that
removes or renames a field must bump the schema string and be noted in `CHANGELOG.md`,
because `repolens compare` reads stored runs from earlier versions.

## Adding a language

Add an entry to `LANGUAGES` in `scan.py` (extension → name, line-comment prefixes, block
comment delimiters), add it to `CODE_LANGUAGES` if it should be complexity-ranked, and add
a weight to `LANGUAGE_WEIGHT` in `metrics.py` if it is documentation or configuration.
