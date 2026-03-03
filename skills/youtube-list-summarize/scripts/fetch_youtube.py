"""
YouTube 채널에서 24시간 이내 업로드된 영상 링크를 가져옵니다.
사용법: python3 fetch_youtube.py
"""
import sys
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

CHANNELS = [
    ("Nate Herk", "https://www.youtube.com/@nateherk"),
    ("Nick Saraev", "https://www.youtube.com/@nicksaraev"),
    ("Jack", "https://www.youtube.com/@Itssssss_Jack"),
    ("Chase (AI)", "https://www.youtube.com/@chase-h-ai"),
]


def get_channel_id(channel_url):
    """채널 @handle URL에서 channel_id를 추출합니다."""
    try:
        req = urllib.request.Request(
            channel_url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        for pattern in [
            r'"channelId":"([UC][^"]{20,})"',
            r'"externalId":"([UC][^"]{20,})"',
            r'channel_id=([UC][^&"]{20,})',
        ]:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"WARN: {channel_url} 채널ID 추출 실패 - {e}", file=sys.stderr)
    return None


def get_videos_from_rss(channel_id, channel_name, cutoff):
    """RSS 피드에서 cutoff 이후 업로드된 영상 목록을 반환합니다."""
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        req = urllib.request.Request(
            rss_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read()

        root = ET.fromstring(xml_data)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "yt": "http://www.youtube.com/xml/schemas/2015",
            "media": "http://search.yahoo.com/mrss/",
        }

        videos = []
        for entry in root.findall("atom:entry", ns):
            published_el = entry.find("atom:published", ns)
            title_el = entry.find("atom:title", ns)
            link_el = entry.find("atom:link", ns)

            if published_el is None or link_el is None:
                continue

            try:
                pub_date = datetime.fromisoformat(published_el.text.replace("Z", "+00:00"))
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
            except Exception:
                continue

            if pub_date >= cutoff:
                title = title_el.text.strip() if title_el is not None and title_el.text else "(제목 없음)"
                link = link_el.get("href", "")
                pub_str = pub_date.strftime("%Y-%m-%d %H:%M UTC")
                videos.append({
                    "channel": channel_name,
                    "title": title,
                    "link": link,
                    "published": pub_str,
                })
        return videos
    except Exception as e:
        print(f"WARN: {channel_name} RSS 수집 실패 - {e}", file=sys.stderr)
        return []


now = datetime.now(timezone.utc)
cutoff = now - timedelta(hours=24)
all_videos = []

for channel_name, channel_url in CHANNELS:
    channel_id = get_channel_id(channel_url)
    if not channel_id:
        print(f"CHANNEL_ERROR: {channel_name} - channel_id를 가져올 수 없습니다.", file=sys.stderr)
        continue
    videos = get_videos_from_rss(channel_id, channel_name, cutoff)
    all_videos.extend(videos)

if not all_videos:
    print("NO_VIDEOS")
else:
    for v in all_videos:
        print("---VIDEO---")
        print(f"CHANNEL: {v['channel']}")
        print(f"TITLE: {v['title']}")
        print(f"LINK: {v['link']}")
        print(f"DATE: {v['published']}")
