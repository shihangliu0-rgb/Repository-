# Examples

## `flask-report.html`

A real RepoLens dashboard: the [pallets/flask](https://github.com/pallets/flask)
repository (3,824 commits, 858 authors, 231 files) rendered into a single offline HTML
file. Download it and open it in any browser — there are no external assets.

Regenerate it yourself:

```bash
git clone https://github.com/pallets/flask /tmp/flask
python -m repolens /tmp/flask --html examples/flask-report.html
```

## Analysing several repositories at once

```bash
for repo in ~/code/*/; do
  name=$(basename "$repo")
  python -m repolens "$repo" --format json > "/tmp/$name.json" 2>/dev/null \
    && python - <<PY
import json
d = json.load(open("/tmp/$name.json"))
s = d["summary"]
print(f"{s['repository']:<25} health {s['health_score']:>3}  "
      f"{s['commits']:>6} commits  {s['loc']:>8,} LOC  bus factor {s['bus_factor']['bus_factor']}")
PY
done
```

## Tracking a repository over time

```bash
python -m repolens . --json runs/$(date +%F).json --no-color > /dev/null
python -m repolens compare runs/2026-08-01.json runs/$(date +%F).json
```
