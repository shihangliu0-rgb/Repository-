# GitHub Actions templates

These workflows are shipped as templates rather than live workflows so the repository can
be pushed by tooling without `workflows` scope. Enable them with one command:

```bash
mkdir -p .github/workflows && cp ci/github/*.yml .github/workflows/
git add .github/workflows && git commit -m "ci: enable GitHub Actions"
```

| File | What it does |
| --- | --- |
| `ci.yml` | Runs the test suite on Python 3.9–3.12 and dogfoods RepoLens on this repository. |
| `repolens.yml` | On every pull request: posts (and updates) a Markdown health report as a PR comment, uploads the interactive HTML dashboard as a build artifact, and optionally fails the build via `--fail-under`. |

`repolens.yml` is designed to be copied into **any** repository, not just this one.
It only needs `fetch-depth: 0` on the checkout so RepoLens can read the full history.
