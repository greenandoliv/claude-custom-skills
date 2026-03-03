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

### `choi-rss` — Threads 피드 요약 Skill

`@choi.openai` Threads 계정의 RSS 피드에서 24시간 이내 게시물을 수집하고, AI 인사이트 요약을 Obsidian에 저장합니다.

**Usage:**

```
"choi rss"
"최신 게시물 가져와"
"/choi-rss"
```

**What it does:**

1. RSS 피드에서 24시간 이내 게시물 수집 (`curl` + `parse_rss.py`)
2. 각 게시물의 인사이트, 키워드, 중요도 분석
3. Obsidian `_Inbox/YYYY-MM-DD choi_claude_skill.md` 저장

**Install:**
```bash
mkdir -p ~/.claude/skills/choi-rss/scripts
cp skills/choi-rss/SKILL.md ~/.claude/skills/choi-rss/
cp skills/choi-rss/scripts/parse_rss.py ~/.claude/skills/choi-rss/scripts/
```

---

### `youtube-notebook` — YouTube → NotebookLM Skill

지정된 YouTube 채널에서 24시간 이내 업로드된 영상을 수집하여 NotebookLM 노트북과 AI 오디오 오버뷰를 자동 생성합니다.

**Monitored channels:** Nate Herk, Nick Saraev, Jack, Chase (AI)

**Usage:**

```
"youtube notebook"
"유튜브 노트북"
"영상 수집"
"/youtube-notebook"
```

**What it does:**

1. YouTube RSS 피드에서 24시간 이내 영상 수집 (`fetch_youtube.py`)
2. NotebookLM 노트북 생성 후 영상 URL 소스 추가
3. AI 오디오 오버뷰 생성 (비동기 폴링)
4. Obsidian `_Inbox/YYYY-MM-DD youtube notebook.md` 저장

**Install:**
```bash
mkdir -p ~/.claude/skills/youtube-notebook/scripts
cp skills/youtube-notebook/SKILL.md ~/.claude/skills/youtube-notebook/
cp skills/youtube-notebook/scripts/fetch_youtube.py ~/.claude/skills/youtube-notebook/scripts/
```

---

### `youtube-list-summarize` — 채널 영상 일괄 요약 Skill

지정된 4개 YouTube 채널에서 24시간 이내 업로드된 영상을 수집하고, 각 영상의 자막을 **병렬**로 추출하여 한국어 요약을 Obsidian에 영상별로 저장합니다.

**Monitored channels:** Nate Herk, Nick Saraev, Jack, Chase (AI)

**Usage:**

```
"youtube list summarize"
"유튜브 목록 요약"
"채널 영상 요약해줘"
"/youtube-list-summarize"
```

**What it does:**

1. YouTube RSS 피드에서 24시간 이내 영상 수집 (`fetch_youtube.py`)
2. 모든 영상에 대해 `general-purpose` 서브에이전트를 **동시에** 병렬 실행
3. 각 에이전트: `fetch_transcript.py`로 자막 추출 후 한국어 시간순 요약 생성
4. 메인 SKILL이 에이전트 결과를 수집하여 Obsidian 저장
5. 각 영상별 `_Inbox/YYYY-MM-DD youtube <채널명> <제목앞10글자>.md` 저장

**Architecture (parallel subagent pattern):**

```
SKILL.md (orchestrator)
  ├── fetch_youtube.py → 영상 목록 수집
  ├── [병렬] Agent 1 → 영상 A 자막 추출 + 요약 → 마크다운 반환
  ├── [병렬] Agent 2 → 영상 B 자막 추출 + 요약 → 마크다운 반환
  └── 결과 수집 → mcp-obsidian으로 저장
```

> 에이전트는 MCP 도구 접근 불가 → 마크다운 내용만 반환, 메인 SKILL이 Obsidian 저장 담당

**Install:**
```bash
pip install youtube-transcript-api
brew install yt-dlp
mkdir -p ~/.claude/skills/youtube-list-summarize/scripts
cp skills/youtube-list-summarize/SKILL.md ~/.claude/skills/youtube-list-summarize/
cp skills/youtube-list-summarize/scripts/fetch_youtube.py ~/.claude/skills/youtube-list-summarize/scripts/
cp skills/youtube-list-summarize/scripts/fetch_transcript.py ~/.claude/skills/youtube-list-summarize/scripts/
cp skills/youtube-list-summarize/agents/youtube-video-summarize.md ~/.claude/agents/
```

