import argparse
import os
import sys
from pathlib import Path

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
                print("ToC format not yet implemented", file=sys.stderr)

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


def _cmd_install(args: argparse.Namespace) -> None:
    config_path = Path(args.config)
    source_dir = _resolve_source_dir(args.source)
    target_dir = Path(args.target)

    config = load_config(config_path)
    written = _run_install(config, source_dir, target_dir)

    for path in written:
        print(f"  wrote {path}")
    print(f"Installed {len(written)} file(s).")


def _cmd_add(args: argparse.Namespace) -> None:
    if args.from_ and not args.path:
        print("error: --path is required when --from is given", file=sys.stderr)
        sys.exit(1)

    config_path = Path(args.config)
    source_dir = _resolve_source_dir(args.source)
    target_dir = Path(args.target)

    config = _bootstrap_config() if not config_path.exists() else load_config(config_path)

    if args.from_:
        config.docs[args.name] = DocEntry(git=args.from_, path=args.path)

    output = _select_output(config, args.output)
    _add_doc_to_output(output, args.name)

    write_config(config, config_path)

    written = _run_install(config, source_dir, target_dir)
    for path in written:
        print(f"  wrote {path}")
    print(f"Installed {len(written)} file(s).")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docs-compiler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    install = subparsers.add_parser("install", help="Resolve docs and write outputs")
    install.add_argument("--config", default=DEFAULT_CONFIG, metavar="PATH")
    install.add_argument("--source", default=None, metavar="PATH")
    install.add_argument("--target", default=".", metavar="PATH")

    add = subparsers.add_parser("add", help="Add a doc/skill and run install")
    add.add_argument("name", metavar="NAME")
    add.add_argument("--from", dest="from_", default=None, metavar="URL")
    add.add_argument("--path", default=None, metavar="PATH")
    add.add_argument("--output", default=None, metavar="NAME")
    add.add_argument("--config", default=DEFAULT_CONFIG, metavar="PATH")
    add.add_argument("--source", default=None, metavar="PATH")
    add.add_argument("--target", default=".", metavar="PATH")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        match args.command:
            case "install":
                _cmd_install(args)
            case "add":
                _cmd_add(args)
    except DocsCompilerError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
