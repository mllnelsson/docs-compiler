import hashlib
import subprocess
from pathlib import Path

from docs_compiler.config import Config


def resolve_local(name: str, source_dir: Path) -> Path:
    for candidate in source_dir.rglob("*"):
        if candidate.is_file() and candidate.stem.lower() == name.lower():
            return candidate
    raise FileNotFoundError(
        f"Doc '{name}' not found in source directory: {source_dir}"
    )


def fetch_remote(git_url: str, path: str, cache_dir: Path) -> Path:
    url_hash = hashlib.sha256(git_url.encode()).hexdigest()[:16]
    repo_dir = cache_dir / url_hash

    if repo_dir.exists():
        result = subprocess.run(
            ["git", "pull"],
            cwd=repo_dir,
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"git pull failed for {git_url}:\n{result.stderr.decode()}"
            )
    else:
        result = subprocess.run(
            ["git", "clone", git_url, str(repo_dir)],
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"git clone failed for {git_url}:\n{result.stderr.decode()}"
            )

    return repo_dir / path


def resolve_doc(name: str, config: Config, source_dir: Path) -> Path:
    entry = config.docs.get(name)
    if entry is not None and entry.git is not None:
        cache_dir = Path.home() / ".cache" / "docs-compiler"
        file_path = entry.path or name
        return fetch_remote(entry.git, file_path, cache_dir)
    return resolve_local(name, source_dir)
