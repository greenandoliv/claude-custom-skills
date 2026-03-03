---
name: youtube-list-summarize
description: 지정된 YouTube 채널에서 24시간 이내 업로드된 영상의 자막을 추출하여 한국어로 요약하고 각 영상별로 Obsidian _Inbox에 저장합니다. 사용자가 "youtube list summarize", "유튜브 목록 요약", "채널 영상 요약", "/youtube-list-summarize" 등을 말할 때 사용합니다.
allowed-tools: Bash(python3:*), Bash(date:*), Agent, mcp__mcp-obsidian__obsidian_append_content
---

# YouTube List Summarize Skill

지정된 YouTube 채널에서 최근 24시간 이내 업로드된 영상을 수집하고, 각 영상의 자막을 병렬로 추출하여 한국어로 요약한 후 Obsidian `_Inbox`에 영상별로 저장합니다.

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
python3 ~/.claude/skills/youtube-list-summarize/scripts/fetch_youtube.py
```

각 영상은 `---VIDEO---` 구분자로 나뉘며 CHANNEL, TITLE, LINK, DATE 필드를 포함합니다.
결과가 `NO_VIDEOS`이면 "최근 24시간 이내 새 영상이 없습니다." 안내 후 종료합니다.

### 2단계: 오늘 날짜 확인

```bash
date +%Y-%m-%d
```

### 3단계: 모든 영상을 병렬로 자막 추출 및 요약 (Obsidian 저장 제외)

**IMPORTANT: 이 단계는 반드시 모든 영상에 대해 동시에 병렬로 실행해야 합니다.**

수집된 각 영상에 대해 **단일 응답에서 모든 Agent tool 호출을 동시에** 실행합니다.

각 영상마다 `general-purpose` subagent를 호출합니다:
- **subagent_type**: `general-purpose`
- **description**: `Summarize YouTube video: <TITLE>`
- **prompt**: 아래 형식으로 작성합니다. **Obsidian 저장은 하지 않고 마크다운 내용만 반환합니다.**

```
당신은 YouTube 영상 자막 추출 및 요약 에이전트입니다.

## 영상 정보
URL: <LINK>
CHANNEL: <CHANNEL>
TITLE: <TITLE>
DATE: <DATE>
TODAY: <오늘날짜 YYYY-MM-DD>

## 처리 절차

### 1단계: 자막 추출
```bash
python3 ~/.claude/skills/youtube-list-summarize/scripts/fetch_transcript.py "<URL>"
```
- 첫 줄: `VIDEO_ID: <id>`, 둘째 줄: `LANGUAGE: <언어>`
- `---TRANSCRIPT---` ~ `---END---` 사이가 자막
- `ERROR:`로 시작하면 오류를 반환하고 종료

### 2단계: 제목 및 채널명 정제
1. 특수문자 제거 (한글, 영문, 숫자, 공백만 유지)
2. 연속 공백 → 하나로 정리
3. 제목 앞 10글자만 사용

### 3단계: 한국어 시간순 요약 생성
- 각 `[MM:SS]` 섹션을 1~3문장 한국어로 요약
- 영어 자막은 번역하여 한국어로 작성
- 전체 3~5줄 종합 요약 포함

## 반환 형식
아래 세 가지를 반환합니다:

**FILEPATH:** `_Inbox/<TODAY> youtube <정제된_채널명> <정제된_제목_앞10글자>.md`

**LANGUAGE:** <자막 언어>

**MARKDOWN_CONTENT:**
```markdown
# 📺 YouTube 영상 요약

> 영상: [<제목>](<URL>) | 요약일: <TODAY> | 채널: <채널명> | 자막 언어: <언어>

---

## 🗒️ 종합 요약

<3~5문장 종합 요약>

---

## ⏱️ 시간순 요약

### [00:00] <섹션 제목>
<핵심 내용>

(섹션마다 반복)

---

## 🔖 태그

#youtube #summary #<날짜>
```

**중요: Obsidian에 직접 저장하지 말고 위 형식으로만 반환하세요.**
```

### 4단계: 에이전트 결과 수집 후 Obsidian에 저장

모든 에이전트가 완료되면, 각 에이전트가 반환한 내용을 파싱하여 Obsidian에 저장합니다.

각 영상별로 `mcp__mcp-obsidian__obsidian_append_content` 도구를 사용합니다:
- **filepath**: 에이전트가 반환한 `FILEPATH:` 값
- **content**: 에이전트가 반환한 `MARKDOWN_CONTENT:` 블록 전체

오류가 발생한 영상은 건너뛰고 계속 진행합니다.

### 5단계: 완료 안내

1. 처리된 영상 수 (성공/실패 구분)
2. 저장된 Obsidian 파일 경로 목록
3. 각 영상의 채널명과 제목
4. 오류 발생 영상 안내
