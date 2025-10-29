from __future__ import annotations
from typing import Iterable, Dict, Any, List
import os, time
import requests
from bs4 import BeautifulSoup  # only to strip HTML if needed

HEADERS = {"User-Agent": os.getenv("USER_AGENT", "JobSkillsTrendBot/1.0")}

def _ms_to_iso(ms: int | None) -> str | None:
    if not ms:
        return None
    try:
        import datetime
        return datetime.datetime.utcfromtimestamp(ms/1000).replace(tzinfo=datetime.timezone.utc).isoformat()
    except Exception:
        return None

class LeverSource:
    name = "lever"

    def __init__(self, companies: List[str]):
        # companies are Lever account slugs, like "openai"
        self.companies = [c.strip() for c in companies if c.strip()]

    def fetch(self) -> Iterable[Dict[str, Any]]:
        for comp in self.companies:
            url = f"https://api.lever.co/v0/postings/{comp}?mode=json"
            try:
                r = requests.get(url, headers=HEADERS, timeout=30)
                r.raise_for_status()
                for job in r.json():
                    title = job.get("text") or job.get("title") or "Untitled"
                    url_j = job.get("hostedUrl") or job.get("applyUrl") or job.get("url")
                    created = _ms_to_iso(job.get("createdAt"))
                    # Lever often nests location in "categories"
                    cats = job.get("categories") or {}
                    location = (cats.get("location") or "").strip() or None
                    company = comp

                    # Prefer plain text description if present; else sanitize
                    desc = job.get("descriptionPlain") or job.get("description") or ""
                    if "descriptionPlain" not in job and desc:
                        desc = BeautifulSoup(desc, "html.parser").get_text(" ", strip=True)

                    yield {
                        "title": title,
                        "company": company,
                        "location": location,
                        "posted_at": created,
                        "url": url_j,
                        "description_text": desc,
                    }
                time.sleep(0.5)
            except Exception:
                continue
