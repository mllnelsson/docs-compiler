from pathlib import Path

import pytest

from docs_compiler.config import ClaudeOutput, Config, DocEntry, PluginOutput, TocOutput, load_config, write_config
from docs_compiler.errors import ConfigError


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "docs-compiler.yaml"
    p.write_text(content)
    return p


def test_minimal_valid_config(tmp_path):
    path = _write(tmp_path, """
outputs:
  - format: claude
    include: [python-guidelines]
""")
    config = load_config(path)
    assert isinstance(config, Config)
    assert config.docs == {}
    assert len(config.outputs) == 1
    assert isinstance(config.outputs[0], ClaudeOutput)
    assert config.outputs[0].include == ["python-guidelines"]


def test_config_with_remote_docs(tmp_path):
    path = _write(tmp_path, """
docs:
  commit-skill:
    git: https://github.com/user/shared-skills
    path: documentation/commit-skill.md

outputs:
  - format: plugin
    name: my-plugin
    skills: [python-guidelines, commit-skill]
    agents: [backlog-agent]
""")
    config = load_config(path)
    assert "commit-skill" in config.docs
    entry = config.docs["commit-skill"]
    assert isinstance(entry, DocEntry)
    assert entry.git == "https://github.com/user/shared-skills"
    assert entry.path == "documentation/commit-skill.md"
    assert isinstance(config.outputs[0], PluginOutput)
    assert config.outputs[0].name == "my-plugin"


def test_toc_output_parses(tmp_path):
    path = _write(tmp_path, """
outputs:
  - format: toc
""")
    config = load_config(path)
    assert isinstance(config.outputs[0], TocOutput)


def test_missing_outputs_raises(tmp_path):
    path = _write(tmp_path, """
docs:
  some-doc:
    path: foo.md
""")
    with pytest.raises(ConfigError, match="outputs"):
        load_config(path)


def test_unknown_format_raises(tmp_path):
    path = _write(tmp_path, """
outputs:
  - format: unknown
    include: []
""")
    with pytest.raises(ConfigError):
        load_config(path)


def test_missing_file_raises(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nonexistent.yaml")


def test_round_trip(tmp_path):
    original = Config(
        docs={"commit-skill": DocEntry(git="https://github.com/user/skills", path="docs/commit.md")},
        outputs=[
            ClaudeOutput(format="claude", include=["python-guidelines", "commit-skill"]),
            PluginOutput(format="plugin", name="my-plugin", skills=["python-guidelines"], agents=["backlog-agent"]),
        ],
    )
    path = tmp_path / "docs-compiler.yaml"
    write_config(original, path)
    loaded = load_config(path)
    assert loaded == original


def test_bootstrap_write(tmp_path):
    path = tmp_path / "new-dir" / "docs-compiler.yaml"
    path.parent.mkdir()
    config = Config(outputs=[ClaudeOutput(format="claude", include=["python-guidelines"])])
    write_config(config, path)
    assert path.exists()
    loaded = load_config(path)
    assert loaded == config
