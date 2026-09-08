import json
import os

import pytest

from repolens import analyzer
from repolens.cli import main
from repolens.report import render_html, render_markdown


def test_analyze_document_shape(sample_repo):
    result = analyzer.analyze(sample_repo)
    assert result["schema"] == "repolens/1"
    for key in ("summary", "hotspots", "files", "languages", "authors", "timeline",
                "directories", "coupling", "knowledge_risk", "stale", "todos", "quick_wins"):
        assert key in result
    s = result["summary"]
    assert s["commits"] == 10
    assert s["authors"] == 2
    assert s["branch"] == "main"
    assert 0 <= s["health_score"] <= 100
    assert s["loc"] > 0


def test_analyze_rejects_non_repo(tmp_path):
    with pytest.raises(analyzer.AnalysisError):
        analyzer.analyze(str(tmp_path))


def test_analyze_respects_excludes(sample_repo):
    full = analyzer.analyze(sample_repo)
    filtered = analyzer.analyze(sample_repo, excludes=("tests/",))
    assert filtered["summary"]["analysed_files"] < full["summary"]["analysed_files"]
    assert all(not f["path"].startswith("tests/") for f in filtered["files"])


def test_analyze_since_window(sample_repo):
    limited = analyzer.analyze(sample_repo, max_commits=2)
    assert limited["summary"]["commits"] == 2


def test_compare_detects_regression(sample_repo):
    before = analyzer.analyze(sample_repo)
    after = json.loads(json.dumps(before))
    after["files"][0]["risk"] += 20
    after["summary"]["health_score"] -= 10
    diff = analyzer.compare(before, after)
    assert diff["worsened"] >= 1
    assert diff["health_after"] < diff["health_before"]
    assert diff["changes"][0]["delta"] == 20


def test_render_html_is_self_contained(sample_repo):
    html = render_html(analyzer.analyze(sample_repo))
    assert html.startswith("<!DOCTYPE html>")
    assert "src/hot.py" in html
    assert "http://" not in html.replace("http://www.w3.org", "")  # no external assets
    assert "<script src=" not in html
    payload = html.split('id="repolens-data" type="application/json">')[1].split("</script>")[0]
    data = json.loads(payload.replace("<\\/", "</"))
    assert data["summary"]["repository"] == "sample"


def test_render_markdown(sample_repo):
    md = render_markdown(analyzer.analyze(sample_repo))
    assert md.startswith("## RepoLens report")
    assert "| Dimension | Score | Detail |" in md
    assert "src/hot.py" in md


def test_cli_text_output(sample_repo, capsys):
    assert main([sample_repo, "--no-color"]) == 0
    out = capsys.readouterr().out
    assert "HEALTH SCORE" in out
    assert "HOTSPOTS" in out
    assert "src/hot.py" in out


def test_cli_json_output(sample_repo, capsys):
    assert main(["analyze", sample_repo, "--format", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["summary"]["commits"] == 10


def test_cli_markdown_output(sample_repo, capsys):
    assert main(["analyze", sample_repo, "--format", "markdown"]) == 0
    assert "## RepoLens report" in capsys.readouterr().out


def test_cli_writes_files(sample_repo, tmp_path, capsys):
    html = tmp_path / "out" / "report.html"
    js = tmp_path / "out" / "report.json"
    md = tmp_path / "out" / "report.md"
    code = main([sample_repo, "--html", str(html), "--json", str(js),
                 "--markdown", str(md), "--no-color"])
    capsys.readouterr()
    assert code == 0
    assert html.exists() and js.exists() and md.exists()
    assert json.loads(js.read_text(encoding="utf-8"))["schema"] == "repolens/1"


def test_cli_fail_under(sample_repo, capsys):
    assert main([sample_repo, "--fail-under", "0", "--no-color"]) == 0
    assert main([sample_repo, "--fail-under", "101", "--no-color"]) == 2


def test_cli_todos_flag(sample_repo, capsys):
    main([sample_repo, "--todos", "--no-color"])
    out = capsys.readouterr().out
    assert "TODO / FIXME MARKERS" in out


def test_cli_compare(sample_repo, tmp_path, capsys):
    base = tmp_path / "base.json"
    cur = tmp_path / "cur.json"
    main([sample_repo, "--json", str(base), "--no-color"])
    data = json.loads(base.read_text(encoding="utf-8"))
    data["summary"]["health_score"] -= 5
    data["files"][0]["risk"] += 9
    cur.write_text(json.dumps(data), encoding="utf-8")
    capsys.readouterr()

    assert main(["compare", str(base), str(cur), "--no-color"]) == 0
    assert "HEALTH" in capsys.readouterr().out
    assert main(["compare", str(base), str(cur), "--fail-on-regression", "--no-color"]) == 2


def test_cli_errors_on_non_repo(tmp_path, capsys):
    assert main([str(tmp_path), "--no-color"]) == 1
    assert "not a git repository" in capsys.readouterr().err


def test_cli_help(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "repository health" in capsys.readouterr().out.lower()
