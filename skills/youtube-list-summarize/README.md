# youtube-list-summarize Skill

지정된 YouTube 채널에서 24시간 이내 업로드된 영상을 수집하고, 각 영상의 자막을 **병렬로** 추출하여 한국어로 요약한 후 Obsidian `_Inbox`에 영상별로 저장합니다.

## 요구사항 (원본 스펙)

1. 아래 채널에서 24시간 이내에 올라온 영상 링크를 가져옵니다.

| 채널명 | URL |
|--------|-----|
| Nate Herk | [@nateherk](https://www.youtube.com/@nateherk) |
| Nick Saraev | [@nicksaraev](https://www.youtube.com/@nicksaraev) |
| Jack | [@Itssssss_Jack](https://www.youtube.com/@Itssssss_Jack) |
| Chase (AI) | [@chase-h-ai](https://www.youtube.com/@chase-h-ai) |

2. 각 영상의 자막을 추출합니다. (한국어 우선, 없으면 영어로 대체)
3. 추출된 자막을 시간 순으로 한국어로 요약합니다. (병렬 subagent로 실행)
4. 요약결과를 Obsidian MCP를 사용하여 `_Inbox/YYYY-MM-DD youtube <채널명> <제목앞10글자>.md` 저장

## 파일 구조

```
youtube-list-summarize/
├── README.md
├── SKILL.md                         # 메인 오케스트레이터 (병렬 에이전트 실행)
├── agents/
│   └── youtube-video-summarize.md   # 커스텀 서브에이전트 (재시작 후 사용 가능)
└── scripts/
    ├── fetch_youtube.py              # YouTube RSS 피드 수집 스크립트
    └── fetch_transcript.py           # 자막 추출 스크립트 (dual-fallback)
```

## 구현

### 병렬 처리 아키텍처

`youtube-summarize` 스킬(단일 영상)과 달리, 이 스킬은 여러 영상을 **동시에** 처리합니다.

```
SKILL.md (orchestrator)
  │
  ├── fetch_youtube.py → 24시간 이내 영상 목록 수집
  │
  ├── [병렬 실행] general-purpose 에이전트 × N개
  │     ├── 에이전트 1: 영상 A 자막 추출 + 한국어 요약 → MARKDOWN_CONTENT 반환
  │     ├── 에이전트 2: 영상 B 자막 추출 + 한국어 요약 → MARKDOWN_CONTENT 반환
  │     └── 에이전트 N: 영상 N 자막 추출 + 한국어 요약 → MARKDOWN_CONTENT 반환
  │
  └── 각 에이전트 결과 수집 → mcp__mcp-obsidian__obsidian_append_content로 저장
```

**중요한 설계 결정:**
- 에이전트는 자막 추출 + 요약만 담당하고 `FILEPATH:` / `MARKDOWN_CONTENT:` 형식으로 반환
- Obsidian 저장은 **메인 SKILL**이 처리 (background 에이전트는 MCP 도구 접근 불가)
- `general-purpose` 서브에이전트 사용 (커스텀 에이전트는 Claude Code 재시작 후 인식됨)

### 워크플로우

| 단계 | 작업 | 도구 |
|------|------|------|
| 1 | YouTube RSS 피드에서 영상 수집 | `fetch_youtube.py` |
| 2 | 오늘 날짜 확인 | `date` |
| 3 | 모든 영상에 대해 병렬 에이전트 실행 | `Agent (general-purpose)` |
| 3a | 각 에이전트: 자막 추출 | `fetch_transcript.py` |
| 3b | 각 에이전트: 한국어 시간순 요약 생성 | Claude LLM |
| 3c | 각 에이전트: 마크다운 내용 반환 | — |
| 4 | 에이전트 결과 수집 후 Obsidian 저장 | `mcp__mcp-obsidian__obsidian_append_content` |
| 5 | 완료 안내 | — |

### fetch_youtube.py

YouTube API 키 없이 RSS 피드로 영상 수집:

1. 채널 `@handle` URL의 HTML에서 `channel_id` 추출 (regex 패턴 3가지 시도)
2. `https://www.youtube.com/feeds/videos.xml?channel_id=<id>` RSS XML 파싱
3. 24시간 이내 업로드된 영상만 필터링
4. `---VIDEO---` 구분자로 출력 (CHANNEL, TITLE, LINK, DATE 필드)

### fetch_transcript.py

IP 차단에 강한 dual-fallback 전략:

```
1차: youtube-transcript-api  →  IpBlocked/RequestBlocked 시
2차: yt-dlp (VTT 파일 파싱)
```

**언어 우선순위:** 한국어 수동 → 한국어 자동 → 영어 수동 → 영어 자동

출력: 5분 구간별 `[MM:SS]` 타임스탬프 자막

### Obsidian 출력 형식

```markdown
# 📺 YouTube 영상 요약

> 영상: [제목](URL) | 요약일: YYYY-MM-DD | 채널: 채널명 | 자막 언어: ko

---

## 🗒️ 종합 요약

3~5문장 종합 요약

---

## ⏱️ 시간순 요약

### [00:00] 섹션 제목
핵심 내용

...

---

## 🔖 태그

#youtube #summary #YYYY-MM-DD
```

**파일명:** `_Inbox/YYYY-MM-DD youtube <채널명> <제목앞10글자>.md`

## 사용법

```
"youtube list summarize"
"유튜브 목록 요약"
"채널 영상 요약해줘"
"/youtube-list-summarize"
```

## 설치

```bash
# 의존성 설치
pip install youtube-transcript-api
brew install yt-dlp  # IP 차단 fallback용

# 스킬 배포
mkdir -p ~/.claude/skills/youtube-list-summarize/scripts
cp skills/youtube-list-summarize/SKILL.md ~/.claude/skills/youtube-list-summarize/
cp skills/youtube-list-summarize/scripts/fetch_youtube.py ~/.claude/skills/youtube-list-summarize/scripts/
cp skills/youtube-list-summarize/scripts/fetch_transcript.py ~/.claude/skills/youtube-list-summarize/scripts/

# 커스텀 에이전트 배포 (Claude Code 재시작 후 인식)
cp skills/youtube-list-summarize/agents/youtube-video-summarize.md ~/.claude/agents/
```

## 필수 MCP 서버

| MCP 서버 | 용도 |
|----------|------|
| `mcp__mcp-obsidian` | Obsidian vault 저장 |
