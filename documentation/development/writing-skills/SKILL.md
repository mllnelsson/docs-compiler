---
name: skill-creator
description: Create new skills, improve existing skills, and optimize skill descriptions. Use when the user wants to build a skill from scratch, refine a draft skill, turn a workflow into a reusable skill, improve skill triggering, or benchmark skill quality. Also use when the user says "make this a skill", "turn this into a skill", "I want Claude to always do X this way", or wants to encode a repeatable workflow.
---

# Skill Creator

A skill for creating, testing, and iteratively improving Claude skills (SKILL.md files).

## What a skill is

A skill is a Markdown file (`SKILL.md`) that gives Claude domain knowledge and reusable workflows. Skills live in `.claude/skills/<skill-name>/SKILL.md`. Claude discovers them from the description in their YAML frontmatter, reads the body when triggered, and can load bundled resources on demand.

Skills are for things that are sometimes relevant — they're loaded on demand, not burned into every session like CLAUDE.md. When to use each:
- **CLAUDE.md** → always-on context: commands, conventions, team rules
- **Skills** → domain knowledge or workflows needed only sometimes

## Skill anatomy

```
skill-name/
├── SKILL.md              ← required; frontmatter + instructions
├── scripts/              ← executable code for deterministic tasks
├── references/           ← docs loaded into context as needed
└── assets/               ← templates, fonts, icons used in output
```

**Three-tier loading:**
1. **Frontmatter** (name + description) — always in context, ~100 words
2. **SKILL.md body** — loaded when skill is triggered, ideally <500 lines
3. **Bundled resources** — loaded only when referenced; scripts can execute without being read

## The creation process

### 0. Orient: where is the user?

Identify which phase they're in and jump in there:
- "I want to make a skill for X" → start at **Capture Intent**
- "Here's my draft, help me test it" → jump to **Test & Evaluate**
- "My skill isn't triggering reliably" → jump to **Optimize Description**
- "Turn this conversation into a skill" → extract from history, go to **Write the Skill**

### 1. Capture intent

If the user's request comes from a conversation, extract answers first — look at tools used, step sequence, corrections made, input/output formats. Fill gaps by asking. Confirm before proceeding.

Key questions:
1. What should this skill enable Claude to do?
2. When should it trigger? What user phrases or contexts?
3. What's the expected output format?
4. Do we need test cases? (Yes for verifiable outputs; often skip for subjective ones)

### 2. Interview and research

Ask about edge cases, example files, success criteria, and dependencies. If useful MCPs are available, research in parallel. Come prepared — reduce burden on the user.

### 3. Write the SKILL.md

**Frontmatter (required):**
```yaml
---
name: skill-name           # lowercase, hyphens only
description: |             # What it does + when to use it.
  One or two sentences. Include both the capability AND specific triggers/contexts.
  Be slightly "pushy" — Claude tends to undertrigger. Instead of "for PDF files",
  write "Use when working with PDFs, forms, or when the user mentions document extraction."
---
```

**Body — writing guidelines:**

- Use imperative form ("Extract the table" not "You should extract")
- Explain *why* things matter, not just what to do — this generalizes better
- Only include what Claude doesn't already know
- Define output formats explicitly when they matter (show a template, not just a description)
- Include 1–2 brief examples for non-obvious transformations
- Keep SKILL.md under 500 lines; if approaching this limit, split into reference files and link them clearly

**Avoid:**
- Information that will become stale (time-sensitive version-specific instructions)
- Reproducing knowledge Claude already has
- Vague instructions ("make it look good")

**Reference files:** For large domain docs, add a table of contents at the top and reference from SKILL.md with clear guidance on when to read them.

**Shell commands in SKILL.md:** Use `!command` syntax to inject live shell output into context at invocation time (Claude runs it, not the user):
```markdown
Current git branch: !`git branch --show-current`
```

### 4. Test the skill

Come up with 2–3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user and confirm before running.

Save to `evals/evals.json`:
```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's actual task prompt",
      "expected_output": "Description of what a good result looks like",
      "files": []
    }
  ]
}
```

**In Claude.ai (no subagents):** Run test cases yourself, one at a time. Read the skill's SKILL.md, then follow its instructions to complete the prompt. Present outputs in-conversation and ask for feedback inline.

**In Claude Code / Cowork (subagents available):** Spawn with-skill and baseline subagents in the same turn (don't do with-skill first and come back for baselines). Save results in `<skill-name>-workspace/iteration-N/eval-ID/`. After running, generate the eval viewer BEFORE evaluating inputs yourself — get them in front of the human ASAP.

### 5. Evaluate and iterate

While test cases run, draft assertions (in Claude Code). In Claude.ai, do qualitative review with the user.

Ask the user:
- Does the output look right?
- What would you change?
- Does it handle edge case X?

Rewrite the skill based on feedback. Repeat until satisfied.

### 6. Optimize the description (optional but valuable)

A good description is the entire triggering mechanism. Claude only sees `name` + `description` when deciding whether to consult a skill.

Good description checklist:
- States what the skill does (capability)
- States when to use it (specific triggers, user phrases, file types)
- Slightly pushy — errs toward triggering rather than staying silent
- Third person, no ambiguity
- Under ~50 words

Example:
```
Processes Excel files and generates formatted reports with charts and pivot tables.
Use when analyzing spreadsheets, .xlsx files, tabular data, or when the user asks
to summarize, visualize, or restructure tabular data — even if they don't say "Excel".
```

In Claude Code, use `run_loop.py` from the skill-creator scripts to run automated description optimization. In Claude.ai, iterate manually based on whether test queries would plausibly trigger a skill with that description.

### 7. Package and deliver

If `present_files` is available, package the skill:
```bash
python -m scripts.package_skill <path/to/skill-folder>
```
Present the `.skill` file to the user. If packaging isn't available, zip the directory or provide the raw file tree.

## Updating an existing skill

- Preserve the original `name` field exactly — don't rename
- Copy to a writable location before editing if the original path is read-only:
  ```bash
  cp -r /mnt/skills/public/my-skill /tmp/my-skill
  ```
- Edit in `/tmp/`, then package and return to the user

## Skill design principles

**Progressive disclosure:** Don't front-load everything. SKILL.md is a table of contents; reference files carry the detail. Claude reads only what it needs.

**No surprise:** Skills must not contain malware, misleading instructions, or content designed to facilitate unauthorized access. The skill's contents should match its description.

**Testability:** Prefer skills with verifiable outputs. If you can assert "output contains X" or "file was created with correct structure", the skill is more reliable and improvable.

**Leanness:** Every line should earn its place. Challenge each piece: does Claude need to be told this, or does it already know? A shorter SKILL.md means the important parts get read and followed.

## Communicating with the user

Skill creator is used by developers, non-developers, and everyone in between. Read context cues and adjust jargon accordingly:
- "Evaluation", "benchmark" — OK for technical users; briefly define for others
- "JSON", "assertion" — only use without explanation if the user clearly knows them
- If in doubt, explain briefly and move on

---

**Core loop (don't skip steps):**
1. Understand the skill's purpose
2. Draft or edit SKILL.md
3. Run test prompts (yourself in Claude.ai; via subagents in Claude Code)
4. Review with the user — qualitative first, quantitative if available
5. Revise and repeat
6. Optimize description when the skill is otherwise stable
7. Package and return
