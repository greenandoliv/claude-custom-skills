#!/usr/bin/env python3
"""
Thread CHOI RSS 요약 스크립트
- RSS 피드에서 CHOI(@choi.openai)의 24시간 이내 게시물 수집
- Claude API로 요약
- Obsidian _Inbox에 마크다운 파일로 저장
"""

import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path

# .env 파일 로드 (스크립트와 같은 디렉토리)
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

RSS_URL = "https://rss.app/feeds/M4NpVSm323yf8bmE.xml"
OBSIDIAN_INBOX = "/Users/sunhee/workspace/obsidian/secondbrain/_Inbox"


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text_parts.append(text)

    def get_text(self):
        return "\n".join(self.text_parts)


def strip_html(html_content):
    parser = HTMLTextExtractor()
    parser.feed(html_content)
    return parser.get_text()


def fetch_rss():
    req = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; RSS reader)"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_rss_items(xml_content, hours=24):
    root = ET.fromstring(xml_content)
    channel = root.find("channel")
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    items = []
    for item in channel.findall("item"):
        pub_date_str = item.findtext("pubDate", "")
        try:
            pub_date = parsedate_to_datetime(pub_date_str)
        except Exception:
            continue

        if pub_date < cutoff:
            continue

        title = item.findtext("title", "").strip()
        description = item.findtext("description", "")
        link = item.findtext("link", "")

        text = strip_html(description)
        if not text:
            text = title

        items.append({
            "pub_date": pub_date,
            "title": title,
            "text": text,
            "link": link,
        })

    # 오래된 순으로 정렬
    items.sort(key=lambda x: x["pub_date"])
    return items


def summarize_with_openai(posts):
    from openai import OpenAI

    client = OpenAI()

    posts_text = ""
    for i, post in enumerate(posts, 1):
        kst = post["pub_date"].astimezone(
            timezone(timedelta(hours=9))
        )
        posts_text += f"\n---\n[{i}] {kst.strftime('%H:%M')} KST\n{post['text']}\n링크: {post['link']}\n"

    prompt = f"""다음은 AI 인플루언서 CHOI(@choi.openai)가 오늘 Threads에 올린 게시물들입니다.

{posts_text}

위 게시물들을 다음 형식으로 정리해 주세요:

1. **오늘의 핵심 키워드** (3-5개, 태그 형식 #키워드)
2. **주요 내용 요약** (게시물별로 핵심만 2-3줄씩)
3. **오늘의 인사이트** (전체 게시물에서 얻을 수 있는 핵심 통찰 3가지)

한국어로 작성하고, Obsidian 마크다운 형식으로 작성해 주세요."""

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def save_to_obsidian(posts, summary):
    today = datetime.now(timezone(timedelta(hours=9)))
    date_str = today.strftime("%Y-%m-%d")
    filename = f"{date_str} Thread CHOI_claude.md"
    filepath = os.path.join(OBSIDIAN_INBOX, filename)

    post_links = "\n".join(
        f"- [{p['pub_date'].astimezone(timezone(timedelta(hours=9))).strftime('%H:%M')}] {p['link']}"
        for p in posts
    )

    content = f"""---
date: {date_str}
source: Threads @choi.openai
tags: [thread, choi, ai, daily-summary]
created: {today.strftime('%Y-%m-%d %H:%M')} KST
---

# Thread CHOI 일일 요약 ({date_str})

> 수집 게시물: {len(posts)}개 (최근 24시간)

## 요약

{summary}

## 원본 링크

{post_links}
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Thread CHOI 요약 시작")

    # OPENAI_API_KEY 확인
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    # RSS 피드 가져오기
    print("RSS 피드 수집 중...")
    xml_content = fetch_rss()

    # 24시간 이내 게시물 필터링
    posts = parse_rss_items(xml_content, hours=24)
    print(f"24시간 이내 게시물: {len(posts)}개")

    if not posts:
        print("24시간 이내 게시물이 없습니다.")
        # 빈 파일 생성 (기록용)
        today = datetime.now(timezone(timedelta(hours=9)))
        date_str = today.strftime("%Y-%m-%d")
        filepath = os.path.join(OBSIDIAN_INBOX, f"{date_str} Thread CHOI_claude.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"---\ndate: {date_str}\n---\n\n# Thread CHOI ({date_str})\n\n오늘 24시간 이내 게시물이 없습니다.\n")
        print(f"파일 생성: {filepath}")
        return

    # Claude로 요약
    print("Claude로 요약 생성 중...")
    summary = summarize_with_openai(posts)

    # Obsidian에 저장
    filepath = save_to_obsidian(posts, summary)
    print(f"저장 완료: {filepath}")


if __name__ == "__main__":
    main()
