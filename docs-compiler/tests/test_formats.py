from pathlib import Path

from docs_compiler.config import ClaudeOutput, PluginOutput
from docs_compiler.formats.claude import write_claude_output
from docs_compiler.formats.plugin import write_plugin_output


def test_claude_output_creates_skill_file(tmp_path: Path) -> None:
    output = ClaudeOutput(format="claude", include=["python-guidelines"])
    resolved = {"python-guidelines": "# Python Guidelines\nContent here."}

    write_claude_output(output, resolved, tmp_path)

    skill_file = tmp_path / ".claude" / "skills" / "python-guidelines" / "SKILL.md"
    assert skill_file.exists()
    assert skill_file.read_text() == resolved["python-guidelines"]


def test_claude_output_multiple_docs(tmp_path: Path) -> None:
    output = ClaudeOutput(format="claude", include=["doc-a", "doc-b"])
    resolved = {"doc-a": "Content A", "doc-b": "Content B"}

    write_claude_output(output, resolved, tmp_path)

    assert (tmp_path / ".claude" / "skills" / "doc-a" / "SKILL.md").read_text() == "Content A"
    assert (tmp_path / ".claude" / "skills" / "doc-b" / "SKILL.md").read_text() == "Content B"


def test_plugin_output_creates_skill_file(tmp_path: Path) -> None:
    output = PluginOutput(format="plugin", name="my-plugin", skills=["uv"], agents=[])
    resolved = {"uv": "# uv skill content"}

    write_plugin_output(output, resolved, tmp_path)

    skill_file = tmp_path / ".claude" / "plugins" / "my-plugin" / "skills" / "uv" / "SKILL.md"
    assert skill_file.exists()
    assert skill_file.read_text() == resolved["uv"]


def test_plugin_output_creates_agent_file(tmp_path: Path) -> None:
    output = PluginOutput(format="plugin", name="my-plugin", skills=[], agents=["researcher"])
    resolved = {"researcher": "# Researcher agent"}

    write_plugin_output(output, resolved, tmp_path)

    agent_file = tmp_path / ".claude" / "plugins" / "my-plugin" / "agents" / "researcher.md"
    assert agent_file.exists()
    assert agent_file.read_text() == resolved["researcher"]


def test_plugin_output_creates_skills_and_agents(tmp_path: Path) -> None:
    output = PluginOutput(
        format="plugin",
        name="full-plugin",
        skills=["skill-a", "skill-b"],
        agents=["agent-x"],
    )
    resolved = {
        "skill-a": "Skill A content",
        "skill-b": "Skill B content",
        "agent-x": "Agent X content",
    }

    write_plugin_output(output, resolved, tmp_path)

    base = tmp_path / ".claude" / "plugins" / "full-plugin"
    assert (base / "skills" / "skill-a" / "SKILL.md").read_text() == "Skill A content"
    assert (base / "skills" / "skill-b" / "SKILL.md").read_text() == "Skill B content"
    assert (base / "agents" / "agent-x.md").read_text() == "Agent X content"
