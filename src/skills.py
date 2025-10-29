from __future__ import annotations
import re
from typing import List, Dict

# Build a simple case-insensitive mapping of skills -> regex
CANONICAL_SKILLS = [
    "python", "sql", "pandas", "spark", "airflow", "databricks",
    "n8n", "puppeteer", "selenium", "aws", "gcp", "azure",
    "tableau", "power bi", "streamlit", "langchain", "llm", "rag",
    "mlflow", "dbt", "kafka"
]

SKILL_PATTERNS: Dict[str, re.Pattern] = {
    s: re.compile(rf"\b{re.escape(s)}\b", re.IGNORECASE) for s in CANONICAL_SKILLS
}

def extract_skills(text: str, whitelist: List[str] | None = None) -> List[str]:
    if not text:
        return []
    targets = whitelist or CANONICAL_SKILLS
    found = []
    for s in targets:
        pat = SKILL_PATTERNS.get(s) or re.compile(rf"\b{re.escape(s)}\b", re.IGNORECASE)
        if pat.search(text):
            found.append(s.lower())
    return sorted(set(found))
