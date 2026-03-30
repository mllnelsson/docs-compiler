---
name: claude-md-creator
description: Create or improve a CLAUDE.md file for a project. Use when the user wants to set up Claude Code for a project, generate a CLAUDE.md from scratch, audit an existing CLAUDE.md, or asks how Claude Code should understand their codebase. Also use when the user wants to make Claude remember project conventions, stop repeating mistakes, or encode team standards.
---

# CLAUDE.md Creator

A skill for generating, auditing, and iteratively improving `CLAUDE.md` files — the persistent context file that Claude Code reads at the start of every session.

## What CLAUDE.md is

CLAUDE.md is the "permanent brain" for a project. Claude Code reads it automatically at session start. It's the primary mechanism for encoding project-specific context that can't be inferred from source code alone: build commands, conventions, architecture decisions, and "never do this" rules.

It can live in multiple places:
- `~/.claude/CLAUDE.md` — personal global defaults (applies to all projects)
- `./CLAUDE.md` — project root, checked into git (shared with team)
- `./subdir/CLAUDE.md` — subdirectory-specific rules, auto-loaded when Claude touches files there
- `.claude/rules/*.md` — scoped rule files imported from CLAUDE.md via `@path/to/file`

## What to put in CLAUDE.md

**Include:**
- Build, test, and run commands (exact shell commands)
- Code style rules that aren't obvious from the codebase (naming conventions, import style, preferred patterns)
- Architecture notes: which files/modules own what, important data flows
- "Never do this" rules — things Claude keeps getting wrong
- Workflow steps: what to run after edits, how to submit changes
- Environment setup notes if non-obvious

**Exclude:**
- Anything Claude can infer from reading the files (e.g., don't list every dependency)
- Vague goals ("write clean code") — be specific or omit
- Information that becomes stale (e.g., time-sensitive data, version numbers unless pinned)
- Anything only relevant occasionally — those belong in Skills, not CLAUDE.md

**The leanness test:** For every line, ask "Would removing this cause Claude to make a mistake?" If no, cut it. A bloated CLAUDE.md causes Claude to ignore the parts that matter.

Keep CLAUDE.md under ~200 lines. If it grows beyond that, move domain-specific rules into `.claude/rules/` and import them with `@.claude/rules/your-rule.md`.

## Anatomy of a good CLAUDE.md

```markdown
# Project overview
One-paragraph summary of what this project is and does.

# Tech stack
List the primary languages, frameworks, and infra. Be brief.

# Commands
## Build
npm run build

## Test
npm test -- --run (run a single test file, not the whole suite)

## Lint
npm run lint

# Code style
- Use ES modules (import/export), not CommonJS (require)
- Functional React components only, no class components
- State management via Zustand (see src/stores/)

# Architecture
- API layer: src/api/ — never call fetch() directly outside here
- Components should not contain business logic; delegate to hooks

# Rules
- NEVER commit directly to main; always use a feature branch
- After changing Python files, always run pytest
- When adding a new route, update src/routes/index.ts

# Imports
@.claude/rules/git-workflow.md
@docs/architecture.md
```

## How to create a CLAUDE.md

### Step 1: Gather context

Before writing anything, understand the project. If you have access to the filesystem:
```bash
ls -la
cat package.json   # or pyproject.toml, Cargo.toml, go.mod, etc.
git log --oneline -10
```

Ask the user:
1. What does this project do? (brief)
2. What commands do you use to build, test, and run it?
3. What conventions does Claude keep violating? (this is gold)
4. Is there a team, or is this solo? (affects whether to git-commit the file)
5. Any domains Claude should know about? (infra, deployment, specific APIs)

If the user ran `/init`, they already have a starter. In that case, jump to the **audit** flow.

### Step 2: Write a draft

Use the anatomy above as a template. Prioritize:
1. Commands first (highest impact, most concrete)
2. Rules that prevent known mistakes
3. Architecture pointers
4. Style conventions

Start minimal. It's easier to add than to prune.

### Step 3: Audit an existing CLAUDE.md

Apply these checks:
- **Leanness**: Flag every line that Claude could figure out without this hint
- **Specificity**: Replace vague rules ("keep it clean") with concrete ones ("max 80 chars per line")
- **Staleness risk**: Flag time-sensitive content or things that might drift
- **Missing commands**: Ask if test/build/lint commands are present
- **Missing "never" rules**: Ask "What does Claude keep getting wrong?" and encode those
- **Too long?**: If over 200 lines, recommend splitting into `.claude/rules/` files

### Step 4: Iterate

CLAUDE.md should be treated like code. Suggest to the user:
- Add a rule every time Claude does something wrong
- Prune rules that no longer apply when the stack changes
- If Claude keeps ignoring a rule, the file might be too long (prune) or the rule phrasing might be ambiguous (rewrite)

Emphasis markers like `IMPORTANT:` or `YOU MUST` improve adherence for critical rules — use sparingly.

## For teams

Recommend:
- Commit CLAUDE.md to git so the whole team benefits
- Personal overrides go in `~/.claude/CLAUDE.md` (gitignored)
- Use `@.claude/rules/your-rule.md` to scope rules to specific workflows
- Treat CLAUDE.md improvements like any other PR

## Using `@imports`

CLAUDE.md supports importing other files:
```markdown
See @README.md for project overview
See @package.json for available scripts

# Additional rules
@.claude/rules/git-workflow.md
@.claude/rules/testing-standards.md
```

This keeps the root file lean while allowing deep documentation to be loaded when relevant.

## Output format

When generating a CLAUDE.md, produce the file directly — don't just describe what to put in it. Show it to the user as a file they can copy-paste or save. If you have filesystem access, offer to write it directly.

After producing it, ask: "Anything Claude keeps getting wrong that we should add?" — that question reliably surfaces the highest-value rules.
