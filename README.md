# Job Skills Demand Monitor

Track trending skills from job postings and visualize demand over time.
This repo provides a production-minded scaffold: modular sources, NLP-based skills extraction, storage, alerts, and a Streamlit dashboard.

## Features
- Pluggable sources (RSS/company pages/APIs) with retry + polite scraping
- Text cleaning and skill extraction via simple NLP/regex (easily replaceable with spaCy/transformers)
- CSV storage (swap to SQLite/Postgres later)
- Email alerts when a target skill spikes
- Streamlit dashboard for trends

## Quickstart
```bash
# 1) Create and activate a venv (recommended)
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Configure env
cp .env.example .env
# edit .env to set SKILL_LIST and EMAIL settings (optional)

# 4) Run a single collection
python -m src.scraper

# 5) Launch dashboard
streamlit run dashboards/streamlit_app.py
