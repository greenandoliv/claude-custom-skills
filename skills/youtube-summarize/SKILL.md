---
name: youtube-summarize
description: 특정 YouTube 링크를 입력받아 자막을 추출하고, 시간 순으로 한국어 요약을 생성한 후 Obsidian _Inbox에 저장합니다. 사용자가 "youtube 요약", "유튜브 요약", "이 영상 요약해줘", "/youtube-summarize" 등을 말하거나 YouTube URL을 제공할 때 사용합니다.
allowed-tools: Bash(python3:*), Bash(date:*), mcp__mcp-obsidian__obsidian_append_content
---

# YouTube Summarize Skill

특정 YouTube 영상의 자막을 추출하고, 시간 순으로 한국어 요약을 생성하여 Obsidian `_Inbox`에 저장합니다.

## 실행 절차

### 0단계: YouTube URL 확인

사용자로부터 YouTube URL을 받습니다. 사용자가 URL을 제공하지 않은 경우 요청합니다.

### 1단계: 자막 추출

아래 스크립트를 실행하여 자막을 가져옵니다. `<URL>`을 실제 YouTube URL로 교체합니다.

```bash
python3 ~/.claude/skills/youtube-summarize/scripts/fetch_transcript.py "<URL>"
```

- 출력 첫 줄: `VIDEO_ID: <id>`
- 출력 두 번째 줄: `LANGUAGE: <언어 코드>`
- `---TRANSCRIPT---` 이후: 5분 단위 `[MM:SS]` 타임스탬프 + 자막 텍스트
- `---END---`로 종료

오류가 발생하면(`ERROR:` 로 시작하는 줄) 사용자에게 오류 내용을 알리고 종료합니다.

### 2단계: 영상 제목 및 채널명 가져오기

yt-dlp로 제목과 채널명을 가져옵니다.

```bash
yt-dlp --print "%(title)s" --no-download "<URL>" 2>/dev/null
yt-dlp --print "%(channel)s" --no-download "<URL>" 2>/dev/null
```

가져온 제목과 채널명을 다음 규칙으로 정제합니다:

1. **특수문자 제거**: 한글, 영문, 숫자, 공백만 남기고 나머지 문자는 모두 제거
2. **공백 정리**: 연속된 공백은 하나로, 앞뒤 공백 제거
3. **제목 단축**: 정제된 제목의 앞 10글자만 사용

예시:
- 원본 제목: `"AI의 미래: ChatGPT vs Claude!"` → 정제: `AI의 미래 ChatGPT vs Claud` → 10글자: `AI의 미래 Cha`
- 원본 채널명: `"Lex Fridman Podcast"` → 정제: `Lex Fridman Podcast`

제목/채널명을 알 수 없으면 각각 `unknown`, `unknown`으로 대체합니다.

### 3단계: 한국어 시간 순 요약 생성

추출된 자막을 분석하여 다음 형식으로 요약합니다:

- 각 `[MM:SS]` 섹션별로 핵심 내용을 1~3문장으로 한국어 요약
- 자막이 영어인 경우 번역하여 한국어로 작성
- 음악/노래 자막([♪])은 "[음악/노래 섹션]"으로 표기
- 전체 영상을 아우르는 3~5줄 종합 요약도 작성

### 4단계: 오늘 날짜 확인

```bash
date +%Y-%m-%d
```

### 5단계: Obsidian에 결과 저장

`mcp__mcp-obsidian__obsidian_append_content` 도구로 저장합니다.

- **filepath** (vault root 기준 상대경로): `_Inbox/<YYYY-MM-DD> youtube <정제된_채널명> <정제된_제목_앞10글자>.md`
  - 예시: `_Inbox/2026-03-02 youtube Lex Fridman Podcast AI의 미래 Cha.md`
- 파일이 없으면 자동 생성, 있으면 내용 추가

## 출력 템플릿

```markdown
# 📺 YouTube 영상 요약

> 영상: [<제목>](<URL>) | 요약일: <YYYY-MM-DD HH:MM> | 자막 언어: <언어>

---

## 🗒️ 종합 요약

<영상 전체 내용을 3~5문장으로 요약>

---

## ⏱️ 시간 순 요약

### [00:00] <첫 섹션 제목>

<해당 구간 핵심 내용 1~3문장>

### [MM:SS] <섹션 제목>

<해당 구간 핵심 내용>

(섹션마다 반복)

---

## 🔖 태그

#youtube #summary #<날짜>
```

## 완료 후 안내

작업 완료 시 사용자에게 다음을 알립니다:
1. 저장된 파일 경로
2. 자막 언어 (한국어/영어)
3. 종합 요약 미리보기 (2~3줄)
