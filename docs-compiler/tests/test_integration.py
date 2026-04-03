from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from docs_compiler.config import load_config
from docs_compiler.main import app

runner = CliRunner()


def test_install(tmp_path: Path) -> None:
    source_dir = tmp_path / "docs"
    source_dir.mkdir()
    (source_dir / "guide.md").write_text("# Guide\nHello world")

    config_path = tmp_path / "docs-compiler.yaml"
    config_path.write_text("outputs:\n- format: claude\n  include:\n  - guide\n")

    result = runner.invoke(app, [
        "install",
        "--config", str(config_path),
        "--source", str(source_dir),
        "--scope", "local",
        "--target", str(tmp_path),
    ])

    assert result.exit_code == 0
    skill_file = tmp_path / ".claude" / "skills" / "guide" / "SKILL.md"
    assert skill_file.exists()
    assert skill_file.read_text() == "# Guide\nHello world"


def test_add_local_no_config(tmp_path: Path) -> None:
    source_dir = tmp_path / "docs"
    source_dir.mkdir()
    (source_dir / "intro.md").write_text("# Intro")

    config_path = tmp_path / "docs-compiler.yaml"

    result = runner.invoke(app, [
        "add", "intro",
        "--config", str(config_path),
        "--source", str(source_dir),
        "--scope", "local",
        "--target", str(tmp_path),
    ])

    assert result.exit_code == 0
    assert config_path.exists()
    config = load_config(config_path)
    assert "intro" in config.outputs[0].include

    assert (tmp_path / ".claude" / "skills" / "intro" / "SKILL.md").exists()


def test_add_remote_mocked(tmp_path: Path) -> None:
    remote_doc = tmp_path / "remote_doc.md"
    remote_doc.write_text("# Remote Doc")

    config_path = tmp_path / "docs-compiler.yaml"

    with patch("docs_compiler.resolver.fetch_remote", return_value=remote_doc):
        result = runner.invoke(app, [
            "add", "remote-skill",
            "--from", "https://github.com/example/repo",
            "--path", "docs/skill.md",
            "--config", str(config_path),
            "--source", str(tmp_path / "does-not-exist"),
            "--scope", "local",
            "--target", str(tmp_path),
        ])

    assert result.exit_code == 0
    config = load_config(config_path)
    assert "remote-skill" in config.docs
    assert config.docs["remote-skill"].git == "https://github.com/example/repo"

    skill_file = tmp_path / ".claude" / "skills" / "remote-skill" / "SKILL.md"
    assert skill_file.exists()
    assert skill_file.read_text() == "# Remote Doc"


def test_add_to_existing_config(tmp_path: Path) -> None:
    source_dir = tmp_path / "docs"
    source_dir.mkdir()
    (source_dir / "existing.md").write_text("# Existing")
    (source_dir / "new.md").write_text("# New")

    config_path = tmp_path / "docs-compiler.yaml"
    config_path.write_text("outputs:\n- format: claude\n  include:\n  - existing\n")

    result = runner.invoke(app, [
        "add", "new",
        "--config", str(config_path),
        "--source", str(source_dir),
        "--scope", "local",
        "--target", str(tmp_path),
    ])

    assert result.exit_code == 0
    config = load_config(config_path)
    assert "existing" in config.outputs[0].include
    assert "new" in config.outputs[0].include
