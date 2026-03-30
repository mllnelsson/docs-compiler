from pathlib import Path

from docs_compiler.config import PluginOutput

_SKILL_FILENAME = "SKILL.md"


def write_plugin_output(
    output: PluginOutput,
    resolved_docs: dict[str, str],
    target_dir: Path,
) -> None:
    base = target_dir / ".claude" / "plugins" / output.name

    for name in output.skills:
        skill_dir = base / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / _SKILL_FILENAME).write_text(resolved_docs[name])

    for name in output.agents:
        agents_dir = base / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / f"{name}.md").write_text(resolved_docs[name])
