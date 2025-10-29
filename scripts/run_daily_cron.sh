#!/usr/bin/env bash
# Add something like this to your crontab (daily at 9am):
# 0 9 * * * /path/to/repo/scripts/run_daily_cron.sh >> /path/to/repo/cron.log 2>&1
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate || true
python -m src.scraper
