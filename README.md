# Claude Custom Skills

A collection of reusable [Claude Code](https://claude.ai/code) skills (slash commands) for daily developer workflows.

## What are Claude Code Skills?

Claude Code skills are custom slash commands stored as markdown files. They let you invoke complex, multi-step AI workflows with a single command — anywhere, across any project.

- Stored in `~/.claude/commands/` → available globally in all projects
- Stored in `.claude/commands/` inside a project → available only in that project
- Invoked as `/skill-name [arguments]` in any Claude Code session

---

## Skills

### `/analyze-repo` — Code Analysis Agent

Analyze any GitHub repository or local directory and generate a comprehensive markdown report.

**Usage:**
```bash
# Analyze a GitHub repo
/analyze-repo https://github.com/owner/repo-name

# Analyze a local directory
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
# Copy to your global Claude commands directory
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

# Copy skills (slash commands) to Claude's global commands directory
cp analyze-repo.md ~/.claude/commands/

# Copy subagents to Claude's global agents directory
cp code-improvement-advisor.md ~/.claude/agents/
```

No restart required — skills and agents are available immediately in Claude Code.

### File locations

| Type | Directory | Invoked as |
|------|-----------|-----------|
| Skill (slash command) | `~/.claude/commands/` | `/skill-name [args]` |
| Subagent | `~/.claude/agents/` | Automatically by Claude or via Agent tool |

---

## Requirements

- [Claude Code](https://claude.ai/code) CLI installed
- For `/analyze-repo`:
  - `gh` CLI (for GitHub URL cloning): `brew install gh`
  - An Obsidian vault (or update the output path in the skill file)

---

## Contributing

Feel free to open a PR with your own skills!

**Skill file format:**
```markdown
---
description: "Brief description of what this skill does"
argument-hint: "<argument-name>"
allowed-tools: [list of tools this skill uses]
---

[Prompt content — written in natural language, instructing Claude what to do]
```
