from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    USER_AGENT: str = os.getenv("USER_AGENT", "JobSkillsTrendBot/1.0")
    OUTPUT_CSV: str = os.getenv("OUTPUT_CSV", "data/jobs.csv")
    SKILL_LIST: str = os.getenv("SKILL_LIST", "python, sql, pandas")
    EMAIL_FROM: str | None = os.getenv("EMAIL_FROM")
    EMAIL_TO: str | None = os.getenv("EMAIL_TO")
    EMAIL_APP_PASSWORD: str | None = os.getenv("EMAIL_APP_PASSWORD")
    ALERT_MIN_MENTIONS: int = int(os.getenv("ALERT_MIN_MENTIONS", "10"))
    ALERT_TARGET_SKILL: str = os.getenv("ALERT_TARGET_SKILL", "python")
    LEVER_COMPANIES: str = os.getenv("LEVER_COMPANIES", "")
    GREENHOUSE_BOARDS: str = os.getenv("GREENHOUSE_BOARDS", "")

    @property
    def skills(self) -> list[str]:
        return [s.strip().lower() for s in self.SKILL_LIST.split(",") if s.strip()]

    @property
    def lever_list(self) -> list[str]:
        return [s.strip().lower() for s in self.LEVER_COMPANIES.split(",") if s.strip()]

    @property
    def greenhouse_list(self) -> list[str]:
        return [s.strip().lower() for s in self.GREENHOUSE_BOARDS.split(",") if s.strip()]

settings = Settings()
