from __future__ import annotations
import os, csv
from datetime import datetime, timezone
from typing import List, Dict

def ensure_csv(path: str):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["source","title","company","location","posted_at","url","skills","fetched_at"])

def append_rows(path: str, rows: List[Dict]):
    ensure_csv(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow([
                r.get("source"), r.get("title"), r.get("company"), r.get("location"),
                r.get("posted_at"), r.get("url"), ",".join(r.get("skills", [])),
                datetime.now(timezone.utc).isoformat()
            ])
