from repolens import gitlog
from repolens.gitlog import _split_rename

from conftest import commit, git, write


def test_is_git_repo_and_root(sample_repo, tmp_path):
    assert gitlog.is_git_repo(sample_repo)
    assert not gitlog.is_git_repo(str(tmp_path))
    assert gitlog.repo_root(sample_repo).endswith("sample")
    assert gitlog.current_branch(sample_repo) == "main"


def test_read_commits_parses_numstat(sample_repo):
    commits = gitlog.read_commits(sample_repo)
    assert len(commits) == 10
    assert commits[0].subject == "add helper"
    assert all(c.sha for c in commits)
    touched = {p for c in commits for p, _, _ in c.files}
    assert "src/hot.py" in touched
    assert any(a > 0 for c in commits for _, a, _ in c.files)


def test_read_commits_window(sample_repo):
    assert len(gitlog.read_commits(sample_repo, max_commits=3)) == 3


def test_aggregate_history(sample_repo):
    hist = gitlog.aggregate_history(gitlog.read_commits(sample_repo))
    hot = hist["src/hot.py"]
    assert hot.commits == 9
    assert hot.churn > 0
    assert hot.main_author == "Alice"
    assert hot.ownership == 1.0
    assert hist["src/other.py"].main_author == "Bob"
    assert hot.first_seen <= hot.last_seen


def test_author_stats(sample_repo):
    stats = gitlog.author_stats(gitlog.read_commits(sample_repo))
    names = [s["author"] for s in stats]
    assert names[0] == "Alice"
    assert "Bob" in names
    assert stats[0]["commits"] == 9
    assert stats[0]["files"] >= 3


def test_coupling_detects_paired_files(sample_repo):
    pairs = gitlog.coupling(gitlog.read_commits(sample_repo), min_shared=3)
    found = {(p["a"], p["b"]) for p in pairs}
    assert ("src/config.py", "src/hot.py") in found or ("src/hot.py", "src/config.py") in found


def test_coupling_skips_bulk_commits(sample_repo):
    commits = gitlog.read_commits(sample_repo)
    assert gitlog.coupling(commits, min_shared=3, max_files_per_commit=1) == []


def test_split_rename_forms():
    assert _split_rename("a.py") == "a.py"
    assert _split_rename("old.py => new.py") == "new.py"
    assert _split_rename("src/{old => new}/file.py") == "src/new/file.py"


def test_list_tracked_files(sample_repo):
    files = gitlog.list_tracked_files(sample_repo)
    assert "src/hot.py" in files
    assert "README.md" in files


def test_binary_files_are_skipped(tiny_repo):
    with open(f"{tiny_repo}/logo.png", "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + bytes(range(256)))
    commit(tiny_repo, "add binary")
    commits = gitlog.read_commits(tiny_repo)
    assert all(p != "logo.png" for c in commits for p, _, _ in c.files)
