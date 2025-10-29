from __future__ import annotations
from typing import Iterable, Dict, Any, List
import os, time, requests

HEADERS = {"User-Agent": os.getenv("USER_AGENT", "JobSkillsTrendBot/1.0")}

class GreenhouseSource:
    name = "greenhouse"

    def __init__(self, boards: List[str]):
        # boards are Greenhouse board tokens like "airbnb"
        self.boards = [b.strip() for b in boards if b.strip()]

    def fetch(self) -> Iterable[Dict[str, Any]]:
        for token in self.boards:
            url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
            try:
                r = requests.get(url, headers=HEADERS, timeout=30)
                r.raise_for_status()
                data = r.json() or {}
                for job in data.get("jobs", []):
                    title = job.get("title") or "Untitled"
                    url_j = job.get("absolute_url")
                    # Greenhouse puts location as dict with name
                    loc = (job.get("location") or {}).get("name")
                    updated = job.get("updated_at")
                    company = token  # lightweight proxy; you can map tokens -> nice names

                    # Greenhouse job description requires another call for full text; use title+location for skill scan seed
                    yield {
                        "title": title,
                        "company": company,
                        "location": loc,
                        "posted_at": updated,
                        "url": url_j,
                        "description_text": f"{title} @ {loc or ''}",
                    }
                time.sleep(0.5)
            except Exception:
                continue
