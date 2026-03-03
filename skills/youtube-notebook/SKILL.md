---
name: youtube-notebook
description: 지정된 YouTube 채널에서 24시간 이내 업로드된 영상을 수집하여 NotebookLM 노트북을 생성하고 AI 오디오 오버뷰를 만든 후 Obsidian _Inbox에 결과를 저장합니다. 사용자가 "youtube notebook", "유튜브 노트북", "영상 수집", "/youtube-notebook" 등을 말할 때 사용합니다.
allowed-tools: Bash(python3:*), Bash(date:*), mcp__notebooklm-mcp__notebook_create, mcp__notebooklm-mcp__source_add, mcp__notebooklm-mcp__studio_create, mcp__notebooklm-mcp__studio_status, mcp__notebooklm-mcp__notebook_describe, mcp__mcp-obsidian__obsidian_append_content
---

# YouTube Notebook Skill

지정된 YouTube 채널에서 최근 24시간 이내 업로드된 영상을 수집하고, NotebookLM 노트북을 생성하여 AI 오디오 오버뷰를 만든 후 Obsidian `_Inbox`에 결과를 저장합니다.

## 모니터링 채널

| 채널명 | URL |
|--------|-----|
| Nate Herk | https://www.youtube.com/@nateherk |
| Nick Saraev | https://www.youtube.com/@nicksaraev |
| Jack | https://www.youtube.com/@Itssssss_Jack |
| Chase (AI) | https://www.youtube.com/@chase-h-ai |

## 실행 절차

### 1단계: YouTube 영상 수집

파싱 스크립트를 실행하여 24시간 이내 업로드된 영상 목록을 가져옵니다.

```bash
python3 ~/.claude/skills/youtube-notebook/scripts/fetch_youtube.py
```

결과를 파싱합니다. 각 영상은 `---VIDEO---` 구분자로 나뉘며 CHANNEL, TITLE, LINK, DATE 필드를 포함합니다.

결과가 `NO_VIDEOS`이면 "최근 24시간 이내 새 영상이 없습니다." 안내 후 종료합니다.

### 2단계: 오늘 날짜 확인

```bash
date +%Y-%m-%d
```

노트북 이름: `YYYY-MM-DD youtube notebook`

### 3단계: NotebookLM 노트북 생성

`mcp__notebooklm-mcp__notebook_create` 도구로 새 노트북을 생성합니다.

- **title**: `YYYY-MM-DD youtube notebook`

반환된 `document_id`를 이후 단계에 사용합니다.

### 4단계: YouTube 영상을 소스로 추가

수집된 각 영상 URL을 `mcp__notebooklm-mcp__source_add` 도구로 노트북에 추가합니다.

- **source_type**: `url`
- **url**: 각 YouTube 영상 URL (LINK 필드)
- **document_id**: 3단계에서 반환된 노트북 ID

### 5단계: AI 오디오 오버뷰 생성

`mcp__notebooklm-mcp__studio_create` 도구로 오디오 오버뷰를 생성합니다.

- **artifact_type**: `audio`
- **document_id**: 노트북 ID

이후 `mcp__notebooklm-mcp__studio_status`를 폴링하여 생성 완료를 확인합니다. (완료까지 수 분 소요될 수 있습니다)

### 6단계: 노트북 정보 조회

`mcp__notebooklm-mcp__notebook_describe` 도구로 노트북 URL 등 상세 정보를 조회합니다.

- **document_id**: 노트북 ID

### 7단계: Obsidian에 결과 저장

`mcp__mcp-obsidian__obsidian_append_content` 도구로 결과를 저장합니다.

- **filepath** (vault root 기준 상대경로): `_Inbox/YYYY-MM-DD youtube notebook.md`
- 파일이 없으면 자동 생성됩니다.

## 출력 템플릿

```markdown
# 📺 YouTube Notebook

> 수집일: <YYYY-MM-DD HH:MM> | 수집 범위: 최근 24시간 | 영상 수: <N>개

---

## 🔗 NotebookLM

- **노트북**: [YYYY-MM-DD youtube notebook](<notebook_url>)
- **오디오 오버뷰**: 생성 완료 (NotebookLM에서 재생 가능)

---

## 📋 수집된 영상

| 채널 | 제목 | 링크 | 업로드일 |
|------|------|------|----------|
| <채널명> | <제목> | [보기](<link>) | <YYYY-MM-DD HH:MM UTC> |
(영상마다 반복)

---

## 🔖 태그

#youtube #notebook #ai-news #<날짜>
```

## 완료 후 안내

작업 완료 시 사용자에게 다음을 알립니다:
1. 저장된 Obsidian 파일 경로
2. 수집된 영상 수와 채널별 분포
3. NotebookLM 노트북 링크
4. 오디오 오버뷰 생성 상태

영상이 없으면: "최근 24시간 이내 새 영상이 없습니다." 안내 후 종료합니다.
