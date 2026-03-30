from pathlib import Path

from docs_compiler.config import ClaudeOutput

_SKILL_FILENAME = "SKILL.md"


def write_claude_output(
    output: ClaudeOutput,
    resolved_docs: dict[str, str],
    target_dir: Path,
) -> None:
    for name in output.include:
        skill_dir = target_dir / ".claude" / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / _SKILL_FILENAME).write_text(resolved_docs[name])