---

### `youtube-summarize` — YouTube 영상 요약 Skill

특정 YouTube 영상 URL을 받아 자막을 추출하고, 시간 순으로 한국어 요약을 생성하여 Obsidian에 저장합니다.

**Usage:**

```
"이 영상 요약해줘: https://youtube.com/watch?v=..."
"유튜브 요약"
"/youtube-summarize"
```

**What it does:**

1. `fetch_transcript.py`로 자막 추출 (한국어 우선, 없으면 영어)
2. IP 차단 시 yt-dlp로 자동 fallback
3. 5분 구간별 시간 순 한국어 요약 생성
4. Obsidian `_Inbox/YYYY-MM-DD youtube <채널명> <제목앞10글자>.md` 저장

**Transcript extraction strategy:**

```
1차: youtube-transcript-api  →  IpBlocked/RequestBlocked 시
2차: yt-dlp (VTT 파싱)
```

**Language priority:** 한국어 수동 → 한국어 자동 → 영어 수동 → 영어 자동

**Install:**
```bash
pip install youtube-transcript-api
mkdir -p ~/.claude/skills/youtube-summarize/scripts
cp skills/youtube-summarize/SKILL.md ~/.claude/skills/youtube-summarize/
cp skills/youtube-summarize/scripts/fetch_transcript.py ~/.claude/skills/youtube-summarize/scripts/
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

# analyze-repo skill + slash command
mkdir -p ~/.claude/skills/analyze-repo
cp skills/analyze-repo/SKILL.md ~/.claude/skills/analyze-repo/SKILL.md
cp analyze-repo.md ~/.claude/commands/

# choi-rss skill
mkdir -p ~/.claude/skills/choi-rss/scripts
cp skills/choi-rss/SKILL.md ~/.claude/skills/choi-rss/
cp skills/choi-rss/scripts/parse_rss.py ~/.claude/skills/choi-rss/scripts/

# youtube-notebook skill
mkdir -p ~/.claude/skills/youtube-notebook/scripts
cp skills/youtube-notebook/SKILL.md ~/.claude/skills/youtube-notebook/
cp skills/youtube-notebook/scripts/fetch_youtube.py ~/.claude/skills/youtube-notebook/scripts/

# youtube-summarize skill
pip install youtube-transcript-api
mkdir -p ~/.claude/skills/youtube-summarize/scripts
cp skills/youtube-summarize/SKILL.md ~/.claude/skills/youtube-summarize/
cp skills/youtube-summarize/scripts/fetch_transcript.py ~/.claude/skills/youtube-summarize/scripts/

# youtube-list-summarize skill (parallel multi-video summarization)
pip install youtube-transcript-api
brew install yt-dlp
mkdir -p ~/.claude/skills/youtube-list-summarize/scripts
cp skills/youtube-list-summarize/SKILL.md ~/.claude/skills/youtube-list-summarize/
cp skills/youtube-list-summarize/scripts/fetch_youtube.py ~/.claude/skills/youtube-list-summarize/scripts/
cp skills/youtube-list-summarize/scripts/fetch_transcript.py ~/.claude/skills/youtube-list-summarize/scripts/
cp skills/youtube-list-summarize/agents/youtube-video-summarize.md ~/.claude/agents/

# code-improvement-advisor subagent
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
- For `analyze-repo`:
  - `gh` CLI (for GitHub URL cloning): `brew install gh`
  - An Obsidian vault (or update the output path in the skill file)
- For `choi-rss`:
  - An Obsidian vault with MCP configured (`mcp__mcp-obsidian`)
- For `youtube-notebook`:
  - NotebookLM MCP configured (`mcp__notebooklm-mcp`) — run `nlm login` to authenticate
  - An Obsidian vault with MCP configured
- For `youtube-summarize`:
  - `pip install youtube-transcript-api`
  - `yt-dlp` (fallback): `brew install yt-dlp`
  - An Obsidian vault with MCP configured
- For `youtube-list-summarize`:
  - `pip install youtube-transcript-api`
  - `yt-dlp` (fallback): `brew install yt-dlp`
  - An Obsidian vault with MCP configured (`mcp__mcp-obsidian`)

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
