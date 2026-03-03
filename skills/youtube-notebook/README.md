# youtube-notebook

지정된 YouTube 채널에서 최근 24시간 이내 업로드된 영상을 수집하고, NotebookLM 노트북을 생성하여 AI 오디오 오버뷰를 만든 후 Obsidian `_Inbox`에 결과를 저장합니다.

## 요구사항

1. 아래 채널에서 24시간 이내에 올라온 영상 링크를 가져옵니다. (scripts 폴더내에 python 파일로 생성해서 skill.md 파일에서 호출하도록 함)

| 채널명 | URL |
|--------|-----|
| Nate Herk | [@nateherk](https://www.youtube.com/@nateherk) |
| Nick Saraev | [@nicksaraev](https://www.youtube.com/@nicksaraev) |
| Jack | [@Itssssss_Jack](https://www.youtube.com/@Itssssss_Jack) |
| Chase (AI) | [@chase-h-ai](https://www.youtube.com/@chase-h-ai) |

2. notebooklm mcp를 사용해서 새로운 노트북을 생성해서 이름을 "YYYY-MM-DD youtube notebook"으로 설정하고, 위에서 가져온 영상링크를 추가합니다.

3. AI 오디오 오버뷰를 생성합니다.

4. 최종 수행한 결과, 추가한 유튜브 링크, 노트북 링크를 포함하여 obsidian mcp를 사용하여 _Inbox 폴더에 "YYYY-MM-DD youtube notebook.md" 파일로 저장합니다.

## 파일 구조

```
youtube-notebook/
├── README.md          # 요구사항 및 구현 문서
├── SKILL.md           # Claude 스킬 정의 (7단계 워크플로우)
└── scripts/
    └── fetch_youtube.py   # YouTube 채널 영상 수집 스크립트
```

## 구현 상세

### scripts/fetch_youtube.py

YouTube Data API 키 없이 **RSS 피드 방식**으로 영상을 수집합니다.

**동작 방식:**
1. 채널 `@handle` URL에서 HTML 파싱으로 `channel_id` 추출 (정규식 3종 시도)
2. `https://www.youtube.com/feeds/videos.xml?channel_id=<ID>` RSS 피드 조회
3. 24시간 이내 업로드된 영상만 필터링
4. `---VIDEO---` 구분자 형식으로 결과 출력

**출력 형식:**
```
---VIDEO---
CHANNEL: Nate Herk
TITLE: 영상 제목
LINK: https://www.youtube.com/watch?v=...
DATE: 2026-03-03 10:30 UTC
```

영상이 없으면 `NO_VIDEOS` 출력 후 스킬 종료.

### SKILL.md 워크플로우 (7단계)

| 단계 | 내용 | 도구 |
|------|------|------|
| 1 | YouTube 영상 수집 | `Bash(python3)` |
| 2 | 오늘 날짜 확인 | `Bash(date)` |
| 3 | NotebookLM 노트북 생성 | `mcp__notebooklm-mcp__notebook_create` |
| 4 | 영상 URL을 소스로 추가 | `mcp__notebooklm-mcp__source_add` |
| 5 | AI 오디오 오버뷰 생성 | `mcp__notebooklm-mcp__studio_create` |
| 6 | 노트북 정보 조회 | `mcp__notebooklm-mcp__notebook_describe` |
| 7 | Obsidian에 결과 저장 | `mcp__mcp-obsidian__obsidian_append_content` |

### Obsidian 출력 템플릿

```markdown
# 📺 YouTube Notebook

> 수집일: YYYY-MM-DD HH:MM | 수집 범위: 최근 24시간 | 영상 수: N개

---

## 🔗 NotebookLM

- **노트북**: [YYYY-MM-DD youtube notebook](<notebook_url>)
- **오디오 오버뷰**: 생성 완료 (NotebookLM에서 재생 가능)

---

## 📋 수집된 영상

| 채널 | 제목 | 링크 | 업로드일 |
|------|------|------|----------|
| 채널명 | 제목 | [보기](link) | YYYY-MM-DD HH:MM UTC |

---

## 🔖 태그

#youtube #notebook #ai-news #날짜
```

저장 경로: `_Inbox/YYYY-MM-DD youtube notebook.md`

## 사용법

```
/youtube-notebook
youtube notebook 만들어줘
유튜브 노트북
영상 수집해줘
```

## 설치

```bash
mkdir -p ~/.claude/skills/youtube-notebook/scripts
cp skills/youtube-notebook/SKILL.md ~/.claude/skills/youtube-notebook/SKILL.md
cp skills/youtube-notebook/scripts/fetch_youtube.py ~/.claude/skills/youtube-notebook/scripts/fetch_youtube.py
```

## 필요 MCP 서버

- **notebooklm-mcp**: NotebookLM 노트북 생성 및 오디오 오버뷰 (`nlm login`으로 인증)
- **mcp-obsidian**: Obsidian vault 저장
