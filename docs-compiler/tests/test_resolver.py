from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from docs_compiler.config import Config, DocEntry, ClaudeOutput
from docs_compiler.errors import DocNotFoundError, GitError
from docs_compiler.resolver import fetch_remote, resolve_doc, resolve_local


# --- resolve_local ---

def test_resolve_local_finds_file(tmp_path):
    subdir = tmp_path / "sub"
    subdir.mkdir()
    doc = subdir / "python-guidelines.md"
    doc.write_text("content")

    result = resolve_local("python-guidelines", tmp_path)
    assert result == doc


def test_resolve_local_case_insensitive(tmp_path):
    doc = tmp_path / "Python-Guidelines.md"
    doc.write_text("content")

    result = resolve_local("python-guidelines", tmp_path)
    assert result == doc


def test_resolve_local_raises_when_missing(tmp_path):
    with pytest.raises(DocNotFoundError, match="python-guidelines"):
        resolve_local("python-guidelines", tmp_path)


# --- fetch_remote ---

def _make_completed(returncode=0, stderr=b""):
    mock = MagicMock()
    mock.returncode = returncode
    mock.stderr = stderr
    return mock


def test_fetch_remote_clones_when_not_cached(tmp_path):
    with patch("docs_compiler.resolver.subprocess.run", return_value=_make_completed()) as mock_run:
        result = fetch_remote("https://github.com/user/repo", "docs/file.md", tmp_path)

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[0] == "git"
    assert args[1] == "clone"
    assert "https://github.com/user/repo" in args
    assert result.name == "file.md"


def test_fetch_remote_pulls_when_cached(tmp_path):
    import hashlib
    url = "https://github.com/user/repo"
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    repo_dir = tmp_path / url_hash
    repo_dir.mkdir()

    with patch("docs_compiler.resolver.subprocess.run", return_value=_make_completed()) as mock_run:
        result = fetch_remote(url, "docs/file.md", tmp_path)

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args == ["git", "pull"]
    assert result == repo_dir / "docs/file.md"


def test_fetch_remote_raises_on_clone_failure(tmp_path):
    with patch("docs_compiler.resolver.subprocess.run", return_value=_make_completed(1, b"error")):
        with pytest.raises(GitError, match="git clone failed"):
            fetch_remote("https://github.com/user/repo", "docs/file.md", tmp_path)


def test_fetch_remote_raises_on_pull_failure(tmp_path):
    import hashlib
    url = "https://github.com/user/repo"
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    repo_dir = tmp_path / url_hash
    repo_dir.mkdir()

    with patch("docs_compiler.resolver.subprocess.run", return_value=_make_completed(1, b"error")):
        with pytest.raises(GitError, match="git pull failed"):
            fetch_remote(url, "docs/file.md", tmp_path)


# --- resolve_doc ---

def _config_with_remote(name: str, git_url: str, path: str) -> Config:
    return Config(
        docs={name: DocEntry(git=git_url, path=path)},
        outputs=[ClaudeOutput(format="claude", include=[name])],
    )


def _config_empty() -> Config:
    return Config(outputs=[ClaudeOutput(format="claude", include=[])])


def test_resolve_doc_uses_local_when_no_git(tmp_path):
    doc = tmp_path / "my-doc.md"
    doc.write_text("content")

    result = resolve_doc("my-doc", _config_empty(), tmp_path)
    assert result == doc


def test_resolve_doc_uses_remote_when_git_entry(tmp_path):
    config = _config_with_remote("commit-skill", "https://github.com/user/skills", "docs/commit-skill.md")

    with patch("docs_compiler.resolver.fetch_remote", return_value=tmp_path / "docs/commit-skill.md") as mock_fetch:
        result = resolve_doc("commit-skill", config, tmp_path)

    mock_fetch.assert_called_once()
    call_args = mock_fetch.call_args[0]
    assert call_args[0] == "https://github.com/user/skills"
    assert call_args[1] == "docs/commit-skill.md"
