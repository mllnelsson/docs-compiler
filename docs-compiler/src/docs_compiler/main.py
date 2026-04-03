import os
from enum import StrEnum, auto
from pathlib import Path
from typing import Annotated

import typer

from docs_compiler.config import (
    ClaudeOutput,
    Config,
    DocEntry,
    Output,
    PluginOutput,
    TocOutput,
    load_config,
    write_config,
)
from docs_compiler.errors import ConfigError, DocsCompilerError
from docs_compiler.formats.claude import write_claude_output
from docs_compiler.formats.plugin import write_plugin_output
from docs_compiler.references import resolve_references
from docs_compiler.resolver import resolve_doc

DEFAULT_CONFIG = "docs-compiler.yaml"
SOURCE_ENV_VAR = "DOCS_COMPILER_SOURCE"

app = typer.Typer()


class Scope(StrEnum):
    LOCAL = auto()
    USER = auto()


def _resolve_target_dir(scope: Scope, target: str | None) -> Path:
    if target is not None:
        return Path(target)
    match scope:
        case Scope.LOCAL:
            return Path(".")
        case Scope.USER:
            return Path.home()


def _resolve_source_dir(source_flag: str | None) -> Path:
    if source_flag:
        return Path(source_flag)
    env = os.environ.get(SOURCE_ENV_VAR)
    if env:
        return Path(env)
    return Path(__file__).parent.parent / "documentation"


def _collect_doc_names(config: Config) -> set[str]:
    names: set[str] = set()
    for output in config.outputs:
        match output:
            case ClaudeOutput():
                names.update(output.include)
            case PluginOutput():
                names.update(output.skills)
                names.update(output.agents)
            case TocOutput():
                pass
    return names


def _resolve_all_docs(
    names: set[str], config: Config, source_dir: Path
) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for name in names:
        path = resolve_doc(name, config, source_dir)
        content = path.read_text()
        resolved[name] = resolve_references(content, name, config, source_dir)
    return resolved


def _run_install(config: Config, source_dir: Path, target_dir: Path) -> list[str]:
    names = _collect_doc_names(config)
    resolved_docs = _resolve_all_docs(names, config, source_dir)

    written: list[str] = []
    for output in config.outputs:
        match output:
            case ClaudeOutput():
                write_claude_output(output, resolved_docs, target_dir)
                written.extend(
                    str(target_dir / ".claude" / "skills" / name / "SKILL.md")
                    for name in output.include
                )
            case PluginOutput():
                write_plugin_output(output, resolved_docs, target_dir)
                written.extend(
                    str(target_dir / ".claude" / "plugins" / output.name / "skills" / name / "SKILL.md")
                    for name in output.skills
                )
                written.extend(
                    str(target_dir / ".claude" / "plugins" / output.name / "agents" / f"{name}.md")
                    for name in output.agents
                )
            case TocOutput():
                typer.echo("ToC format not yet implemented", err=True)

    return written


def _bootstrap_config() -> Config:
    return Config(
        docs={},
        outputs=[ClaudeOutput(format="claude", include=[])],
    )


def _select_output(config: Config, output_name: str | None) -> Output:
    if output_name is None:
        return config.outputs[0]
    for output in config.outputs:
        if isinstance(output, PluginOutput) and output.name == output_name:
            return output
    raise ConfigError(f"Output '{output_name}' not found in config")


def _add_doc_to_output(output: Output, name: str) -> None:
    match output:
        case ClaudeOutput():
            if name not in output.include:
                output.include.append(name)
        case PluginOutput():
            if name not in output.skills:
                output.skills.append(name)
        case TocOutput():
            raise ConfigError("Cannot add docs to a 'toc' output")


@app.command()
def install(
    config: Annotated[str, typer.Option(metavar="PATH")] = DEFAULT_CONFIG,
    source: Annotated[str | None, typer.Option(metavar="PATH")] = None,
    scope: Annotated[Scope, typer.Option()] = Scope.LOCAL,
    target: Annotated[str | None, typer.Option(metavar="PATH")] = None,
) -> None:
    """Resolve docs and write outputs."""
    try:
        config_path = Path(config)
        source_dir = _resolve_source_dir(source)
        target_dir = _resolve_target_dir(scope, target)

        loaded_config = load_config(config_path)
        written = _run_install(loaded_config, source_dir, target_dir)

        for path in written:
            typer.echo(f"  wrote {path}")
        typer.echo(f"Installed {len(written)} file(s).")
    except DocsCompilerError as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def add(
    name: Annotated[str, typer.Argument(metavar="NAME")],
    from_: Annotated[str | None, typer.Option("--from", metavar="URL")] = None,
    path: Annotated[str | None, typer.Option(metavar="PATH")] = None,
    output: Annotated[str | None, typer.Option(metavar="NAME")] = None,
    config: Annotated[str, typer.Option(metavar="PATH")] = DEFAULT_CONFIG,
    source: Annotated[str | None, typer.Option(metavar="PATH")] = None,
    scope: Annotated[Scope, typer.Option()] = Scope.LOCAL,
    target: Annotated[str | None, typer.Option(metavar="PATH")] = None,
) -> None:
    """Add a doc/skill and run install."""
    if from_ and not path:
        typer.echo("error: --path is required when --from is given", err=True)
        raise typer.Exit(code=1)

    try:
        config_path = Path(config)
        source_dir = _resolve_source_dir(source)
        target_dir = _resolve_target_dir(scope, target)

        loaded_config = _bootstrap_config() if not config_path.exists() else load_config(config_path)

        if from_:
            loaded_config.docs[name] = DocEntry(git=from_, path=path)

        selected_output = _select_output(loaded_config, output)
        _add_doc_to_output(selected_output, name)

        write_config(loaded_config, config_path)

        written = _run_install(loaded_config, source_dir, target_dir)
        for written_path in written:
            typer.echo(f"  wrote {written_path}")
        typer.echo(f"Installed {len(written)} file(s).")
    except DocsCompilerError as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=1)


def main() -> None:
    app()
