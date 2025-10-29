# Windows Task Scheduler

1. Open Task Scheduler → Create Basic Task
2. Trigger: Daily (choose time)
3. Action: Start a Program
   - Program/script: `python`
   - Add arguments: `-m src.scraper`
   - Start in: `C:\path\to\repo`
4. Finish. Ensure your virtual environment or Python is on PATH.
