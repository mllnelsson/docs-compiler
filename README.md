# Docs Compiler

Write reusable skills and agent instructions once, compile them into multiple AI platform formats.

## Supported formats

- **Claude** — writes skills to `.claude/skills/<name>/SKILL.md`
- **GitHub Copilot plugin** — writes skills/agents under `.claude/plugins/<name>/`
- **ToC** — table of contents (not yet implemented)

## Installation

```sh
cd docs-compiler
uv sync
```

## Configuration

Create a `docs-compiler.yaml` in your project root:

```yaml
docs:
  my-skill:
    git: https://github.com/org/repo
    path: skills/my-skill.md

outputs:
  - format: claude
    include:
      - my-skill

  - format: plugin
    name: my-plugin
    skills:
      - my-skill
    agents:
      - my-agent
```

**`docs`** — optional registry of named remote docs. Each entry can have:
- `git` — git remote URL
- `path` — path within the repo

**`outputs`** — list of output targets. Each output has a `format` field:
- `claude` — `include` lists the doc names to compile
- `plugin` — `name` identifies the plugin; `skills` and `agents` list doc names
- `toc` — no additional fields

Local docs (not listed under `docs`) are resolved from the source directory.

## CLI

### `install`

Resolves all docs and writes output files.

```sh
docs-compiler install [--scope local|user] [--config PATH] [--source PATH] [--target PATH]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--scope` | `local` | `local` writes to `./.claude/`; `user` writes to `~/.claude/` |
| `--config` | `docs-compiler.yaml` | Path to config file |
| `--source` | `$DOCS_COMPILER_SOURCE` or bundled `documentation/` | Directory of local source docs |
| `--target` | — | Override the output root directory (takes precedence over `--scope`) |

### `add`

Adds a doc/skill to the config and immediately runs install.

```sh
docs-compiler add NAME [--from URL --path PATH] [--output NAME] [--scope local|user] [--config PATH] [--source PATH] [--target PATH]
```

| Flag | Default | Description |
|------|---------|-------------|
| `NAME` | *(required)* | Name to register the doc as |
| `--from` | — | Git remote URL (requires `--path`) |
| `--path` | — | Path within the remote repo |
| `--output` | first output in config | Name of the plugin output to add the doc to |
| `--scope` | `local` | `local` writes to `./.claude/`; `user` writes to `~/.claude/` |
| `--config` | `docs-compiler.yaml` | Path to config file (created if missing) |
| `--source` | see `install` | Directory of local source docs |
| `--target` | — | Override the output root directory (takes precedence over `--scope`) |

**Examples:**

Add a local doc (must exist in the source directory):

```sh
docs-compiler add coding-guidelines
```

Add a remote doc from a git repository:

```sh
docs-compiler add coding-guidelines --from https://github.com/org/repo --path docs/coding-guidelines.md
```

Add to a specific plugin output:

```sh
docs-compiler add my-skill --output my-plugin
```
