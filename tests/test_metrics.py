import time

from repolens import gitlog, metrics, scan
from repolens.model import FileHistory, FileScan


def _reports(repo):
    commits = gitlog.read_commits(repo)
    scans = scan.scan_paths(repo, gitlog.list_tracked_files(repo))
    history = gitlog.aggregate_history(commits)
    return commits, scans, history, metrics.build_file_reports(scans, history)


def test_hotspot_ranks_churny_complex_file_first(sample_repo):
    _, _, _, reports = _reports(sample_repo)
    top = reports[0]
    assert top.path == "src/hot.py"
    assert top.risk > 0
    stable = next(r for r in reports if r.path == "src/stable.py")
    assert top.hotspot > stable.hotspot


def test_reasons_are_explainable(sample_repo):
    _, _, _, reports = _reports(sample_repo)
    top = reports[0]
    assert any("knowledge concentrated" in r for r in top.reasons)


def test_tiny_repo_scores_stay_low(tiny_repo):
    _, _, _, reports = _reports(tiny_repo)
    assert reports, "expected at least one file"
    # A one-line README must never look like a serious hazard.
    assert max(r.risk for r in reports) < 25


def test_ownership_and_authors(sample_repo):
    _, _, _, reports = _reports(sample_repo)
    hot = next(r for r in reports if r.path == "src/hot.py")
    assert hot.ownership == 1.0
    assert hot.main_author == "Alice"
    other = next(r for r in reports if r.path == "src/other.py")
    assert other.main_author == "Bob"


def test_language_summary(sample_repo):
    _, scans, _, _ = _reports(sample_repo)
    langs = {l["language"]: l for l in metrics.language_summary(scans)}
    assert "Python" in langs
    assert langs["Python"]["files"] >= 4
    assert langs["Python"]["loc"] > 0


def test_commit_timeline_is_sorted(sample_repo):
    commits, _, _, _ = _reports(sample_repo)
    timeline = metrics.commit_timeline(commits)
    assert timeline == sorted(timeline, key=lambda t: t["month"])
    assert sum(t["commits"] for t in timeline) == len(commits)


def test_bus_factor():
    stats = [
        {"author": "A", "commits": 80}, {"author": "B", "commits": 15},
        {"author": "C", "commits": 5},
    ]
    bf = metrics.bus_factor(stats)
    assert bf["bus_factor"] == 1
    assert bf["top_author"] == "A"
    assert bf["authors"] == 3
    even = metrics.bus_factor([{"author": c, "commits": 10} for c in "ABCDE"])
    assert even["bus_factor"] == 3


def test_knowledge_risk(sample_repo):
    _, _, _, reports = _reports(sample_repo)
    risky = metrics.knowledge_risk(reports, min_commits=4, ownership_threshold=0.8)
    assert any(item["path"] == "src/hot.py" for item in risky)


def test_stale_files_detection():
    scans = {"old.py": FileScan(path="old.py", language="Python", loc=200, lines=220, complexity=30)}
    now = time.time()
    hist = {"old.py": FileHistory(path="old.py", commits=3, added=200, deleted=0,
                                  first_seen=int(now - 900 * 86400),
                                  last_seen=int(now - 800 * 86400),
                                  authors={"A": 3})}
    reports = metrics.build_file_reports(scans, hist, now=now)
    stale = metrics.stale_files(reports, days=365, min_loc=80)
    assert stale and stale[0]["path"] == "old.py"


def test_collect_todos_priority():
    scans = {
        "a.py": FileScan(path="a.py", language="Python", todos=[(3, "TODO", "later")]),
        "b.py": FileScan(path="b.py", language="Python", todos=[(9, "FIXME", "now")]),
    }
    todos = metrics.collect_todos(scans)
    assert todos[0]["tag"] == "FIXME"
    assert len(todos) == 2


def test_health_score_bounds(sample_repo):
    _, scans, _, reports = _reports(sample_repo)
    summary = {"bus_factor": metrics.bus_factor(
        gitlog.author_stats(gitlog.read_commits(sample_repo)))}
    score, dims = metrics.health_score(reports, summary)
    assert 0 <= score <= 100
    assert len(dims) == 5
    assert all(0 <= d["score"] <= 100 for d in dims)
    assert all(d["detail"] for d in dims)


def test_directory_summary(sample_repo):
    _, _, _, reports = _reports(sample_repo)
    dirs = {d["directory"] for d in metrics.directory_summary(reports)}
    assert any(d.startswith("src") for d in dirs)


def test_norm_is_monotonic():
    assert metrics._norm(0, 100) == 0
    assert metrics._norm(10, 100) < metrics._norm(50, 100) < metrics._norm(100, 100)
    assert metrics._norm(500, 100) == 1.0
    assert metrics._norm(5, 0) == 0.0
