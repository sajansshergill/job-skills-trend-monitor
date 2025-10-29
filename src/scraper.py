from __future__ import annotations
from collections import Counter
from typing import List, Dict
from .config import settings
from .skills import extract_skills
from .parsers import normalize_posting
from .storage import append_rows
from .alerts import maybe_alert
from .sources.company_rss import CompanyRSSSource
from .sources.lever import LeverSource
from .sources.greenhouse import GreenhouseSource

def collect() -> List[Dict]:
    rows: List[Dict] = []

    # Enable sources as available:
    sources = []

    # Lever (public postings API)
    if settings.lever_list:
        sources.append(LeverSource(settings.lever_list))

    # Greenhouse (public job board API)
    if settings.greenhouse_list:
        sources.append(GreenhouseSource(settings.greenhouse_list))

    # (Optional) keep RSS if you add real feeds
    # sources.append(CompanyRSSSource())

    if not sources:
        print("No sources configured. Set LEVER_COMPANIES or GREENHOUSE_BOARDS in .env")
        return rows

    for source in sources:
        for raw in source.fetch():
            raw["source"] = getattr(source, "name", "unknown")
            norm = normalize_posting(raw)
            norm["skills"] = extract_skills(norm["text"], whitelist=settings.skills)
            rows.append(norm)
    return rows

def main():
    rows = collect()
    if not rows:
        print("No rows collected; check your sources/config.")
        return

    append_rows(settings.OUTPUT_CSV, rows)
    print(f"Wrote {len(rows)} rows to {settings.OUTPUT_CSV}")

    counts = Counter()
    for r in rows:
        for s in r.get("skills", []):
            counts[s] += 1

    maybe_alert(counts, settings.ALERT_TARGET_SKILL, settings.ALERT_MIN_MENTIONS,
                settings.EMAIL_FROM, settings.EMAIL_TO, settings.EMAIL_APP_PASSWORD)

if __name__ == "__main__":
    main()
