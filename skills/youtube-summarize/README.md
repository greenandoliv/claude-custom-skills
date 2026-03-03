# youtube-summarize Skill

특정 YouTube 영상의 자막을 추출하고, 시간 순으로 한국어 요약을 생성하여 Obsidian `_Inbox`에 저장합니다.

## 요구사항 (원본 스펙)

1. 특정 유튜브 링크를 입력받습니다.
2. 유튜브의 자막을 추출합니다. (한글자막이 없을 경우 영어자막으로 대체)
3. 추출된 자막을 시간 순으로 한국어로 요약합니다.
4. 요약결과를 obsidian mcp를 사용하여 `_Inbox` 폴더에 `YYYY-MM-DD youtube <채널명> <제목앞10글자>.md` 파일로 저장합니다. (특수문자 제거, 제목은 앞 10글자만 사용)

## 구현

### 파일 구조

```
skills/youtube-summarize/
├── SKILL.md                    # 스킬 정의 (워크플로우 + 트리거)
└── scripts/
    └── fetch_transcript.py     # 자막 추출 Python 스크립트
```

### 자막 추출 전략

IP 차단을 대비한 2단계 fallback 구조를 사용합니다.

```
1차: youtube-transcript-api
        ↓ (IpBlocked / RequestBlocked 예외 시)
2차: yt-dlp (VTT 자막 다운로드 + 파싱)
```

**언어 우선순위**: 한국어 수동 → 한국어 자동생성 → 영어 수동 → 영어 자동생성 → 기타 첫 번째 자막

### 출력 형식

`fetch_transcript.py`는 아래 형식으로 표준 출력합니다:

```
VIDEO_ID: <video_id>
LANGUAGE: ko (manual) | ko (auto-generated) | en (manual) | en (auto-generated)
TOTAL_SEGMENTS: <숫자>
---TRANSCRIPT---
[MM:SS]
<5분 구간의 자막 텍스트>

[MM:SS]
...
---END---
```

### 의존성

| 패키지 | 역할 | 설치 |
|--------|------|------|
| `youtube-transcript-api` | 1차 자막 추출 | `pip install youtube-transcript-api` |
| `yt-dlp` | 2차 fallback | `brew install yt-dlp` |

## 워크플로우 (SKILL.md)

| 단계 | 작업 |
|------|------|
| 0단계 | YouTube URL 확인 (없으면 사용자에게 요청) |
| 1단계 | `fetch_transcript.py` 실행하여 자막 추출 |
| 2단계 | `yt-dlp`로 제목·채널명 가져오기 → 특수문자 제거 → 제목 앞 10글자 단축 |
| 3단계 | 5분 구간별 한국어 요약 생성 + 전체 종합 요약 |
| 4단계 | 오늘 날짜 확인 (`date +%Y-%m-%d`) |
| 5단계 | Obsidian MCP로 `_Inbox/YYYY-MM-DD youtube <채널명> <제목앞10글자>.md` 저장 |

## 사용법

```
/youtube-summarize
"이 영상 요약해줘: https://youtube.com/watch?v=..."
"유튜브 요약"
"youtube 요약 <URL>"
```

## 출력 예시

저장 파일: `_Inbox/2026-03-02 youtube Lex Fridman Podcast AI의 미래 Cha.md`

```markdown
# 📺 YouTube 영상 요약

> 영상: [제목](URL) | 요약일: 2026-03-02 10:30 | 자막 언어: ko (auto-generated)

---

## 🗒️ 종합 요약

영상 전체 내용을 3~5문장으로 요약

---

## ⏱️ 시간 순 요약

### [00:00] 도입부
...

### [05:00] 본론
...
```

## 설치

```bash
mkdir -p ~/.claude/skills/youtube-summarize/scripts
cp skills/youtube-summarize/SKILL.md ~/.claude/skills/youtube-summarize/
cp skills/youtube-summarize/scripts/fetch_transcript.py ~/.claude/skills/youtube-summarize/scripts/
```
