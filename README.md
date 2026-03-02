# Claude Custom Skills

A collection of reusable [Claude Code](https://claude.ai/code) extensions for daily developer workflows — slash commands, skills, and subagents.

## Claude Code Extension Types

Claude Code supports three types of extensions:

| Type | Directory | How it's invoked |
|------|-----------|-----------------|
| **Slash command** | `~/.claude/commands/` | User types `/name [args]` explicitly |
| **Skill** | `~/.claude/skills/` | Claude auto-triggers based on conversation context |
| **Subagent** | `~/.claude/agents/` | Claude spawns as an independent subprocess |

**Skill vs Slash command**: A skill's `description` field acts as a trigger condition — Claude reads it and decides whether to load the skill automatically. A slash command requires explicit user invocation.

---

## Skills

### `analyze-repo` — Code Analysis Skill

Auto-triggered when you ask Claude to analyze a repository or codebase — no slash command needed.

Analyze any GitHub repository or local directory and generate a comprehensive markdown report.

**Usage:**

Just ask Claude naturally — no slash command required:

```
"이 GitHub repo 분석해줘: https://github.com/owner/repo-name"
"이 코드베이스 설명해줘"
"Analyze this project for me: /path/to/your/project"
"What does this repo do?"
```

Or still use the slash command if you prefer:
```bash
/analyze-repo https://github.com/owner/repo-name
/analyze-repo /path/to/your/project
```

**What it generates:**

A structured markdown file saved to your Obsidian inbox with:

| Section | Content |
|---------|---------|
| TL;DR | One-line summary, key value, top 3 features |
| Key Concepts | Domain terms and core abstractions |
| Directory Structure | File tree (3 levels deep) + Start Here guide |
| Tech Stack | Languages, frameworks, libraries, external APIs |
| Environment Setup | Required env vars, config files |
| Features | Numbered feature list with file references |
| How to Run | Prerequisites, install, dev/prod commands |
| Flow Diagram | Mermaid flowchart of the full system |
| Architecture | Mermaid component/module relationship graph |
| Sequence Diagram | Key user scenario or API call flow |

**How it works:**

The skill orchestrates **4 parallel subagents** using Claude's Task tool:

```
/analyze-repo <input>
      │
      ├── Agent 1: Structure Analysis    → directory tree, file roles, Start Here guide
      ├── Agent 2: Features & Deps       → tech stack, libraries, env vars, external APIs
      ├── Agent 3: Entry Point & Flow    → main files, execution path, data flow
      └── Agent 4: Architecture          → modules, layers, Mermaid diagrams (×3)
                                │
                                └── Merged → repo-analysis-<name>-<date>.md
```

**Output location:**

```
~/workspace/obsidian/secondbrain/_Inbox/repo-analysis-<repo-name>-YYYY-MM-DD.md
```

> Customize this path in the skill file to match your own Obsidian vault location.

**Install:**
```bash
# As a skill (auto-triggered by Claude)
cp skills/analyze-repo/SKILL.md ~/.claude/skills/analyze-repo/SKILL.md

# As a slash command (user-invoked with /analyze-repo)
cp analyze-repo.md ~/.claude/commands/analyze-repo.md
```

---

### `code-improvement-advisor` — Code Quality Subagent

Analyzes code files for quality improvements, identifies readability issues, performance bottlenecks, and best practice violations. Returns actionable suggestions with before/after code comparisons.

**How to use:**

This is a **subagent** (not a slash command). Claude automatically invokes it when reviewing code quality. You can also trigger it manually by asking Claude to review a file.

```
# Claude will automatically launch this agent when you say things like:
"Can you review auth.py for quality issues?"
"This pipeline.js feels slow and messy, take a look"
"Do a final pass on utils.py and api_handler.py"
```

**What it analyzes:**

| Dimension | What It Checks |
|-----------|---------------|
| Readability | Naming, complexity, nesting, comments, long functions, magic values |
| Performance | Algorithm efficiency, repeated computations, caching opportunities, I/O patterns |
| Best Practices | Language idioms, error handling, security vulnerabilities, DRY violations, SOLID |

**Output format per issue:**

```
### Issue N: [Title]
Category: Readability | Performance | Best Practices
Severity: 🔴 High | 🟡 Medium | 🟢 Low
Location: filename.ext, line X–Y

Explanation → Current Code → Improved Version → Why This Is Better
```

Ends with a **Summary** showing total issues by severity and top priority actions.

**Install:**
```bash
# Copy to your global Claude agents directory
cp code-improvement-advisor.md ~/.claude/agents/code-improvement-advisor.md
```

---

## Installation

```bash
# Clone this repo
git clone git@github.com:greenandoliv/claude-custom-skills.git
cd claude-custom-skills

# Install skill (auto-triggered by Claude)
mkdir -p ~/.claude/skills/analyze-repo
cp skills/analyze-repo/SKILL.md ~/.claude/skills/analyze-repo/SKILL.md

# Install slash command (user-invoked with /analyze-repo)
cp analyze-repo.md ~/.claude/commands/

# Install subagent
cp code-improvement-advisor.md ~/.claude/agents/
```

No restart required — all extensions are available immediately in Claude Code.

### File locations

| Type | Directory | Invoked as |
|------|-----------|-----------|
| Skill | `~/.claude/skills/<name>/SKILL.md` | Claude auto-triggers from context |
| Slash command | `~/.claude/commands/` | `/skill-name [args]` |
| Subagent | `~/.claude/agents/` | Claude spawns via Task tool |

---

## Requirements

- [Claude Code](https://claude.ai/code) CLI installed
- For `/analyze-repo`:
  - `gh` CLI (for GitHub URL cloning): `brew install gh`
  - An Obsidian vault (or update the output path in the skill file)

---

## Contributing

Feel free to open a PR with your own extensions!

**Slash command format** (`commands/<name>.md`):
```markdown
---
description: "Brief description"
argument-hint: "<argument-name>"
allowed-tools: [list of tools]
---

[Prompt content instructing Claude what to do]
```

**Skill format** (`skills/<name>/SKILL.md`):
```markdown
---
name: skill-name
description: Use this skill when the user says "...", asks about "...", or mentions "...". [Detailed trigger conditions — Claude reads this to decide when to auto-invoke.]
allowed-tools: [list of tools]
---

[Guidance content Claude incorporates into its responses]
```
