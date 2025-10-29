from __future__ import annotations
import re
from typing import Dict, Any

CLEAN_RE = re.compile(r"\s+", re.MULTILINE)

def normalize_posting(raw: Dict[str, Any]) -> Dict[str, Any]:
    title = (raw.get("title") or "").strip()
    company = (raw.get("company") or "") or None
    location = (raw.get("location") or "") or None
    posted_at = raw.get("posted_at")
    url = raw.get("url")
    text = raw.get("description_text") or raw.get("description_html") or ""

    text = CLEAN_RE.sub(" ", text).strip()
    return {
        "source": raw.get("source", "unknown"),
        "title": title,
        "company": company,
        "location": location,
        "posted_at": posted_at,
        "url": url,
        "text": text,
    }
