from __future__ import annotations
import time
from datetime import datetime, timezone
from typing import Iterable, Dict, Any, List
import requests
from bs4 import BeautifulSoup

from .base import BaseSource

RSS_FEEDS: List[str] = [
    # Replace with real company/job RSS feeds you target.
    "https://stackoverflow.com/jobs/feed",  # example; may change over time
]

HEADERS = {"User-Agent": "JobSkillsTrendBot/1.0 (+contact@example.com)"}

class CompanyRSSSource(BaseSource):
    name = "company_rss"

    def fetch(self) -> Iterable[Dict[str, Any]]:
        for feed_url in RSS_FEEDS:
            try:
                resp = requests.get(feed_url, headers=HEADERS, timeout=20)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "xml")
                for item in soup.find_all("item"):
                    title = (item.title.get_text(strip=True) if item.title else "Untitled")
                    link = (item.link.get_text(strip=True) if item.link else None)
                    pubdate = item.pubDate.get_text(strip=True) if item.pubDate else None
                    desc_html = item.description.get_text() if item.description else ""

                    yield {
                        "title": title,
                        "company": None,
                        "location": None,
                        "posted_at": _to_iso(pubdate),
                        "url": link,
                        "description_html": desc_html,
                        "description_text": BeautifulSoup(desc_html, "html.parser").get_text(" ", strip=True),
                    }
                time.sleep(1.0)  # politeness
            except Exception:
                continue

def _to_iso(datestr: str | None) -> str | None:
    if not datestr:
        return None
    try:
        # Very naive parse; RSS often uses RFC-822
        return datetime.strptime(datestr, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()
