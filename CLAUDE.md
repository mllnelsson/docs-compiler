# General guidelines

You will always think through the given tasks.

## Assumptions
Always ask the user for clarification over assumptions. When assumptions have been made, clearly state them.

## Workflow
Follow these instructions before making any changes
<workflow>
**1. Planning**
Think through your solution carefully before start implementing.
**2. Guidelines**
Consider your guidelines in your design decisions.
**3. Scope**
Always stick to the scope you have been given
**4. Definition of done**
Clearly outline your definition of done and final checks and ensure your design will fulfill them.
**5. Implementation**
Fulfill your task to the point without adding anything extra the user hasn't specified
**6. Documentation**
Only document what the user has asked for or in your instructions
</workflow>

## Documentation
IMPORTANT: Do not create unnecessary documentation md files unless the user has asked for them.

## Context
Utilize subagents for retrieval and discovery based tasks.
Always refer to skills and documentation in `documentation/` before relying on pre-trained knowledge.

# Project overview
`docs-compiler` compiles reusable markdown skills and agent instructions into multiple output formats (Claude SKILL.md, GitHub Copilot plugin, Table of Contents). Write once, compile for multiple AI platforms.

# Tech stack
- Python 3.12+, uv (package manager)
- Pydantic v2 (config/data models), PyYAML
- pytest

# Project structure
The Python package lives in a `docs-compiler/` subdirectory — not the repo root. Run all Python commands from there.

# Commands
## Test
cd docs-compiler && uv run pytest

## Run CLI
cd docs-compiler && uv run docs-compiler install
cd docs-compiler && uv run docs-compiler add NAME [--from URL] [--path PATH]

# Architecture
All source files are under `docs-compiler/src/docs_compiler/`:
- `config.py` — DocEntry, ClaudeOutput, PluginOutput, Config models; load_config/write_config
- `resolver.py` — local and git-remote doc resolution; remote cache at `~/.cache/docs-compiler`
- `references.py` — cross-doc reference resolution with cycle detection
- `formats/` — output writers per target (claude.py, plugin.py)
- `main.py` — CLI entry point (install, add subcommands)
- `errors.py` — custom exception hierarchy; catch only at CLI boundary

# Code style
IMPORTANT: Always invoke the `coding-guidelines` skill (and the `coding-guidelines/python` sub-skill) before writing or reviewing any Python code. Do not rely on pre-trained style intuition — load the skill first.
