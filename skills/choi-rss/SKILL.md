---
name: choi-rss
description: Threads @choi.openai 계정의 RSS 피드에서 24시간 이내 게시물을 수집하고, 요약 및 인사이트를 추출하여 Obsidian _Inbox에 마크다운 파일로 저장합니다. 사용자가 "choi rss", "최신 게시물 가져와", "choi.openai 피드", "/choi-rss" 등을 말할 때 사용합니다.
allowed-tools: Bash(curl:*), Bash(date:*), Bash(python3:*), mcp__mcp-obsidian__obsidian_append_content
---

# Choi RSS Skill

Threads `@choi.openai` 계정의 RSS 피드에서 24시간 이내 게시물을 수집하고, 요약·인사이트를 마크다운으로 정리하여 Obsidian에 저장합니다.

## RSS 정보

- **피드 URL**: https://rss.app/feeds/M4NpVSm323yf8bmE.xml
- **대상 계정**: Threads `@choi.openai`
- **수집 범위**: 최근 24시간 이내 게시물

## 실행 절차

### 1단계: RSS 피드 수집 및 파싱

파싱 스크립트(`scripts/parse_rss.py`)를 사용해 RSS를 가져오고 24시간 이내 게시물만 필터링합니다.

```bash
curl -s https://rss.app/feeds/M4NpVSm323yf8bmE.xml | python3 ~/.claude/skills/choi-rss/scripts/parse_rss.py
```

파싱 결과를 변수에 저장하고, 게시물이 없으면 사용자에게 안내 후 종료합니다.

### 2단계: 요약 및 인사이트 추출

수집된 각 게시물에 대해 다음 기준으로 분석합니다:

- **인사이트**: AI/OpenAI/기술 트렌드 관점에서 얻을 수 있는 인사이트
- **키워드**: 주요 키워드 3~5개 추출
- **중요도**: 상/중/하 평가 (업계 영향력, 새로운 정보 여부 기준)

### 3단계: Obsidian MCP로 마크다운 파일 저장

오늘 날짜를 가져와 파일명을 구성합니다.

```bash
date +%Y-%m-%d
```

작성한 마크다운 내용을 `mcp__mcp-obsidian__obsidian_append_content` 도구로 저장합니다.

- **filepath** (vault root 기준 상대경로): `_Inbox/<YYYY-MM-DD> choi_claude_skill.md`
- 파일이 없으면 자동 생성되고, 있으면 내용이 추가됩니다.

## 출력 템플릿

```markdown
# 📡 @choi.openai Threads 피드 요약

> 수집일: <YYYY-MM-DD HH:MM> | 수집 범위: 최근 24시간 | 게시물 수: <N>개

---

## 📋 전체 인사이트 요약

<모든 게시물을 종합한 3~5줄 요약. 오늘 @choi.openai가 다룬 주요 주제와 흐름>

---

## 📌 게시물 상세

### 1. <게시물 제목 또는 첫 줄 요약>

- **게시일시**: <YYYY-MM-DD HH:MM UTC>
- **링크**: [원문 보기](<link>)
- **중요도**: ⭐⭐⭐ 상 / ⭐⭐ 중 / ⭐ 하

**요약**
> <게시물 핵심 발췌>

**인사이트**
<이 게시물에서 얻을 수 있는 인사이트. AI 트렌드, 기술 변화, 비즈니스 함의 등>

**키워드**: `#키워드1` `#키워드2` `#키워드3`

---

(게시물마다 반복)

## 🔖 태그

#choi-openai #threads #ai-news #<날짜>
```

## 완료 후 안내

작업 완료 시 사용자에게 다음을 알립니다:
1. 저장된 파일 경로
2. 수집된 게시물 수
3. 주요 인사이트 2~3줄 미리보기

게시물이 없으면: "최근 24시간 이내 새 게시물이 없습니다." 안내 후 종료합니다.
