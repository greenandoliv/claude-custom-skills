#!/usr/bin/env python3
"""
YouTube 자막 추출 스크립트
사용법: python3 fetch_transcript.py <YouTube URL>
출력: 시간순 자막 텍스트 (한국어 우선, 없으면 영어)

youtube-transcript-api가 IP 차단될 경우 yt-dlp로 자동 fallback합니다.
"""

import sys
import re
import subprocess
import tempfile
import os


def extract_video_id(url: str) -> str | None:
    """YouTube URL에서 video ID 추출"""
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def format_timestamp(seconds: float) -> str:
    """초를 MM:SS 형식으로 변환"""
    total = int(seconds)
    minutes = total // 60
    secs = total % 60
    return f"{minutes:02d}:{secs:02d}"


def print_transcript(video_id: str, used_lang: str, data) -> None:
    """자막 데이터를 표준 형식으로 출력"""
    print(f"VIDEO_ID: {video_id}")
    print(f"LANGUAGE: {used_lang}")
    print(f"TOTAL_SEGMENTS: {len(data)}")
    print("---TRANSCRIPT---")

    section_interval = 300  # 5분 단위 섹션
    current_section_start = 0
    section_lines = []

    for entry in data:
        start = entry.start if hasattr(entry, "start") else entry.get("start", 0)
        text_raw = entry.text if hasattr(entry, "text") else entry.get("text", "")
        text = text_raw.replace("\n", " ").strip()

        if not text:
            continue

        if start >= current_section_start + section_interval:
            if section_lines:
                print(f"[{format_timestamp(current_section_start)}]")
                print(" ".join(section_lines))
                print()
            current_section_start = (int(start) // section_interval) * section_interval
            section_lines = []

        section_lines.append(text)

    if section_lines:
        print(f"[{format_timestamp(current_section_start)}]")
        print(" ".join(section_lines))

    print("---END---")


def fetch_via_api(video_id: str) -> bool:
    """youtube-transcript-api를 사용하여 자막 추출. 성공 시 True 반환."""
    try:
        from youtube_transcript_api import (
            YouTubeTranscriptApi,
            NoTranscriptFound,
            TranscriptsDisabled,
            IpBlocked,
            RequestBlocked,
        )
    except ImportError:
        return False

    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
    except (IpBlocked, RequestBlocked) as e:
        sys.stderr.write(f"[youtube-transcript-api] IP/요청 차단됨, yt-dlp로 전환: {e}\n")
        return False
    except TranscriptsDisabled:
        print("ERROR: 이 영상은 자막이 비활성화되어 있습니다.")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"[youtube-transcript-api] 오류, yt-dlp로 전환: {e}\n")
        return False

    # 언어 우선순위: 한국어(수동) > 한국어(자동) > 영어(수동) > 영어(자동) > 기타
    transcript = None
    used_lang = None

    for find_method, langs, label in [
        ("find_manually_created_transcript", ["ko"], "ko (manual)"),
        ("find_generated_transcript", ["ko"], "ko (auto-generated)"),
        ("find_manually_created_transcript", ["en"], "en (manual)"),
        ("find_generated_transcript", ["en"], "en (auto-generated)"),
    ]:
        try:
            transcript = getattr(transcript_list, find_method)(langs)
            used_lang = label
            break
        except NoTranscriptFound:
            continue

    if transcript is None:
        available = list(transcript_list)
        if available:
            transcript = available[0]
            used_lang = transcript.language_code
        else:
            print("ERROR: 사용 가능한 자막이 없습니다.")
            sys.exit(1)

    try:
        data = transcript.fetch()
    except (IpBlocked, RequestBlocked) as e:
        sys.stderr.write(f"[youtube-transcript-api] fetch 차단됨, yt-dlp로 전환: {e}\n")
        return False
    except Exception as e:
        print(f"ERROR: 자막 데이터 로딩 실패: {e}")
        sys.exit(1)

    print_transcript(video_id, used_lang, data)
    return True


def parse_vtt_content(vtt_text: str) -> list[dict]:
    """VTT 자막 파일 파싱 → [{start, text}, ...] 반환"""
    entries = []
    lines = vtt_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # 타임스탬프 줄 감지: "00:00:00.000 --> 00:00:05.000"
        if "-->" in line:
            time_match = re.match(r"(\d+):(\d+):(\d+)\.(\d+)\s*-->", line)
            if time_match:
                h, m, s = int(time_match.group(1)), int(time_match.group(2)), int(time_match.group(3))
                start_sec = h * 3600 + m * 60 + s
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip():
                    # VTT 태그 제거 (<c>, </c>, <00:00:01.000> 등)
                    cleaned = re.sub(r"<[^>]+>", "", lines[i]).strip()
                    if cleaned:
                        text_lines.append(cleaned)
                    i += 1
                text = " ".join(text_lines)
                if text:
                    entries.append({"start": start_sec, "text": text})
                continue
        i += 1
    return entries


def fetch_via_ytdlp(video_id: str, url: str) -> bool:
    """yt-dlp를 사용하여 자막 추출. 성공 시 True 반환."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 한국어 자막 시도
        for lang_args, used_lang in [
            (["--sub-lang", "ko", "--write-auto-subs"], "ko (yt-dlp auto)"),
            (["--sub-lang", "ko", "--write-subs"], "ko (yt-dlp manual)"),
            (["--sub-lang", "en", "--write-auto-subs"], "en (yt-dlp auto)"),
            (["--sub-lang", "en", "--write-subs"], "en (yt-dlp manual)"),
        ]:
            cmd = [
                "yt-dlp",
                "--skip-download",
                "--sub-format", "vtt",
                *lang_args,
                "-o", os.path.join(tmpdir, "%(id)s.%(ext)s"),
                url,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            vtt_files = [f for f in os.listdir(tmpdir) if f.endswith(".vtt")]
            if vtt_files:
                vtt_path = os.path.join(tmpdir, vtt_files[0])
                with open(vtt_path, "r", encoding="utf-8") as f:
                    vtt_text = f.read()
                entries = parse_vtt_content(vtt_text)
                # 중복 제거 (연속 동일 텍스트)
                deduped = []
                prev_text = None
                for e in entries:
                    if e["text"] != prev_text:
                        deduped.append(e)
                        prev_text = e["text"]
                if deduped:
                    print_transcript(video_id, used_lang, deduped)
                    return True

    sys.stderr.write("[yt-dlp] 자막을 찾을 수 없습니다.\n")
    return False


def fetch_transcript(url: str) -> None:
    video_id = extract_video_id(url)
    if not video_id:
        print(f"ERROR: YouTube URL에서 video ID를 추출할 수 없습니다: {url}")
        sys.exit(1)

    # 1차 시도: youtube-transcript-api
    if fetch_via_api(video_id):
        return

    # 2차 시도: yt-dlp fallback
    sys.stderr.write("[fallback] yt-dlp로 자막을 가져옵니다...\n")
    if fetch_via_ytdlp(video_id, url):
        return

    print("ERROR: youtube-transcript-api와 yt-dlp 모두 자막을 가져오지 못했습니다.")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 fetch_transcript.py <YouTube URL>")
        sys.exit(1)

    fetch_transcript(sys.argv[1])
