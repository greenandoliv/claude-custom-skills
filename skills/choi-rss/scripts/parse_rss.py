"""
RSS 피드를 stdin에서 읽어 24시간 이내 게시물을 파싱하고 출력합니다.
사용법: curl -s <rss_url> | python3 parse_rss.py
"""
import sys
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

data = sys.stdin.read()
root = ET.fromstring(data)
ns = {'atom': 'http://www.w3.org/2005/Atom'}
channel = root.find('channel')
items = channel.findall('item') if channel else root.findall('atom:entry', ns)

now = datetime.now(timezone.utc)
cutoff = now - timedelta(hours=24)
found = []

for item in items:
    # RSS 2.0 형식
    title_el = item.find('title')
    desc_el = item.find('description')
    link_el = item.find('link')
    date_el = item.find('pubDate')

    # Atom 형식 폴백
    if date_el is None:
        date_el = item.find('atom:published', ns)
    if title_el is None:
        title_el = item.find('atom:title', ns)
    if desc_el is None:
        desc_el = item.find('atom:content', ns) or item.find('atom:summary', ns)
    if link_el is None:
        link_rel = item.find('atom:link', ns)
        link_val = link_rel.get('href') if link_rel is not None else ''
    else:
        link_val = link_el.text or ''

    if date_el is None:
        continue

    try:
        pub_date = parsedate_to_datetime(date_el.text)
        if pub_date.tzinfo is None:
            pub_date = pub_date.replace(tzinfo=timezone.utc)
    except Exception:
        try:
            pub_date = datetime.fromisoformat(date_el.text.replace('Z', '+00:00'))
        except Exception:
            continue

    if pub_date >= cutoff:
        title = title_el.text.strip() if title_el is not None and title_el.text else '(제목 없음)'
        content = desc_el.text.strip() if desc_el is not None and desc_el.text else ''
        content = re.sub(r'<[^>]+>', '', content).strip()
        pub_str = pub_date.strftime('%Y-%m-%d %H:%M UTC')
        found.append(True)
        print(f"---ITEM---")
        print(f"DATE: {pub_str}")
        print(f"TITLE: {title}")
        print(f"LINK: {link_val}")
        print(f"CONTENT: {content}")

if not found:
    print("NO_ITEMS")
