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

## Installation (All Skills)

```bash
# Clone this repo
git clone git@github.com:greenandoliv/claude-custom-skills.git
cd claude-custom-skills

# Copy all skills to Claude's global commands directory
cp *.md ~/.claude/commands/
```

No restart required — skills are available immediately in Claude Code.

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
